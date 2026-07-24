from nxcore.repository.duckdb_dao import DuckDAO
from flask import json
import config


class ServerConfigDao(DuckDAO):
    """Data access object for server configuration."""

    def __init__(self, connection=None, auto_commit=True):
        """Initialize ServerConfigDao instance.

        :param connection: Optional database connection instance.
        :type connection: duckdb.DuckDBPyConnection or None
        :param auto_commit: Whether to automatically commit operations.
        :type auto_commit: bool
        """
        super().__init__(
            db_path=config.DB_PATH,
            table_name="server_config",
            conn=connection,
            auto_commit=auto_commit,
        )
        self.connect()

    def create_schema(self):
        """Create the server_config table schema and primary key index if not exists."""
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                _id varchar(12) PRIMARY KEY,
                name varchar(64),
                network varchar(64),
                netmask varchar(64),
                port integer,
                protocol varchar(10),
                admin_pk varchar(12),
                public_address varchar(100),
                public_port integer,
                auth varchar(64),
                cipher varchar(64),
                data_ciphers varchar(200),
                networks_json TEXT
            )
            """
        )

    def from_dict(self, vo):
        """Prepare value object dictionary before persisting.

        :param vo: Dictionary containing configuration attributes.
        :type vo: dict
        :return: Transformed dictionary with normalized primary key and json fields.
        :rtype: dict
        """
        if vo:
            if "id" in vo:
                vo["_id"] = vo.pop("id")
            if "networks" in vo:
                vo["networks_json"] = json.dumps(vo.pop("networks"))
            if "data-ciphers" in vo:
                vo["data_ciphers"] = vo.pop("data-ciphers")
        return super().from_dict(vo)

    def to_dict(self, row):
        """Transform database row into domain dictionary.

        :param row: Database row record.
        :type row: dict or None
        :return: Entity dictionary including deserialized networks or None.
        :rtype: dict or None
        """
        if row:
            if "_id" in row:
                row["id"] = row.pop("_id")
            if "networks_json" in row and row["networks_json"]:
                row.update({"networks": json.loads(row.pop("networks_json"))})
            if "data_ciphers" in row:
                row["data-ciphers"] = row.pop("data_ciphers")
        return row

    def get_config(self):
        """Retrieve the default/only server configuration.

        :return: Server configuration dictionary if exists, else None.
        :rtype: dict or None
        """
        sql = f"SELECT * FROM {self.table_name} LIMIT 1"
        rs = self._query(sql, fetch=True)
        return self.to_dict(rs[0]) if rs else None

    def persist(self, vo):
        """Persist a new server configuration record.

        :param vo: Dictionary containing server configuration details.
        :type vo: dict
        :return: Generated primary key ID.
        :rtype: str
        """
        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            vo["_id"] = "default"
        super().persist(vo)
        return vo["_id"]

    def update_by_id(self, pk, vo):
        """Update an existing server configuration record by ID.

        :param pk: Primary key ID of the server configuration.
        :type pk: str
        :param vo: Dictionary containing updated server configuration fields.
        :type vo: dict
        :return: True if update succeeded.
        :rtype: bool
        """
        vo = self.from_dict(vo)
        vo.pop("_id", None)
        vo.pop("networks", None)
        return super().update_by_id(pk, vo)
