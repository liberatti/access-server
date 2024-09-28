from api.utils import logger
from api.model.base_model import SQLiteDAO
from api.model.policy_model import PolicyDao


class UserDao(SQLiteDAO):
    __collection_name__ = "users"
    __PK__ = "id"
    __schema__ = [
        f"""CREATE TABLE if not exists {__collection_name__} (
            id varchar(12) PRIMARY KEY,
            name varchar(64),
            username varchar(64) UNIQUE,
            password varchar(250),
            role varchar(64)
        )
        """
    ]

    def persist(self, vo):
        policies = None

        if "policies" in vo:
            policies = vo.pop("policies")

        pk = super().persist(vo)

        if policies:
            up_model = UserPolicyDao(connection=self.connection)
            up_model.delete_by_user(pk)
            for p in policies:
                up_model.persist({"user_id": pk, "policy_id": p["id"]})

        return pk

    def update_by_id(self, pk, vo):
        if "policies" in vo:
            ps = vo.pop("policies")
            up_model = UserPolicyDao(connection=self.connection)
            up_model.delete_by_user(pk)
            for p in ps:
                up_model.persist({"user_id": pk, "policy_id": p["id"]})
        return super().update_by_id(pk, vo)

    def fetchone(self, cursor):
        try:
            vo = super().fetchone(cursor)
            up_model = UserPolicyDao()
            if vo:
                vo.update({"policies": up_model.get_by_user_id(vo["id"])})
            return vo
        finally:
            cursor.close()

    def fetchall(self, cursor):
        try:
            rows = super().fetchall(cursor)
            up_model = UserPolicyDao()
            for vo in rows:
                if vo:
                    vo.update({"policies": up_model.get_by_user_id(vo["id"])})
            return rows
        finally:
            cursor.close()

    def get_descr(self, id):
        query = f"SELECT id,name FROM {self.__collection_name__} WHERE id=:id limit 1"
        filter = {"id": id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            return super().fetchone(cursor)
        finally:
            cursor.close()

    def find_by_username(self, username):
        query = (
            f"SELECT * FROM {self.__collection_name__} WHERE username=:username limit 1"
        )
        filter = {"username": username}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            return self.fetchone(cursor)
        finally:
            cursor.close()


class UserPolicyDao(SQLiteDAO):
    __collection_name__ = "user_policies"
    __schema__ = [
        f"""CREATE TABLE if not exists {__collection_name__} (
            user_id varchar(12),
            policy_id varchar(12),
            FOREIGN KEY (policy_id) REFERENCES {PolicyDao.__collection_name__}({PolicyDao.__PK__}),
            FOREIGN KEY (user_id) REFERENCES {UserDao.__collection_name__}({UserDao.__PK__})
        )
        """
    ]

    def get_by_user_id(self, user_id):
        query = f"SELECT * FROM {self.__collection_name__} WHERE user_id=:user_id "
        filter = {"user_id": user_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            rows = self.fetchall(cursor)
            policies = []
            p_model = PolicyDao()
            for r in rows:
                p = p_model.get_by_id(r["policy_id"])
                if p:
                    policies.append(p)
                else:
                    logger.info(f"policy {r['policy_id']} not found")
            return policies
        finally:
            cursor.close()

    def delete_by_user(self, user_id):
        query = f"DELETE FROM {self.__collection_name__} WHERE user_id=:user_id"
        filter = {"user_id": user_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
        finally:
            cursor.close()