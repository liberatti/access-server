from nxcore.common_utils import gen_random_string
from nxcore.repository.duckdb_dao import DuckDAO
from flask import json
import config


class PolicyDao(DuckDAO):
    """Data access object for policies."""

    def __init__(self, connection=None, auto_commit=True):
        """Initialize PolicyDao instance.

        :param connection: Optional database connection instance.
        :type connection: duckdb.DuckDBPyConnection or None
        :param auto_commit: Whether to automatically commit operations.
        :type auto_commit: bool
        """
        super().__init__(
            db_path=config.DB_PATH,
            table_name="policy",
            conn=connection,
            auto_commit=auto_commit,
        )
        self.connect()

    def create_schema(self):
        """Create the policy table schema if it does not exist."""
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                _id varchar(12) PRIMARY KEY,
                name varchar(64),
                type varchar(64),
                networks_json TEXT
            )
            """
        )

    def from_dict(self, vo):
        """Prepare value object dictionary before persisting.

        :param vo: Dictionary containing policy attributes.
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
        :return: Entity dictionary including deserialized networks and client targets.
        :rtype: dict or None
        """
        if row:
            if "_id" in row:
                row["id"] = row.pop("_id")
            p_model = PolicyClientDao(connection=self.conn)
            if "networks_json" in row and row["networks_json"]:
                row.update({"networks": json.loads(row.pop("networks_json"))})
            row.update({"clients": p_model.get_by_policy(row["id"])})
        return row

    def persist(self, vo):
        """Persist a new policy record and its client associations.

        :param vo: Dictionary containing policy details.
        :type vo: dict
        :return: Generated primary key ID.
        :rtype: str
        """
        if "networks" in vo:
            vo.update({"networks_json": json.dumps(vo.pop("networks"))})

        vo = self.from_dict(vo)
        if "_id" not in vo or not vo["_id"]:
            vo["_id"] = gen_random_string(12)

        if "clients" in vo:
            targets = vo.pop("clients")
            super().persist(vo)
            p_model = PolicyClientDao(connection=self.conn)
            p_model.delete_by_policy(vo["_id"])
            for t in targets:
                client_id = t.get("id") or t.get("_id")
                p_model.persist({"policy_id": vo["_id"], "user_id": client_id})
        else:
            super().persist(vo)

        return vo["_id"]

    def update_by_id(self, pk, vo):
        """Update an existing policy record by ID.

        :param pk: Primary key ID of the policy.
        :type pk: str
        :param vo: Dictionary containing updated policy fields.
        :type vo: dict
        :return: True if update succeeded.
        :rtype: bool
        """
        if "networks" in vo:
            vo.update({"networks_json": json.dumps(vo.pop("networks"))})
        if "clients" in vo:
            clients = vo.pop("clients")
            p_model = PolicyClientDao(connection=self.conn)
            p_model.delete_by_policy(pk)
            for t in clients:
                client_id = t.get("id") or t.get("_id")
                p_model.persist({"policy_id": pk, "user_id": client_id})

        vo = self.from_dict(vo)
        return super().update_by_id(pk, vo)

    def query_all(self, page=None, per_page=None):
        """Query policies with optional pagination.

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


class PolicyClientDao(DuckDAO):
    """Data access object for policy-to-client mappings."""

    def __init__(self, connection=None, auto_commit=True):
        """Initialize PolicyClientDao instance.

        :param connection: Optional database connection instance.
        :type connection: duckdb.DuckDBPyConnection or None
        :param auto_commit: Whether to automatically commit operations.
        :type auto_commit: bool
        """
        super().__init__(
            db_path=config.DB_PATH,
            table_name="policy_clients",
            conn=connection,
            auto_commit=auto_commit,
        )
        self.connect()

    def create_schema(self):
        """Create the policy_clients table schema and index if not exists."""
        self.connect()
        self.ddl(
            f"""CREATE TABLE if not exists {self.table_name} (
                policy_id varchar(12),
                user_id varchar(12),
                FOREIGN KEY (policy_id) REFERENCES policy(_id),
                FOREIGN KEY (user_id) REFERENCES users(_id)
            )
            """
        )
        self.ddl(
            f"CREATE INDEX if not exists {self.table_name}_pk ON {self.table_name}(policy_id)"
        )

    def delete_by_policy(self, policy_id):
        """Delete all client associations for a given policy ID.

        :param policy_id: Policy identifier.
        :type policy_id: str
        """
        sql = f"DELETE FROM {self.table_name} WHERE policy_id = ?"
        self._query(sql, (policy_id,))
        if self.auto_commit:
            self.commit()

    def get_by_policy(self, policy_id):
        """Retrieve all clients assigned to a specific policy.

        :param policy_id: Policy identifier.
        :type policy_id: str
        :return: List of target dictionaries containing client IDs.
        :rtype: list[dict]
        """
        sql = f"SELECT * FROM {self.table_name} WHERE policy_id = ?"
        rows = self._query(sql, (policy_id,), fetch=True)
        targets = []
        if rows:
            for r in rows:
                targets.append({"id": r["user_id"]})
        return targets

    def get_by_client(self, user_id):
        """Retrieve all policies assigned to a specific client.

        :param user_id: User identifier.
        :type user_id: str
        :return: List of target dictionaries containing policy IDs.
        :rtype: list[dict]
        """
        sql = f"SELECT * FROM {self.table_name} WHERE user_id = ?"
        rows = self._query(sql, (user_id,), fetch=True)
        targets = []
        if rows:
            for r in rows:
                targets.append({"id": r["policy_id"]})
        return targets
