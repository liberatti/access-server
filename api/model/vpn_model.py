from api.model.base_model import SQLiteDAO
from api.utils import logger


class VPNSessionDao(SQLiteDAO):
    __collection_name__ = "sessions"
    __PK__ = "id"
    __schema__ = [
        f"""CREATE TABLE if not exists {__collection_name__} (
            id varchar(12),
            user_id varchar(12),
            remote_port integer,
            remote_ip varchar(100),
            local_ip varchar(100),
            state varchar(64)
        )
        """,
        f"CREATE UNIQUE INDEX if not exists {__collection_name__}_pk ON {__collection_name__}(id)",
    ]

    def delete_by_user_id(self, user_id):
        query = f"DELETE FROM {self.__collection_name__} WHERE user_id=:user_id"
        filter = {"user_id": user_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
        finally:
            cursor.close()

    def get_by_user_id(self, user_id):
        query = f"SELECT * FROM {self.__collection_name__} WHERE user_id=:user_id and state='activated' limit 1"
        filter = {"user_id": user_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            return self.fetchone(cursor)
        finally:
            cursor.close()
