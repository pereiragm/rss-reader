# Import all the models, so that Base has them before being imported by Alembic
from rss_reader.db.base_class import Base  # noqa
from rss_reader.models import User  # noqa
from rss_reader.models import Item  # noqa
