class PostgresUserRepository(UserRepository):
    def __init__(self):
        super().__init__()
        self.connection_params = {
            'host': config.db_host,
            'port': config.db_port,
            'database': config.db_name,
            'user': config.db_user,
            'password': config.db_password
        }
        self.conn = psycopg2.connect(**self.connection_params)
        self.create_tables()

    def create_table(self):
        with self.conn.cursor as cur:
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        registered_at TIMESTAMP DEFAULT NOW()
                    )
                """)
            self.conn.commit()

    def save(self, user: User):
        

    def find_by_id(self, id: int) -> User | None:
        pass

    def delete(self, id: int):
        pass
