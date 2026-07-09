from nxcore.repository.sqlite3_dao import SQLite3DAO
from api.utils import logger
import config

class DMZServiceDao(SQLite3DAO):
    def __init__(self, connection=None, auto_commit=True):
        super().__init__(
            db_path=config.DB_PATH,
            table_name="dmz",
            conn=connection,
            auto_commit=auto_commit
        )

    def create_schema(self):
        self.connect()
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                _id varchar(12) PRIMARY KEY,
                name varchar(64),
                description varchar(200)
            )
            """
        )

    def from_dict(self, vo):
        if vo and "id" in vo:
            vo["_id"] = vo.pop("id")
        return super().from_dict(vo)

    def to_dict(self, row):
        if row:
            if "_id" in row:
                row["id"] = row.pop("_id")
            p_model = PortMappingDao(connection=self.conn)
            row.update({"port_mappings": p_model.get_by_dmz_id(row["id"])})
        return row

    def persist(self, vo):
        port_mappings = None
        if "port_mappings" in vo:
            port_mappings = vo.pop("port_mappings")

        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            from api.utils import gen_random_string
            vo["_id"] = gen_random_string(12)

        super().persist(vo)

        if port_mappings:
            p_model = PortMappingDao(connection=self.conn)
            for pm in port_mappings:
                pm.update({"dmz_id": vo["_id"]})
                p_model.persist(pm)

        return vo["_id"]

    def update_by_id(self, pk, vo):
        if "port_mappings" in vo:
            port_mappings = vo.pop("port_mappings")
            p_model = PortMappingDao(connection=self.conn)
            p_model.delete_by_dmz(pk)
            for pm in port_mappings:
                pm.update({"dmz_id": pk})
                p_model.persist(pm)

        vo = self.from_dict(vo)
        return super().update_by_id(pk, vo)

    def get_descr(self, id):
        sql = f"SELECT _id, name FROM {self.table_name} WHERE _id = ? limit 1"
        rs = self._query(sql, (id,), fetch=True)
        return self.to_dict(rs[0]) if rs else None

    def query_all(self, page=None, per_page=None):
        from math import ceil
        pagination = None
        if page and per_page:
            pagination = {"page": page, "per_page": per_page}
        result = self.get_all(pagination=pagination)
        metadata = result["metadata"]
        total_elements = metadata.get("total_elements", 0)
        p_size = metadata.get("per_page", total_elements) or 1
        metadata["total_pages"] = ceil(total_elements / p_size) if p_size > 0 else 0
        return result


class PortMappingDao(SQLite3DAO):
    def __init__(self, connection=None, auto_commit=True):
        super().__init__(
            db_path=config.DB_PATH,
            table_name="user_ports",
            conn=connection,
            auto_commit=auto_commit
        )

    def create_schema(self):
        self.connect()
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                _id varchar(12) PRIMARY KEY,
                user_id varchar(12),
                dmz_id varchar(12),
                user_port integer,
                bind_port integer,
                protocol varchar(10),
                FOREIGN KEY (user_id) REFERENCES dmz(_id)
            )
            """
        )

    def from_dict(self, vo):
        if vo and "id" in vo:
            vo["_id"] = vo.pop("id")
        return super().from_dict(vo)

    def to_dict(self, row):
        if row:
            if "_id" in row:
                row["id"] = row.pop("_id")
            from api.repository.user_model import UserDao
            dao = UserDao(connection=self.conn)
            row.update({"user": dao.get_descr(row["user_id"])})
        return row

    def persist(self, vo):
        user = vo.pop("user")
        user_id = user.get("id") or user.get("_id")
        vo.update({"user_id": user_id})

        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            from api.utils import gen_random_string
            vo["_id"] = gen_random_string(12)

        super().persist(vo)
        return vo["_id"]

    def is_free(self, bind_port):
        sql = f"SELECT * FROM {self.table_name} WHERE bind_port = ? LIMIT 1"
        rs = self._query(sql, (bind_port,), fetch=True)
        return len(rs) == 0

    def get_by_user_id(self, user_id):
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ?"
        rs = self._query(sql, (user_id,), fetch=True)
        return [self.to_dict(r) for r in rs] if rs else []

    def delete_by_user(self, user_id):
        sql = f"DELETE FROM {self.table_name} WHERE user_id = ?"
        self._query(sql, (user_id,))
        if self.auto_commit:
            self.commit()

    def get_by_dmz_id(self, dmz_id):
        sql = f"SELECT * FROM {self.table_name} WHERE dmz_id = ?"
        rs = self._query(sql, (dmz_id,), fetch=True)
        return [self.to_dict(r) for r in rs] if rs else []

    def delete_by_dmz(self, dmz_id):
        sql = f"DELETE FROM {self.table_name} WHERE dmz_id = ?"
        self._query(sql, (dmz_id,))
        if self.auto_commit:
            self.commit()