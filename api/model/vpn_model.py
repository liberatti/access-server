from api.tools.base_model import BaseModel
from api.utils import logger


class VPNSessionModel(BaseModel):
    __table__ = "sessions"
    __PK__ = "id"
    __schema__ = [
        f"""CREATE TABLE if not exists {__table__} (
            id varchar(12),
            user_id varchar(12),
            remote_port integer,
            remote_ip varchar(100),
            local_ip varchar(100),
            state varchar(64)
        )
        """,
        f"CREATE UNIQUE INDEX if not exists {__table__}_pk ON {__table__}(id)",
    ]

    def delete_by_user_id(self, user_id):
        query = f"DELETE FROM {self.__table__} WHERE user_id=:user_id"
        filter = {"user_id": user_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
        finally:
            cursor.close()

    def get_by_user_id(self, user_id):
        query = f"SELECT * FROM {self.__table__} WHERE user_id=:user_id and state='activated' limit 1"
        filter = {"user_id": user_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            return self.fetchone(cursor, True)
        finally:
            cursor.close()
