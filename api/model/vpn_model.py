from nxcore.common_utils import gen_random_string
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
        self.create_schema()

    def create_schema(self):
        """Create the sessions table schema and primary key index if not exists."""
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                _id varchar(12),
                user_id varchar(12),
                remote_port integer,
                remote_ip varchar(100),
                local_ip varchar(100),
                state varchar(64),
                created_at TIMESTAMP,
                bytes_received BIGINT DEFAULT 0,
                bytes_sent BIGINT DEFAULT 0
            )
            """
        )
        self.ddl(
            f"CREATE UNIQUE INDEX if not exists {self.table_name}_pk ON {self.table_name}(_id)"
        )
        try:
            self.ddl(f"ALTER TABLE {self.table_name} ADD COLUMN created_at varchar(64)")
        except Exception:
            pass

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

    def persist(self, vo):
        """Persist a new VPN session record.

        :param vo: Dictionary containing VPN session details.
        :type vo: dict
        :return: Generated primary key ID.
        :rtype: str
        """
        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            vo["_id"] = gen_random_string(12)
        super().persist(vo)
        return vo["_id"]

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

    def query_all(self, page=None, per_page=None):
        """Query sessions with optional pagination.

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
