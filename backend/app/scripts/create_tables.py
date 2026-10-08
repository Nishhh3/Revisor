"""
Run once to create the reviews/findings tables. Not using Alembic
migrations yet -- that's real overhead you don't need until the
schema needs to evolve under existing data, which isn't the case
during initial development.
"""
from app.models.database import Base, engine
from app.models.review import Review, Finding  # noqa: F401 -- import registers models with Base

Base.metadata.create_all(engine)
print("Tables created.")