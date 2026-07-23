from nxcore.common_utils import gen_random_string
from nxcore.repository.duckdb_dao import DuckDAO

import config


class DMZServiceDao(DuckDAO):
    """Data access object for DMZ services."""

    def __init__(self, connection=None, auto_commit=True):
        """Initialize DMZServiceDao instance.

        :param connection: Optional database connection instance.
        :type connection: duckdb.DuckDBPyConnection or None
        :param auto_commit: Whether to automatically commit operations.
        :type auto_commit: bool
        """
        super().__init__(
            db_path=config.DB_PATH,
            table_name="dmz",
            conn=connection,
            auto_commit=auto_commit,
        )
        self.connect()

    def create_schema(self):
        """Create the DMZ table schema if it does not exist."""
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                _id varchar(12) PRIMARY KEY,
                name varchar(64),
                description varchar(200)
            )
            """
        )

    def from_dict(self, vo):
        """Prepare value object dictionary before persisting.

        :param vo: Dictionary containing entity attributes.
        :type vo: dict
        :return: Transformed dictionary with normalized primary key.
        :rtype: dict
        """
        if vo and "id" in vo:
            vo["_id"] = vo.pop("id")
        return super().from_dict(vo)

    def to_dict(self, row):
        """Transform database row into domain dictionary.

        :param row: Database row record.
        :type row: dict or None
        :return: Entity dictionary including associated port mappings.
        :rtype: dict or None
        """
        if row:
            if "_id" in row:
                row["id"] = row.pop("_id")
            p_model = PortMappingDao(connection=self.conn)
            row.update({"port_mappings": p_model.get_by_dmz_id(row["id"])})
        return row

    def persist(self, vo):
        """Persist a new DMZ service record and its port mappings.

        :param vo: Dictionary containing DMZ service details.
        :type vo: dict
        :return: Generated primary key ID.
        :rtype: str
        """
        port_mappings = None
        if "port_mappings" in vo:
            port_mappings = vo.pop("port_mappings")

        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            vo["_id"] = gen_random_string(12)

        super().persist(vo)

        if port_mappings:
            p_model = PortMappingDao(connection=self.conn)
            for pm in port_mappings:
                pm.update({"dmz_id": vo["_id"]})
                p_model.persist(pm)

        return vo["_id"]

    def update_by_id(self, pk, vo):
        """Update an existing DMZ service record by ID.

        :param pk: Primary key ID of the DMZ service.
        :type pk: str
        :param vo: Dictionary containing updated DMZ fields.
        :type vo: dict
        :return: True if update succeeded.
        :rtype: bool
        """
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
        """Retrieve description details for a DMZ service.

        :param id: Primary key ID of the DMZ service.
        :type id: str
        :return: DMZ service entity dictionary or None if not found.
        :rtype: dict or None
        """
        sql = f"SELECT _id, name FROM {self.table_name} WHERE _id = ? limit 1"
        rs = self._query(sql, (id,), fetch=True)
        return self.to_dict(rs[0]) if rs else None

    def query_all(self, page=None, per_page=None):
        """Query DMZ services with optional pagination.

        :param page: Page number for pagination.
        :type page: int or None
        :param per_page: Number of items per page.
        :type per_page: int or None
        :return: Dictionary containing metadata and data records.
        :rtype: dict
        """
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


class PortMappingDao(DuckDAO):
    """Data access object for port mappings."""

    def __init__(self, connection=None, auto_commit=True):
        """Initialize PortMappingDao instance.

        :param connection: Optional database connection instance.
        :type connection: duckdb.DuckDBPyConnection or None
        :param auto_commit: Whether to automatically commit operations.
        :type auto_commit: bool
        """
        super().__init__(
            db_path=config.DB_PATH,
            table_name="user_ports",
            conn=connection,
            auto_commit=auto_commit,
        )
        self.connect()

    def create_schema(self):
        """Create the user_ports table schema if it does not exist."""
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
        """Prepare value object dictionary before persisting.

        :param vo: Dictionary containing port mapping attributes.
        :type vo: dict
        :return: Transformed dictionary with normalized primary key.
        :rtype: dict
        """
        if vo and "id" in vo:
            vo["_id"] = vo.pop("id")
        return super().from_dict(vo)

    def to_dict(self, row):
        """Transform database row into domain dictionary with user details.

        :param row: Database row record.
        :type row: dict or None
        :return: Entity dictionary with user description or None.
        :rtype: dict or None
        """
        if row:
            if "_id" in row:
                row["id"] = row.pop("_id")
            from api.model.user_model import UserDao

            dao = UserDao(connection=self.conn)
            row.update({"user": dao.get_descr(row["user_id"])})
        return row

    def persist(self, vo):
        """Persist a new port mapping record.

        :param vo: Dictionary containing port mapping details.
        :type vo: dict
        :return: Generated primary key ID.
        :rtype: str
        """
        user = vo.pop("user")
        user_id = user.get("id") or user.get("_id")
        vo.update({"user_id": user_id})

        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            vo["_id"] = gen_random_string(12)

        super().persist(vo)
        return vo["_id"]

    def is_free(self, bind_port):
        """Check if a bind port is available.

        :param bind_port: Port number to check.
        :type bind_port: int
        :return: True if the port is free, False otherwise.
        :rtype: bool
        """
        sql = f"SELECT * FROM {self.table_name} WHERE bind_port = ? LIMIT 1"
        rs = self._query(sql, (bind_port,), fetch=True)
        return len(rs) == 0

    def get_by_user_id(self, user_id):
        """Retrieve all port mappings assigned to a specific user.

        :param user_id: User identifier.
        :type user_id: str
        :return: List of port mapping dictionaries.
        :rtype: list[dict]
        """
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ?"
        rs = self._query(sql, (user_id,), fetch=True)
        return [self.to_dict(r) for r in rs] if rs else []

    def delete_by_user(self, user_id):
        """Delete all port mappings for a specific user.

        :param user_id: User identifier.
        :type user_id: str
        """
        sql = f"DELETE FROM {self.table_name} WHERE user_id = ?"
        self._query(sql, (user_id,))
        if self.auto_commit:
            self.commit()

    def get_by_dmz_id(self, dmz_id):
        """Retrieve all port mappings assigned to a DMZ service.

        :param dmz_id: DMZ service identifier.
        :type dmz_id: str
        :return: List of port mapping dictionaries.
        :rtype: list[dict]
        """
        sql = f"SELECT * FROM {self.table_name} WHERE dmz_id = ?"
        rs = self._query(sql, (dmz_id,), fetch=True)
        return [self.to_dict(r) for r in rs] if rs else []

    def delete_by_dmz(self, dmz_id):
        """Delete all port mappings for a DMZ service.

        :param dmz_id: DMZ service identifier.
        :type dmz_id: str
        """
        sql = f"DELETE FROM {self.table_name} WHERE dmz_id = ?"
        self._query(sql, (dmz_id,))
        if self.auto_commit:
            self.commit()
