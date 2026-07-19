from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Register all SQLAlchemy models
import app.auth.model  # noqa: E402,F401
import app.repositories.model  # noqa: E402,F401
import app.pull_requests.model  # noqa: E402,F401
import app.pull_request_files.model  # noqa: E402,F401