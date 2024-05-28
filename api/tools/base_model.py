from datetime import datetime
from math import ceil
import sqlite3
from datetime import datetime
from api.utils import logger,gen_random_string

class BaseModel:
    __connection = None

    def config_connection(self):
        try:
            cursor = self.connection.cursor()
            #cursor.execute("PRAGMA cache_size = 10000")
            #cursor.execute("PRAGMA journal_mode = WAL")
            #cursor.execute("PRAGMA read_uncommitted = true")
        finally:
            cursor.close()

    def __init__(self, connection=None):
        if connection is None:
            logger.debug(f"Create Session {type(self)}")
            self.__connection = sqlite3.connect(f"data/admin.db", timeout=60)
            self.config_connection()
        else:
            logger.debug(f"Reuse Session {type(self)}")
            self.__connection = connection

    # def __del__(self):
    #    if self.__connection:
    #        self.__connection.close()

    @property
    def connection(self):
        return self.__connection

    def _create_dict(self, cols, row):
        data_dict = {}
        for col, value in zip(cols, row):
            if value is not None:
                if isinstance(value, str):
                    try:
                        data_dict[col] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S%z")
                    except ValueError:
                        logger.debug(f"{type(value)}:{value} of {col}")
                        data_dict[col] = value
                else:
                    data_dict[col] = value
        return data_dict

    def fetchall(self, cursor, eager):
        rows = cursor.fetchall()
        cols = [column[0] for column in cursor.description]
        return [self._create_dict(cols, row) for row in rows]

    def fetchone(self, cursor, eager):
        row = cursor.fetchone()
        cols = [column[0] for column in cursor.description]
        if row:
            return self._create_dict(cols, row)
        else:
            return None

    def close(self):
        self.__connection.rollback()
        self.__connection.close()

    def create_schema(self):
        try:
            cursor = self.__connection.cursor()
            for sql in self.__schema__:
                logger.debug(f"{sql}")
                cursor.execute(sql)
        finally:
            cursor.close()

    def commit(self):
        self.__connection.commit()

    def delete_all(self):
        query = f"DELETE FROM {self.__table__}"
        logger.debug(f"{query} : ")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar todos os registros: {e}")
            self.connection.rollback()  # Desfazer alterações em caso de erro
            return False
        finally:
            cursor.close()

    def delete_by_filter(self, filter):
        where = " AND ".join(f":{key} = :{key}" for key in filter.keys())
        query = f"DELETE FROM {self.__table__} WHERE {where}"
        logger.debug(f"{query} : {str(filter)}")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, filter)
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar todos os registros: {e}")
            self.connection.rollback()  # Desfazer alterações em caso de erro
            return False
        finally:
            cursor.close()

    def delete_by_id(self, pk):
        query = f"DELETE FROM {self.__table__} WHERE {self.__PK__}=:id"
        filter = {"id": pk}
        logger.debug(f"{query} : {str(filter)}")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, filter)
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar todos os registros: {e}")
            self.connection.rollback()  # Desfazer alterações em caso de erro
            return False
        finally:
            cursor.close()

    def gen_id(self):
        return gen_random_string(12)

    def persist(self, dict):
        pk_attr = getattr(self, "__PK__", False)
        if pk_attr:
            if pk_attr not in dict or len(dict[pk_attr]) <= 0:
                dict.update({self.__PK__: self.gen_id()})

        columns = ", ".join(dict.keys())
        vals = ", ".join(f":{key}" for key in dict.keys())
        query = f"INSERT INTO {self.__table__} ({columns}) VALUES ({vals})"
        logger.debug(f"{query} : {str(dict)}")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, dict)
            if getattr(self, "__PK__", False):
                return dict[self.__PK__]
        finally:
            cursor.close()

    def get_by_id(self, id):
        query = f"SELECT * FROM {self.__table__} WHERE {self.__PK__}=:id LIMIT 1"
        filter = {"id": id}
        logger.debug(f"{query} : {str(filter)}")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, filter)
            vo = self.fetchone(cursor, True)
            return vo
        finally:
            cursor.close()

    def exist_by_name(self, name):
        query = f"SELECT * FROM {self.__table__} WHERE name=:name LIMIT 1"
        filter = {"name": name}
        logger.debug(f"{query} : {str(filter)}")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, filter)
            vo = cursor.fetchone()
            if vo is None:
                return False
            else:
                return True
        finally:
            cursor.close()

    def exist_by_id(self, id):
        query = f"SELECT * FROM {self.__table__} WHERE {self.__PK__}=:id LIMIT 1"
        filter = {"id": id}
        logger.debug(f"{query} : {str(filter)}")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, filter)
            vo = cursor.fetchone()
            if vo is None:
                return False
            else:
                return True
        finally:
            cursor.close()

    def get_by_name(self, name):
        query = f"SELECT * FROM {self.__table__} WHERE name=:name LIMIT 1"
        filter = {"name": name}
        logger.debug(f"{query} : {str(filter)}")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, filter)
            vo = self.fetchone(cursor, True)
            return vo
        finally:
            cursor.close()

    def query_all(self, page=None, per_page=None, eager=False):
        if page and per_page:
            offset = (page - 1) * per_page
            query = (
                f"SELECT * FROM {self.__table__} limit :per_page offset :offset"
            )
            filter = {"offset": offset, "per_page": per_page}
        else:
            query = f"SELECT * FROM {self.__table__}"
            filter = {}

        logger.debug(f"{query} : {str(filter)}")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, filter)
            result = self.fetchall(cursor, eager)
            if page and per_page:
                count = self._total()
                page_count = ceil(count / per_page)
                page = {
                    "content": result,
                    "per_page": per_page,
                    "total_elements": count,
                    "total_pages": page_count,
                }
                return page

            else:
                return {
                    "content": result,
                    "per_page": len(result),
                    "total_elements": len(result),
                    "total_pages": 1,
                }
        finally:
            cursor.close()

    def update_by_id(self, pk, dict):
        vals = ", ".join(f"{key} = :{key}" for key in dict.keys())
        query = f"UPDATE {self.__table__} SET {vals} WHERE {self.__PK__} = :{self.__PK__}"
        dict[f"{self.__PK__}"] = pk
        logger.debug(f"{query} : {str(dict)}")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, dict)
        finally:
            cursor.close()

        return self.get_by_id(pk)

    def _total(self):
        query = f"SELECT count(1) FROM {self.__table__}"
        logger.debug(query)

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query)
            return cursor.fetchone()[0]
        finally:
            cursor.close()
