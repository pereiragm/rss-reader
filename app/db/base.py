# Import all the models, so that Base has them before being imported by Alembic
from app.db.base_class import Base  # noqa
from app.models import User  # noqa
from app.models import Item  # noqa
from app.models import Feed  # noqa
from app.models import Post  # noqa
