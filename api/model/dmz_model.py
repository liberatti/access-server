from api.utils import logger
from api.model.base_model import SQLiteDAO
from api.model.user_model import UserDao

class DMZServiceDao(SQLiteDAO):
    __collection_name__ = "dmz"
    __PK__ = "id"
    __schema__ = [
        f"""CREATE TABLE if not exists {__collection_name__} (
            id varchar(12) PRIMARY KEY,
            name varchar(64),
            description varchar(200)
        )
        """
    ]

    def persist(self, vo):
        port_mappings=None
        if "port_mappings" in vo:
            port_mappings = vo.pop("port_mappings")
            
        pk = super().persist(vo)
        
        if port_mappings:
            p_model = PortMappingDao(connection=self.connection)
            for pm in port_mappings:
                pm.update({"dmz_id":pk})
                p_model.persist(pm)
                
        return pk

    def update_by_id(self, pk, vo):
        if "port_mappings" in vo:
            port_mappings = vo.pop("port_mappings")
            p_model = PortMappingDao(connection=self.connection)
            p_model.delete_by_dmz(pk)
            for pm in port_mappings:
                pm.update({"dmz_id":pk})
                p_model.persist(pm)
                
        return super().update_by_id(pk, vo)

    def fetchone(self, cursor):
        try:
            vo = super().fetchone(cursor)
            p_model = PortMappingDao()
            if vo:
                vo.update({"port_mappings": p_model.get_by_dmz_id(vo["id"])})
            return vo
        finally:
            cursor.close()

    def fetchall(self, cursor):
        try:
            rows = super().fetchall(cursor)
            p_model = PortMappingDao()
            for vo in rows:
                if vo:
                    vo.update({"port_mappings": p_model.get_by_dmz_id(vo["id"])})
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

class PortMappingDao(SQLiteDAO):
    __collection_name__ = "user_ports"
    __PK__ = "id"
    __schema__ = [
        f"""CREATE TABLE if not exists {__collection_name__} (
            id varchar(12) PRIMARY KEY,
            user_id varchar(12),
            dmz_id varchar(12),
            user_port integer,
            bind_port integer,
            protocol varchar(10),
            FOREIGN KEY (user_id) REFERENCES {DMZServiceDao.__collection_name__}({DMZServiceDao.__PK__})
        )
        """
    ]


    def fetchone(self, cursor):
        try:
            vo = super().fetchone(cursor)
            dao = UserDao()
            if vo:
                vo.update({"user": dao.get_descr(vo["user_id"])})
            return vo
        finally:
            cursor.close()

    def fetchall(self, cursor):
        try:
            rows = super().fetchall(cursor)
            dao = UserDao()
            for vo in rows:
                if vo:
                    vo.update({"user": dao.get_descr(vo["user_id"])})
            return rows
        finally:
            cursor.close()
            

    def persist(self, vo):
        user = vo.pop("user")
        vo.update({"user_id":user['id']})
        return super().persist(vo)

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

    def get_by_dmz_id(self, dmz_id):
        query = f"SELECT * FROM {self.__collection_name__} WHERE dmz_id=:dmz_id "
        filter = {"dmz_id": dmz_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            return self.fetchall(cursor)
        finally:
            cursor.close()
            
    def delete_by_dmz(self, dmz_id):
        query = f"DELETE FROM {self.__collection_name__} WHERE dmz_id=:dmz_id"
        filter = {"dmz_id": dmz_id}
        logger.debug(f"{query} : {str(filter)}")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
        finally:
            cursor.close()
            