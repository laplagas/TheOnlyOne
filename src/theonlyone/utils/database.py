import sqlite3
import os
from datetime import datetime
from theonlyone.utils.logger import logger


class Database:
    def __init__(self, db_path="data/bot.db"):
        self.db_path = db_path
        self._ensure_directory()
        self.conn = None
        self.init_db()

    def _ensure_directory(self):
        """Cria o diretório data/ se não existir"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self):
        """Obtém ou cria conexão com o banco"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_db(self):
        """Inicializa as tabelas do banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabela de avisos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de configurações do servidor
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER,
                welcome_channel_id INTEGER,
                welcome_message TEXT,
                prefix TEXT DEFAULT '$',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de reaction roles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reaction_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                emoji TEXT NOT NULL,
                role_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de tickets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                ticket_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                closed_by INTEGER
            )
        """)

        # Tabela de usuários (para leveling, etc)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                message_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, user_id)
            )
        """)

        conn.commit()
        logger.info("Database initialized successfully")

    # ==================== WARNS ====================
    def add_warn(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> bool:
        """Adiciona um aviso a um usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO warns (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
                """,
                (guild_id, user_id, moderator_id, reason)
            )
            conn.commit()
            logger.info(f"Warn added | Guild: {guild_id} | User: {user_id} | Moderator: {moderator_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding warn: {e}")
            return False

    def get_warns(self, guild_id: int, user_id: int) -> list:
        """Obtém todos os avisos de um usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM warns
                WHERE guild_id = ? AND user_id = ?
                ORDER BY created_at DESC
                """,
                (guild_id, user_id)
            )
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching warns: {e}")
            return []

    def delete_warn(self, warn_id: int) -> bool:
        """Remove um aviso específico"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM warns WHERE id = ?", (warn_id,))
            conn.commit()
            logger.info(f"Warn deleted | ID: {warn_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting warn: {e}")
            return False

    def clear_warns(self, guild_id: int, user_id: int) -> bool:
        """Remove todos os avisos de um usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM warns WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id)
            )
            conn.commit()
            logger.info(f"All warns cleared | Guild: {guild_id} | User: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing warns: {e}")
            return False

    # ==================== GUILD CONFIG ====================
    def set_log_channel(self, guild_id: int, channel_id: int) -> bool:
        """Define o canal de logs do servidor"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO guild_config (guild_id, log_channel_id)
                VALUES (?, ?)
                """,
                (guild_id, channel_id)
            )
            conn.commit()
            logger.info(f"Log channel set | Guild: {guild_id} | Channel: {channel_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting log channel: {e}")
            return False

    def get_log_channel(self, guild_id: int) -> int:
        """Obtém o canal de logs do servidor"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT log_channel_id FROM guild_config WHERE guild_id = ?", (guild_id,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
        except Exception as e:
            logger.error(f"Error getting log channel: {e}")
            return None

    # ==================== REACTION ROLES ====================
    def add_reaction_role(self, guild_id: int, message_id: int, channel_id: int, emoji: str, role_id: int) -> bool:
        """Adiciona uma reação e role associada"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO reaction_roles (guild_id, message_id, channel_id, emoji, role_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (guild_id, message_id, channel_id, emoji, role_id)
            )
            conn.commit()
            logger.info(f"Reaction role added | Guild: {guild_id} | Emoji: {emoji} | Role: {role_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding reaction role: {e}")
            return False

    def get_reaction_roles(self, guild_id: int, message_id: int) -> list:
        """Obtém todas as reaction roles de uma mensagem"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM reaction_roles
                WHERE guild_id = ? AND message_id = ?
                """,
                (guild_id, message_id)
            )
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching reaction roles: {e}")
            return []

    def get_reaction_role_by_emoji(self, guild_id: int, message_id: int, emoji: str) -> int:
        """Obtém o role_id para um emoji específico"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role_id FROM reaction_roles
                WHERE guild_id = ? AND message_id = ? AND emoji = ?
                """,
                (guild_id, message_id, emoji)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting reaction role by emoji: {e}")
            return None

    # ==================== TICKETS ====================
    def create_ticket(self, guild_id: int, ticket_id: int, user_id: int, channel_id: int) -> bool:
        """Cria um ticket"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tickets (guild_id, ticket_id, user_id, channel_id)
                VALUES (?, ?, ?, ?)
                """,
                (guild_id, ticket_id, user_id, channel_id)
            )
            conn.commit()
            logger.info(f"Ticket created | Guild: {guild_id} | Ticket ID: {ticket_id} | User: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return False

    def close_ticket(self, ticket_id: int, closed_by: int) -> bool:
        """Fecha um ticket"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE tickets
                SET status = 'closed', closed_at = CURRENT_TIMESTAMP, closed_by = ?
                WHERE ticket_id = ?
                """,
                (closed_by, ticket_id)
            )
            conn.commit()
            logger.info(f"Ticket closed | Ticket ID: {ticket_id} | Closed by: {closed_by}")
            return True
        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            return False

    def get_ticket(self, ticket_id: int) -> dict:
        """Obtém informações de um ticket"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting ticket: {e}")
            return None

    def get_user_tickets(self, guild_id: int, user_id: int) -> list:
        """Obtém todos os tickets de um usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM tickets
                WHERE guild_id = ? AND user_id = ?
                ORDER BY created_at DESC
                """,
                (guild_id, user_id)
            )
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching user tickets: {e}")
            return []

    # ==================== USERS ====================
    def add_xp(self, guild_id: int, user_id: int, xp: int) -> bool:
        """Adiciona XP a um usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (guild_id, user_id, xp, message_count)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(guild_id, user_id) DO UPDATE SET
                    xp = xp + ?,
                    message_count = message_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (guild_id, user_id, xp, xp)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding XP: {e}")
            return False

    def get_user_stats(self, guild_id: int, user_id: int) -> dict:
        """Obtém estatísticas de um usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT xp, level, message_count FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id)
            )
            result = cursor.fetchone()
            if result:
                return {"xp": result[0], "level": result[1], "message_count": result[2]}
            return {"xp": 0, "level": 1, "message_count": 0}
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {"xp": 0, "level": 1, "message_count": 0}

    def get_leaderboard(self, guild_id: int, limit: int = 10) -> list:
        """Obtém o ranking de usuários"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, xp, level, message_count FROM users
                WHERE guild_id = ?
                ORDER BY xp DESC
                LIMIT ?
                """,
                (guild_id, limit)
            )
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()


# Instância global do banco de dados
db = Database()
