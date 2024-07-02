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

    def persist(self, dict):
        policies = None
        port_mappings = None

        if "policies" in dict:
            policies = dict.pop("policies")

        if "port_mappings" in dict:
            port_mappings = dict.pop("port_mappings")

        pk = super().persist(dict)

        if policies:
            up_model = UserPolicyDao(connection=self.connection)
            up_model.delete_by_user(pk)
            for p in policies:
                up_model.persist({"user_id": pk, "policy_id": p["id"]})

        if port_mappings:
            p_model = PortMappingDao(connection=self.connection)
            for pm in port_mappings:
                logger.info(f"{pm}->{port_mappings}")
                port_map = p_model.get_by_id(pm["id"])
                if "user_id" not in port_map:
                    p_model.update_by_id(pm["id"], {"user_id": pk})

        return pk

    def update_by_id(self, pk, dict):
        if "policies" in dict:
            ps = dict.pop("policies")
            up_model = UserPolicyDao(connection=self.connection)
            up_model.delete_by_user(pk)
            for p in ps:
                up_model.persist({"user_id": pk, "policy_id": p["id"]})

        if "port_mappings" in dict:
            port_mappings = [port["id"] for port in dict.pop("port_mappings")]
            p_model = PortMappingDao(connection=self.connection)
            user_port_mapping = [port["id"] for port in p_model.get_by_user_id(pk)]
            for up in user_port_mapping:
                if up not in port_mappings:
                    p_model.delete_by_id(up)

            for pm in port_mappings:
                port_map = p_model.get_by_id(pm)
                if "user_id" not in port_map:
                    p_model.update_by_id(pm, {"user_id": pk})
        logger.info(dict)
        return super().update_by_id(pk, dict)

    def fetchone(self, cursor):
        try:
            vo = super().fetchone(cursor)
            up_model = UserPolicyDao()
            p_model = PortMappingDao()
            if vo:
                vo.update({"policies": up_model.get_by_user_id(vo["id"])})
                vo.update({"port_mappings": p_model.get_by_user_id(vo["id"])})
            return vo
        finally:
            cursor.close()

    def fetchall(self, cursor):
        try:
            rows = super().fetchall(cursor)
            up_model = UserPolicyDao()
            p_model = PortMappingDao()
            for vo in rows:
                if vo:
                    vo.update({"policies": up_model.get_by_user_id(vo["id"])})
                    vo.update({"port_mappings": p_model.get_by_user_id(vo["id"])})
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


class PortMappingDao(SQLiteDAO):
    __collection_name__ = "user_ports"
    __PK__ = "id"
    __schema__ = [
        f"""CREATE TABLE if not exists {__collection_name__} (
            id varchar(12) PRIMARY KEY,
            user_id varchar(12),
            user_port integer,
            bind_port integer,
            protocol varchar(10),
            type varchar(10),
            FOREIGN KEY (user_id) REFERENCES {UserDao.__collection_name__}({UserDao.__PK__})
        )
        """
    ]

    def is_free(self, bind_port):
        query = f"SELECT * FROM {self.__collection_name__} WHERE bind_port=:bind_port LIMIT 1"
        filter = {"bind_port": bind_port}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            vo = cursor.fetchone()
            if vo is None:
                return True
            else:
                return False
        finally:
            cursor.close()

    def get_by_user_id(self, user_id):
        query = f"SELECT * FROM {self.__collection_name__} WHERE user_id=:user_id "
        filter = {"user_id": user_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            return self.fetchall(cursor)
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
