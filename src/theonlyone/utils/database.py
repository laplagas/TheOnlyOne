import os
from theonlyone.utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    mysql = None
    Error = Exception
    logger.warning("mysql-connector-python não encontrado; banco de dados desabilitado.")


class Database:
    def __init__(self, host=None, user=None, password=None, database=None):
        self.enabled = True
        if mysql is None:
            self.enabled = False

        self.host = host or os.getenv("DB_HOST", "localhost")
        self.user = user or os.getenv("DB_USER", "root")
        self.password = password or os.getenv("DB_PASSWORD", "")
        self.database = database or os.getenv("DB_NAME", "theonlyone_db")
        self.conn = None

        if self.enabled:
            self.init_db()
        else:
            logger.warning("Database está desabilitado; operações persistentes serão ignoradas.")

    def get_connection(self):
        """Obtém ou cria conexão com MySQL"""
        if not self.enabled:
            logger.warning("Banco de dados está desabilitado; get_connection retornando None.")
            return None

        try:
            if self.conn is None or not self.conn.is_connected():
                self.conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            return self.conn
        except Error as e:
            logger.error(f"Erro ao conectar ao MySQL: {e}")
            self.enabled = False
            return None

    def _disabled(self, default=None):
        logger.warning("Banco de dados desabilitado; operação ignorada.")
        return default

    def init_db(self):
        """Inicializa as tabelas do banco de dados"""
        conn = self.get_connection()
        if conn is None:
            logger.error("Nao foi possivel conectar ao banco")
            return
        
        cursor = conn.cursor()

        # Tabela de avisos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                moderator_id BIGINT NOT NULL,
                reason VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_guild_user (guild_id, user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Tabela de configurações do servidor
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id BIGINT PRIMARY KEY,
                log_channel_id BIGINT,
                welcome_channel_id BIGINT,
                welcome_message TEXT,
                prefix VARCHAR(10) DEFAULT '$',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Tabela de reaction roles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reaction_roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                message_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                emoji VARCHAR(255) NOT NULL,
                role_id BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_guild_msg (guild_id, message_id),
                UNIQUE KEY unique_reaction (message_id, emoji)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Tabela de tickets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                ticket_id INT NOT NULL,
                user_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                status VARCHAR(20) DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP NULL,
                closed_by BIGINT,
                INDEX idx_guild_user (guild_id, user_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Tabela de usuários (para leveling, etc)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                xp INT DEFAULT 0,
                level INT DEFAULT 1,
                message_count INT DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_guild_user (guild_id, user_id),
                INDEX idx_leaderboard (guild_id, xp DESC)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        conn.commit()
        logger.info("Database MySQL initialized successfully")

    # ==================== WARNS ====================
    def add_warn(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> bool:
        """Adiciona um aviso a um usuário"""
        if not self.enabled:
            return self._disabled(False)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(False)

            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO warns (guild_id, user_id, moderator_id, reason)
                VALUES (%s, %s, %s, %s)
                """,
                (guild_id, user_id, moderator_id, reason)
            )
            conn.commit()
            logger.info(f"Warn added | Guild: {guild_id} | User: {user_id} | Moderator: {moderator_id}")
            return True
        except Error as e:
            logger.error(f"Error adding warn: {e}")
            return False

    def get_warns(self, guild_id: int, user_id: int) -> list:
        """Obtém todos os avisos de um usuário"""
        if not self.enabled:
            return self._disabled([])

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled([])

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM warns
                WHERE guild_id = %s AND user_id = %s
                ORDER BY created_at DESC
                """,
                (guild_id, user_id)
            )
            return cursor.fetchall()
        except Error as e:
            logger.error(f"Error fetching warns: {e}")
            return []

    def delete_warn(self, warn_id: int) -> bool:
        """Remove um aviso específico"""
        if not self.enabled:
            return self._disabled(False)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(False)

            cursor = conn.cursor()
            cursor.execute("DELETE FROM warns WHERE id = %s", (warn_id,))
            conn.commit()
            logger.info(f"Warn deleted | ID: {warn_id}")
            return True
        except Error as e:
            logger.error(f"Error deleting warn: {e}")
            return False

    def clear_warns(self, guild_id: int, user_id: int) -> bool:
        """Remove todos os avisos de um usuário"""
        if not self.enabled:
            return self._disabled(False)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(False)

            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM warns WHERE guild_id = %s AND user_id = %s",
                (guild_id, user_id)
            )
            conn.commit()
            logger.info(f"All warns cleared | Guild: {guild_id} | User: {user_id}")
            return True
        except Error as e:
            logger.error(f"Error clearing warns: {e}")
            return False

    # ==================== GUILD CONFIG ====================
    def set_log_channel(self, guild_id: int, channel_id: int) -> bool:
        """Define o canal de logs do servidor"""
        if not self.enabled:
            return self._disabled(False)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(False)

            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO guild_config (guild_id, log_channel_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE log_channel_id = %s
                """,
                (guild_id, channel_id, channel_id)
            )
            conn.commit()
            logger.info(f"Log channel set | Guild: {guild_id} | Channel: {channel_id}")
            return True
        except Error as e:
            logger.error(f"Error setting log channel: {e}")
            return False

    def get_log_channel(self, guild_id: int) -> int:
        """Obtém o canal de logs do servidor"""
        if not self.enabled:
            return self._disabled(None)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(None)

            cursor = conn.cursor()
            cursor.execute("SELECT log_channel_id FROM guild_config WHERE guild_id = %s", (guild_id,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
        except Error as e:
            logger.error(f"Error getting log channel: {e}")
            return None

    # ==================== REACTION ROLES ====================
    def add_reaction_role(self, guild_id: int, message_id: int, channel_id: int, emoji: str, role_id: int) -> bool:
        """Adiciona uma reação e role associada"""
        if not self.enabled:
            return self._disabled(False)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(False)

            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO reaction_roles (guild_id, message_id, channel_id, emoji, role_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (guild_id, message_id, channel_id, emoji, role_id)
            )
            conn.commit()
            logger.info(f"Reaction role added | Guild: {guild_id} | Emoji: {emoji} | Role: {role_id}")
            return True
        except Error as e:
            logger.error(f"Error adding reaction role: {e}")
            return False

    def get_reaction_roles(self, guild_id: int, message_id: int) -> list:
        """Obtém todas as reaction roles de uma mensagem"""
        if not self.enabled:
            return self._disabled([])

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled([])

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM reaction_roles
                WHERE guild_id = %s AND message_id = %s
                """,
                (guild_id, message_id)
            )
            return cursor.fetchall()
        except Error as e:
            logger.error(f"Error fetching reaction roles: {e}")
            return []

    def get_reaction_role_by_emoji(self, guild_id: int, message_id: int, emoji: str) -> int:
        """Obtém o role_id para um emoji específico"""
        if not self.enabled:
            return self._disabled(None)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(None)

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role_id FROM reaction_roles
                WHERE guild_id = %s AND message_id = %s AND emoji = %s
                """,
                (guild_id, message_id, emoji)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            logger.error(f"Error getting reaction role by emoji: {e}")
            return None

    # ==================== TICKETS ====================
    def create_ticket(self, guild_id: int, ticket_id: int, user_id: int, channel_id: int) -> bool:
        """Cria um ticket"""
        if not self.enabled:
            return self._disabled(False)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(False)

            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tickets (guild_id, ticket_id, user_id, channel_id)
                VALUES (%s, %s, %s, %s)
                """,
                (guild_id, ticket_id, user_id, channel_id)
            )
            conn.commit()
            logger.info(f"Ticket created | Guild: {guild_id} | Ticket ID: {ticket_id} | User: {user_id}")
            return True
        except Error as e:
            logger.error(f"Error creating ticket: {e}")
            return False

    def close_ticket(self, ticket_id: int, closed_by: int) -> bool:
        """Fecha um ticket"""
        if not self.enabled:
            return self._disabled(False)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(False)

            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE tickets
                SET status = 'closed', closed_at = CURRENT_TIMESTAMP, closed_by = %s
                WHERE ticket_id = %s
                """,
                (closed_by, ticket_id)
            )
            conn.commit()
            logger.info(f"Ticket closed | Ticket ID: {ticket_id} | Closed by: {closed_by}")
            return True
        except Error as e:
            logger.error(f"Error closing ticket: {e}")
            return False

    def get_ticket(self, ticket_id: int) -> dict:
        """Obtém informações de um ticket"""
        if not self.enabled:
            return self._disabled(None)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(None)

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets WHERE ticket_id = %s", (ticket_id,))
            return cursor.fetchone()
        except Error as e:
            logger.error(f"Error getting ticket: {e}")
            return None

    def get_user_tickets(self, guild_id: int, user_id: int) -> list:
        """Obtém todos os tickets de um usuário"""
        if not self.enabled:
            return self._disabled([])

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled([])

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM tickets
                WHERE guild_id = %s AND user_id = %s
                ORDER BY created_at DESC
                """,
                (guild_id, user_id)
            )
            return cursor.fetchall()
        except Error as e:
            logger.error(f"Error fetching user tickets: {e}")
            return []

    # ==================== USERS ====================
    def add_xp(self, guild_id: int, user_id: int, xp: int) -> bool:
        """Adiciona XP a um usuário"""
        if not self.enabled:
            return self._disabled(False)

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled(False)

            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (guild_id, user_id, xp, message_count)
                VALUES (%s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE
                    xp = xp + VALUES(xp),
                    message_count = message_count + 1
                """,
                (guild_id, user_id, xp)
            )
            conn.commit()
            return True
        except Error as e:
            logger.error(f"Error adding XP: {e}")
            return False

    def get_user_stats(self, guild_id: int, user_id: int) -> dict:
        """Obtém estatísticas de um usuário"""
        if not self.enabled:
            return self._disabled({"xp": 0, "level": 1, "message_count": 0})

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled({"xp": 0, "level": 1, "message_count": 0})

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT xp, level, message_count FROM users
                WHERE guild_id = %s AND user_id = %s
                """,
                (guild_id, user_id)
            )
            result = cursor.fetchone()
            if result:
                return {"xp": result[0], "level": result[1], "message_count": result[2]}
            return {"xp": 0, "level": 1, "message_count": 0}
        except Error as e:
            logger.error(f"Error getting user stats: {e}")
            return {"xp": 0, "level": 1, "message_count": 0}

    def get_leaderboard(self, guild_id: int, limit: int = 10) -> list:
        """Obtém o ranking de usuários"""
        if not self.enabled:
            return self._disabled([])

        try:
            conn = self.get_connection()
            if conn is None:
                return self._disabled([])

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, xp, level, message_count FROM users
                WHERE guild_id = %s
                ORDER BY xp DESC
                LIMIT %s
                """,
                (guild_id, limit)
            )
            return cursor.fetchall()
        except Error as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if not self.enabled:
            return
        if self.conn:
            self.conn.close()


# Instância global do banco de dados
db = Database()
