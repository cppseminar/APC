from types import SimpleNamespace

HEADER_EMAIL="X-REQUEST-EMAIL"
DB_NAME = "development"
COL_USERS = "users"
COL_SUBMISSIONS = "submissions"

SCHEMA_USER = SimpleNamespace (
    EMAIL="email",
    ROLES="roles",
    IS_ADMIN="is_admin",
)
