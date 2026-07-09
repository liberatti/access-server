from nxcore.repository.sqlite3_dao import SQLite3DAO
from api.utils import logger
import config

class VPNSessionDao(SQLite3DAO):
    def __init__(self, auto_commit=True):
        super().__init__(
            db_path=config.DB_PATH,
            table_name="sessions",
            auto_commit=auto_commit
        )

    def create_schema(self):
        self.connect()
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                _id varchar(12),
                user_id varchar(12),
                remote_port integer,
                remote_ip varchar(100),
                local_ip varchar(100),
                state varchar(64)
            )
            """
        )
        self.ddl(f"CREATE UNIQUE INDEX if not exists {self.table_name}_pk ON {self.table_name}(_id)")

    def from_dict(self, vo):
        if vo and "id" in vo:
            vo["_id"] = vo.pop("id")
        return super().from_dict(vo)

    def to_dict(self, row):
        if row and "_id" in row:
            row["id"] = row.pop("_id")
        return row

    def delete_by_user_id(self, user_id):
        sql = f"DELETE FROM {self.table_name} WHERE user_id = ?"
        self._query(sql, (user_id,))
        if self.auto_commit:
            self.commit()

    def get_all_by_user_id(self, user_id):
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ?"
        rs = self._query(sql, (user_id,), fetch=True)
        return [self.to_dict(r) for r in rs] if rs else []

    def get_by_user_id(self, user_id):
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ? and state='activated' limit 1"
        rs = self._query(sql, (user_id,), fetch=True)
        return self.to_dict(rs[0]) if rs else None
