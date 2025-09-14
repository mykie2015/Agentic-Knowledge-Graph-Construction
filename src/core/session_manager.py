"""
Session management for the Agentic Knowledge Graph Construction system.
Handles agent sessions, state persistence, and workflow coordination.
"""

import asyncio
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

from utils.logging_config import get_system_logger
from utils.config_manager import get_config


class Session:
    """Represents an agent session with state and metadata."""
    
    def __init__(self, session_id: str, user_id: str, session_type: str = "default"):
        """
        Initialize a session.
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            session_type: Type of session (interactive, batch, etc.)
        """
        self.session_id = session_id
        self.user_id = user_id
        self.session_type = session_type
        self.created_at = datetime.utcnow()
        self.last_activity = self.created_at
        self.state = {}
        self.metadata = {}
        self.is_active = True
        
        # Agent tracking
        self.active_agents = set()
        self.agent_history = []
        
        # Task tracking
        self.current_task = None
        self.completed_tasks = []
        
        # Workflow state
        self.workflow_step = "initialization"
        self.workflow_data = {}
    
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def add_agent(self, agent_name: str):
        """Add an agent to the session."""
        self.active_agents.add(agent_name)
        self.agent_history.append({
            "agent": agent_name,
            "action": "added",
            "timestamp": datetime.utcnow().isoformat()
        })
        self.update_activity()
    
    def remove_agent(self, agent_name: str):
        """Remove an agent from the session."""
        self.active_agents.discard(agent_name)
        self.agent_history.append({
            "agent": agent_name,
            "action": "removed",
            "timestamp": datetime.utcnow().isoformat()
        })
        self.update_activity()
    
    def set_state(self, key: str, value: Any):
        """Set a state value."""
        self.state[key] = value
        self.update_activity()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self.state.get(key, default)
    
    def clear_state(self):
        """Clear all session state."""
        self.state.clear()
        self.update_activity()
    
    def start_task(self, task_id: str, task_data: Dict[str, Any]):
        """Start a new task in the session."""
        self.current_task = {
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat(),
            "data": task_data,
            "status": "in_progress"
        }
        self.update_activity()
    
    def complete_task(self, result: Dict[str, Any]):
        """Complete the current task."""
        if self.current_task:
            self.current_task["completed_at"] = datetime.utcnow().isoformat()
            self.current_task["status"] = "completed"
            self.current_task["result"] = result
            
            self.completed_tasks.append(self.current_task)
            self.current_task = None
            self.update_activity()
    
    def fail_task(self, error: str):
        """Mark the current task as failed."""
        if self.current_task:
            self.current_task["completed_at"] = datetime.utcnow().isoformat()
            self.current_task["status"] = "failed"
            self.current_task["error"] = error
            
            self.completed_tasks.append(self.current_task)
            self.current_task = None
            self.update_activity()
    
    def set_workflow_step(self, step: str, data: Dict[str, Any] = None):
        """Set the current workflow step."""
        self.workflow_step = step
        if data:
            self.workflow_data.update(data)
        self.update_activity()
    
    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if the session has expired."""
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - self.last_activity > timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_type": self.session_type,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "state": self.state,
            "metadata": self.metadata,
            "is_active": self.is_active,
            "active_agents": list(self.active_agents),
            "agent_history": self.agent_history,
            "current_task": self.current_task,
            "completed_tasks": self.completed_tasks,
            "workflow_step": self.workflow_step,
            "workflow_data": self.workflow_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create session from dictionary."""
        session = cls(
            data["session_id"],
            data["user_id"],
            data.get("session_type", "default")
        )
        
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_activity = datetime.fromisoformat(data["last_activity"])
        session.state = data.get("state", {})
        session.metadata = data.get("metadata", {})
        session.is_active = data.get("is_active", True)
        session.active_agents = set(data.get("active_agents", []))
        session.agent_history = data.get("agent_history", [])
        session.current_task = data.get("current_task")
        session.completed_tasks = data.get("completed_tasks", [])
        session.workflow_step = data.get("workflow_step", "initialization")
        session.workflow_data = data.get("workflow_data", {})
        
        return session


class SessionManager:
    """Manages agent sessions and their lifecycle."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize session manager.
        
        Args:
            storage_dir: Directory for session persistence
        """
        self.logger = get_system_logger('session_manager')
        self.config = get_config()
        
        # Session storage
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            output_dir = self.config.get('data.output_dir', './data/output')
            self.storage_dir = Path(output_dir) / 'sessions'
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Active sessions
        self.sessions: Dict[str, Session] = {}
        
        # Configuration
        self.session_timeout = self.config.get('system.session_timeout', 3600)  # seconds
        
        # Load existing sessions
        self._load_sessions()
        
        self.logger.info(f"Session manager initialized with storage: {self.storage_dir}")
    
    async def create_session(self, user_id: str, session_type: str = "default") -> str:
        """
        Create a new session.
        
        Args:
            user_id: User identifier
            session_type: Type of session
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session = Session(session_id, user_id, session_type)
        
        self.sessions[session_id] = session
        await self._persist_session(session)
        
        self.logger.info(f"Created session {session_id} for user {user_id} (type: {session_type})")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object or None if not found
        """
        session = self.sessions.get(session_id)
        
        if session:
            # Check if session expired
            if session.is_expired(self.session_timeout // 60):
                await self.close_session(session_id)
                return None
            
            session.update_activity()
            await self._persist_session(session)
        
        return session
    
    async def close_session(self, session_id: str):
        """
        Close and clean up a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.is_active = False
            
            await self._persist_session(session)
            del self.sessions[session_id]
            
            self.logger.info(f"Closed session {session_id}")
    
    async def list_sessions(self, user_id: Optional[str] = None, active_only: bool = True) -> List[Session]:
        """
        List sessions, optionally filtered by user.
        
        Args:
            user_id: Filter by user ID
            active_only: Only return active sessions
            
        Returns:
            List of sessions
        """
        sessions = []
        
        for session in self.sessions.values():
            if user_id and session.user_id != user_id:
                continue
            if active_only and not session.is_active:
                continue
            
            sessions.append(session)
        
        return sessions
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.is_expired(self.session_timeout // 60):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.close_session(session_id)
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def _persist_session(self, session: Session):
        """Persist session to storage."""
        try:
            session_file = self.storage_dir / f"{session.session_id}.json"
            
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to persist session {session.session_id}: {e}")
    
    def _load_sessions(self):
        """Load sessions from storage."""
        try:
            for session_file in self.storage_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    session = Session.from_dict(session_data)
                    
                    # Only load active sessions
                    if session.is_active and not session.is_expired(self.session_timeout // 60):
                        self.sessions[session.session_id] = session
                    else:
                        # Remove expired session file
                        session_file.unlink()
                        
                except Exception as e:
                    self.logger.warning(f"Failed to load session from {session_file}: {e}")
                    
            self.logger.info(f"Loaded {len(self.sessions)} active sessions")
            
        except Exception as e:
            self.logger.error(f"Failed to load sessions: {e}")
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        active_sessions = len(self.sessions)
        total_tasks = sum(len(s.completed_tasks) for s in self.sessions.values())
        active_tasks = sum(1 for s in self.sessions.values() if s.current_task)
        
        session_types = {}
        for session in self.sessions.values():
            session_types[session.session_type] = session_types.get(session.session_type, 0) + 1
        
        return {
            "active_sessions": active_sessions,
            "total_completed_tasks": total_tasks,
            "active_tasks": active_tasks,
            "session_types": session_types,
            "storage_directory": str(self.storage_dir)
        }
