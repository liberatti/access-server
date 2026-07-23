from nxcore.common_utils import gen_random_string
from nxcore.middleware.logging_manager import logger
from nxcore.repository.duckdb_dao import DuckDAO
from typing import Dict, Any
import config


class UserDao(DuckDAO):
    """Data access object for users."""

    def __init__(self, connection=None, auto_commit=True):
        """Initialize UserDao instance.

        :param connection: Optional database connection instance.
        :type connection: duckdb.DuckDBPyConnection or None
        :param auto_commit: Whether to automatically commit operations.
        :type auto_commit: bool
        """
        super().__init__(
            db_path=config.DB_PATH,
            table_name="users",
            conn=connection,
            auto_commit=auto_commit,
        )
        self.connect()

    def create_schema(self):
        """Create the users table schema if it does not exist."""
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
        """Prepare value object dictionary before persisting.

        :param vo: Dictionary containing user attributes.
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
        :return: Entity dictionary including assigned policies or None.
        :rtype: dict or None
        """
        if row:
            if "_id" in row:
                row["id"] = row.pop("_id")
            up_model = UserPolicyDao(connection=self.conn)
            row.update({"policies": up_model.get_by_user_id(row["id"])})
        return row

    def _persist(self, vo: Dict[str, Any]) -> Any:
        """Inserts a new record.

        Args:
            vo (dict): Dictionary with record data.

        Returns:
            any: The last inserted ID.
        """
        vo = self.from_dict(vo)
        keys = ", ".join(vo.keys())
        values_placeholder = ", ".join(["?"] * len(vo))
        sql = f"INSERT INTO {self.table_name} ({keys}) VALUES ({values_placeholder})"
        values = list(vo.values())
        logger.debug(self._interpolate_sql(sql, values))
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, values)
            if self.auto_commit:
                self.commit()
        finally:
            cursor.close()

    def persist(self, vo):
        """Persist a new user record and policy assignments.

        :param vo: Dictionary containing user details.
        :type vo: dict
        :return: Generated primary key ID.
        :rtype: str
        """
        policies = None
        if "policies" in vo:
            policies = vo.pop("policies")

        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            vo["_id"] = gen_random_string(12)

        self._persist(vo)

        if policies:
            up_model = UserPolicyDao(connection=self.conn)
            up_model.delete_by_user(vo["_id"])
            for p in policies:
                policy_id = p.get("id") or p.get("_id")
                up_model.persist({"user_id": vo["_id"], "policy_id": policy_id})

        return vo["_id"]

    def update_by_id(self, pk, vo):
        """Update an existing user record by ID.

        :param pk: Primary key ID of the user.
        :type pk: str
        :param vo: Dictionary containing updated user fields.
        :type vo: dict
        :return: True if update succeeded.
        :rtype: bool
        """
        policies = None
        if "policies" in vo:
            policies = vo.pop("policies")

        vo = self.from_dict(vo)
        vo.pop("_id", None)
        res = super().update_by_id(pk, vo)

        if policies is not None:
            up_model = UserPolicyDao(connection=self.conn)
            up_model.delete_by_user(pk)
            for p in policies:
                policy_id = p.get("id") or p.get("_id")
                up_model.persist({"user_id": pk, "policy_id": policy_id})

        return res

    def get_descr(self, id):
        """Retrieve description details for a user.

        :param id: Primary key ID of the user.
        :type id: str
        :return: User entity dictionary or None if not found.
        :rtype: dict or None
        """
        sql = f"SELECT _id, name FROM {self.table_name} WHERE _id = ? limit 1"
        rs = self._query(sql, (id,), fetch=True)
        return self.to_dict(rs[0]) if rs else None

    def find_by_username(self, username):
        """Find a user record by username.

        :param username: Username of the user.
        :type username: str
        :return: User entity dictionary or None if not found.
        :rtype: dict or None
        """
        sql = f"SELECT * FROM {self.table_name} WHERE username = ? limit 1"
        rs = self._query(sql, (username,), fetch=True)
        return self.to_dict(rs[0]) if rs else None

    def query_all(self, page=None, per_page=None):
        """Query users with optional pagination.

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


class UserPolicyDao(DuckDAO):
    """Data access object for user-to-policy mappings."""

    def __init__(self, connection=None, auto_commit=True):
        """Initialize UserPolicyDao instance.

        :param connection: Optional database connection instance.
        :type connection: duckdb.DuckDBPyConnection or None
        :param auto_commit: Whether to automatically commit operations.
        :type auto_commit: bool
        """
        super().__init__(
            db_path=config.DB_PATH,
            table_name="user_policies",
            conn=connection,
            auto_commit=auto_commit,
        )
        self.connect()

    def create_schema(self):
        """Create the user_policies table schema if it does not exist."""
        self.connect()
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                user_id varchar(12),
                policy_id varchar(12)
            )
            """
        )

    def get_by_user_id(self, user_id):
        """Retrieve all policies associated with a user ID.

        :param user_id: User identifier.
        :type user_id: str
        :return: List of policy dictionaries.
        :rtype: list[dict]
        """
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ?"
        rows = self._query(sql, (user_id,), fetch=True)
        policies = []
        if rows:
            from api.model.policy_model import PolicyDao

            p_model = PolicyDao(connection=self.conn)
            for r in rows:
                p = p_model.get_by_id(r["policy_id"])
                if p:
                    policies.append(p)
                else:
                    logger.info(f"policy {r['policy_id']} not found")
        return policies

    def delete_by_user(self, user_id):
        """Delete all policy assignments for a user ID.

        :param user_id: User identifier.
        :type user_id: str
        """
        sql = f"DELETE FROM {self.table_name} WHERE user_id = ?"
        self._query(sql, (user_id,))
        if self.auto_commit:
            self.commit()

    def persist(self, vo: Dict[str, Any]) -> Any:
        """Persist a new user policy mapping record without RETURNING _id.

        :param vo: Dictionary containing mapping data.
        :type vo: dict
        """
        vo = self.from_dict(vo)
        keys = ", ".join(vo.keys())
        values_placeholder = ", ".join(["?"] * len(vo))
        sql = f"INSERT INTO {self.table_name} ({keys}) VALUES ({values_placeholder})"
        values = list(vo.values())
        logger.debug(self._interpolate_sql(sql, values))
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, values)
            if self.auto_commit:
                self.commit()
        finally:
            cursor.close()
