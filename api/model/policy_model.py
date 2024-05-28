from flask import json
from api.utils import logger
from api.tools.base_model import BaseModel


class PolicyModel(BaseModel):
    __table__ = "policy"
    __PK__ = "id"
    __schema__ = [
        f"""CREATE TABLE if not exists {__table__} (
            id varchar(12) PRIMARY KEY,
            name varchar(64),
            type varchar(64),
            networks_json longtext
        )
        """
    ]

    def persist(self, dict):
        if "networks" in dict:
            dict.update({"networks_json": json.dumps(dict.pop("networks"))})

        if "clients" in dict:
            targets = dict.pop("clients")
            policy_id = super().persist(dict)
            p_model = PolicyClientModel(self.connection)
            p_model.delete_by_policy(policy_id)
            for t in targets:
                p_model.persist({"policy_id": policy_id, "user_id": t["id"]})
            return policy_id
        else:
            return super().persist(dict)

    def update_by_id(self, pk, dict):
        if "networks" in dict:
            dict.update({"networks_json": json.dumps(dict.pop("networks"))})
        if "clients" in dict:
            clients = dict.pop('clients')
            p_model = PolicyClientModel(self.connection)
            p_model.delete_by_policy(dict["id"])
            for t in clients:
                p_model.persist({"policy_id": dict["id"], "user_id": t["id"]})
        return super().update_by_id(pk, dict)

    def fetchone(self, cursor, eager=True):
        try:
            vo = super().fetchone(cursor, eager)
            if vo:
                p_model = PolicyClientModel(self.connection)
                vo.update({"networks": json.loads(vo.pop("networks_json"))})
                vo.update({"clients": p_model.get_by_policy(vo["id"])})
            return vo
        finally:
            cursor.close()

    def fetchall(self, cursor, eager=False):
        try:
            rows = super().fetchall(cursor, eager)
            p_model = PolicyClientModel(self.connection)
            for vo in rows:
                if vo:
                    vo.update({"networks": json.loads(vo.pop("networks_json"))})
                    vo.update({"clients": p_model.get_by_policy(vo["id"])})
            return rows
        finally:
            cursor.close()


class PolicyClientModel(BaseModel):
    __table__ = "policy_clients"
    __schema__ = [
        f"""CREATE TABLE if not exists {__table__} (
            policy_id varchar(12),
            user_id varchar(12),
            FOREIGN KEY (policy_id) REFERENCES {PolicyModel.__table__}({PolicyModel.__PK__}),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """,
        f"CREATE INDEX if not exists {__table__}_pk ON {__table__}(policy_id)"
    ]

    def delete_by_policy(self, policy_id):
        query = f"DELETE FROM {self.__table__} WHERE policy_id=:policy_id"
        filter = {"policy_id": policy_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
        finally:
            cursor.close()

    def get_by_policy(self, policy_id):
        query = f"SELECT * FROM {self.__table__} WHERE policy_id=:policy_id"
        filter = {"policy_id": policy_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            rows = self.fetchall(cursor, False)
            targets = []
            for r in rows:
                targets.append({"id": r["user_id"]})
            return targets
        finally:
            cursor.close()

    def get_by_client(self, user_id):
        query = f"SELECT * FROM {self.__table__} WHERE user_id=:user_id"
        filter = {"user_id": user_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            rows = self.fetchall(cursor, False)
            targets = []
            for r in rows:
                targets.append({"id": r["policy_id"]})
            return targets
        finally:
            cursor.close()
