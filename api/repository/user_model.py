from nxcore.repository.sqlite3_dao import SQLite3DAO
from api.utils import logger
import config

class UserDao(SQLite3DAO):
    def __init__(self, connection=None, auto_commit=True):
        super().__init__(
            db_path=config.DB_PATH,
            table_name="users",
            conn=connection,
            auto_commit=auto_commit
        )

    def create_schema(self):
        self.connect()
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                _id varchar(12) PRIMARY KEY,
                name varchar(64),
                username varchar(64) UNIQUE,
                password varchar(250),
                role varchar(64)
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
            up_model = UserPolicyDao(connection=self.conn)
            row.update({"policies": up_model.get_by_user_id(row["id"])})
        return row

    def persist(self, vo):
        policies = None
        if "policies" in vo:
            policies = vo.pop("policies")

        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            from api.utils import gen_random_string
            vo["_id"] = gen_random_string(12)

        super().persist(vo)

        if policies:
            up_model = UserPolicyDao(connection=self.conn)
            up_model.delete_by_user(vo["_id"])
            for p in policies:
                policy_id = p.get("id") or p.get("_id")
                up_model.persist({"user_id": vo["_id"], "policy_id": policy_id})

        return vo["_id"]

    def update_by_id(self, pk, vo):
        if "policies" in vo:
            ps = vo.pop("policies")
            up_model = UserPolicyDao(connection=self.conn)
            up_model.delete_by_user(pk)
            for p in ps:
                policy_id = p.get("id") or p.get("_id")
                up_model.persist({"user_id": pk, "policy_id": policy_id})

        vo = self.from_dict(vo)
        return super().update_by_id(pk, vo)

    def get_descr(self, id):
        sql = f"SELECT _id, name FROM {self.table_name} WHERE _id = ? limit 1"
        rs = self._query(sql, (id,), fetch=True)
        return self.to_dict(rs[0]) if rs else None

    def find_by_username(self, username):
        sql = f"SELECT * FROM {self.table_name} WHERE username = ? limit 1"
        rs = self._query(sql, (username,), fetch=True)
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


class UserPolicyDao(SQLite3DAO):
    def __init__(self, connection=None, auto_commit=True):
        super().__init__(
            db_path=config.DB_PATH,
            table_name="user_policies",
            conn=connection,
            auto_commit=auto_commit
        )

    def create_schema(self):
        self.connect()
        # We define foreign keys targetting _id of users and policy
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                user_id varchar(12),
                policy_id varchar(12),
                FOREIGN KEY (policy_id) REFERENCES policy(_id),
                FOREIGN KEY (user_id) REFERENCES users(_id)
            )
            """
        )

    def get_by_user_id(self, user_id):
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ?"
        rows = self._query(sql, (user_id,), fetch=True)
        policies = []
        if rows:
            from api.repository.policy_model import PolicyDao
            p_model = PolicyDao(connection=self.conn)
            for r in rows:
                p = p_model.get_by_id(r["policy_id"])
                if p:
                    policies.append(p)
                else:
                    logger.info(f"policy {r['policy_id']} not found")
        return policies

    def delete_by_user(self, user_id):
        sql = f"DELETE FROM {self.table_name} WHERE user_id = ?"
        self._query(sql, (user_id,))
        if self.auto_commit:
            self.commit()