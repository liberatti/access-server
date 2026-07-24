from nxcore.repository.duckdb_dao import DuckDAO
import config


class VPNSessionDao(DuckDAO):
    """Data access object for VPN sessions."""

    def __init__(self, auto_commit=True):
        """Initialize VPNSessionDao instance.

        :param auto_commit: Whether to automatically commit operations.
        :type auto_commit: bool
        """
        super().__init__(
            db_path=config.DB_PATH, table_name="sessions", auto_commit=auto_commit
        )
        self.connect()

    def create_schema(self):
        """Create the sessions table schema and primary key index if not exists."""
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
        self.ddl(
            f"CREATE UNIQUE INDEX if not exists {self.table_name}_pk ON {self.table_name}(_id)"
        )

    def from_dict(self, vo):
        """Prepare value object dictionary before persisting.

        :param vo: Dictionary containing VPN session attributes.
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
        :return: Entity dictionary with normalized id or None.
        :rtype: dict or None
        """
        if row and "_id" in row:
            row["id"] = row.pop("_id")
        return row

    def delete_by_user_id(self, user_id):
        """Delete all VPN sessions for a given user ID.

        :param user_id: User identifier.
        :type user_id: str
        """
        sql = f"DELETE FROM {self.table_name} WHERE user_id = ?"
        self._query(sql, (user_id,))
        if self.auto_commit:
            self.commit()

    def get_all_by_user_id(self, user_id):
        """Retrieve all VPN sessions assigned to a user ID.

        :param user_id: User identifier.
        :type user_id: str
        :return: List of VPN session dictionaries.
        :rtype: list[dict]
        """
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ?"
        rs = self._query(sql, (user_id,), fetch=True)
        return [self.to_dict(r) for r in rs] if rs else []

    def get_by_user_id(self, user_id):
        """Retrieve active VPN session for a given user ID.

        :param user_id: User identifier.
        :type user_id: str
        :return: VPN session dictionary if active, else None.
        :rtype: dict or None
        """
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ? and state='activated' limit 1"
        rs = self._query(sql, (user_id,), fetch=True)
        return self.to_dict(rs[0]) if rs else None
