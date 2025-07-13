"""Database operations for WhatsApp MCP server."""

import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from .config import config
from .models import Message, Chat, Contact, MessageContext

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Database operation error."""
    pass


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.database_path
        
    @contextmanager
    def get_connection(self):
        """Get a database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount


class MessageRepository:
    """Repository for message operations."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
    
    def search_messages(
        self,
        query: Optional[str] = None,
        chat_jid: Optional[str] = None,
        sender_phone_number: Optional[str] = None,
        after: Optional[datetime] = None,
        before: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Message]:
        """Search messages with filters."""
        
        conditions = []
        params = []
        
        if query:
            conditions.append("LOWER(messages.content) LIKE LOWER(?)")
            params.append(f"%{query}%")
        
        if chat_jid:
            conditions.append("messages.chat_jid = ?")
            params.append(chat_jid)
        
        if sender_phone_number:
            conditions.append("messages.sender LIKE ?")
            params.append(f"%{sender_phone_number}%")
        
        if after:
            conditions.append("messages.timestamp >= ?")
            params.append(after.isoformat())
        
        if before:
            conditions.append("messages.timestamp <= ?")
            params.append(before.isoformat())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query_sql = f"""
            SELECT messages.*, chats.name as chat_name
            FROM messages
            LEFT JOIN chats ON messages.chat_jid = chats.jid
            WHERE {where_clause}
            ORDER BY messages.timestamp DESC
            LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        
        rows = self.db.execute_query(query_sql, tuple(params))
        return [self._row_to_message(row) for row in rows]
    
    def get_message_context(
        self,
        message_id: str,
        before: int = 5,
        after: int = 5
    ) -> Optional[MessageContext]:
        """Get context around a specific message."""
        
        # First, get the target message
        target_query = """
            SELECT messages.*, chats.name as chat_name
            FROM messages
            LEFT JOIN chats ON messages.chat_jid = chats.jid
            WHERE messages.id = ?
        """
        
        target_rows = self.db.execute_query(target_query, (message_id,))
        if not target_rows:
            return None
        
        target_message = self._row_to_message(target_rows[0])
        
        # Get messages before
        before_query = """
            SELECT messages.*, chats.name as chat_name
            FROM messages
            LEFT JOIN chats ON messages.chat_jid = chats.jid
            WHERE messages.chat_jid = ? AND messages.timestamp < ?
            ORDER BY messages.timestamp DESC
            LIMIT ?
        """
        
        before_rows = self.db.execute_query(
            before_query,
            (target_message.chat_jid, target_message.timestamp.isoformat(), before)
        )
        before_messages = [self._row_to_message(row) for row in before_rows]
        before_messages.reverse()  # Chronological order
        
        # Get messages after
        after_query = """
            SELECT messages.*, chats.name as chat_name
            FROM messages
            LEFT JOIN chats ON messages.chat_jid = chats.jid
            WHERE messages.chat_jid = ? AND messages.timestamp > ?
            ORDER BY messages.timestamp ASC
            LIMIT ?
        """
        
        after_rows = self.db.execute_query(
            after_query,
            (target_message.chat_jid, target_message.timestamp.isoformat(), after)
        )
        after_messages = [self._row_to_message(row) for row in after_rows]
        
        return MessageContext(
            message=target_message,
            before=before_messages,
            after=after_messages
        )
    
    def _row_to_message(self, row: sqlite3.Row) -> Message:
        """Convert database row to Message object."""
        return Message(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            sender=row['sender'],
            content=row['content'] or '',
            is_from_me=bool(row['is_from_me']),
            chat_jid=row['chat_jid'],
            chat_name=row.get('chat_name'),
            media_type=row.get('media_type')
        )


class ChatRepository:
    """Repository for chat operations."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
    
    def search_chats(
        self,
        query: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "last_active"
    ) -> List[Chat]:
        """Search chats with filters."""
        
        conditions = []
        params = []
        
        if query:
            conditions.append("(chats.name LIKE ? OR chats.jid LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        order_by = "last_message_time DESC" if sort_by == "last_active" else "name ASC"
        
        query_sql = f"""
            SELECT jid, name, last_message_time
            FROM chats
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        
        rows = self.db.execute_query(query_sql, tuple(params))
        return [self._row_to_chat(row) for row in rows]
    
    def get_chat_by_jid(self, jid: str) -> Optional[Chat]:
        """Get chat by JID."""
        query = "SELECT jid, name, last_message_time FROM chats WHERE jid = ?"
        rows = self.db.execute_query(query, (jid,))
        return self._row_to_chat(rows[0]) if rows else None
    
    def _row_to_chat(self, row: sqlite3.Row) -> Chat:
        """Convert database row to Chat object."""
        return Chat(
            jid=row['jid'],
            name=row['name'],
            last_message_time=datetime.fromisoformat(row['last_message_time']) if row['last_message_time'] else None
        )


# Global repository instances
db_manager = DatabaseManager()
message_repo = MessageRepository(db_manager)
chat_repo = ChatRepository(db_manager)