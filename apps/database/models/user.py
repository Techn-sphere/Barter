from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.database.mixins.id_mixins import IDMixin
from apps.database.mixins.timestamp_mixins import TimestampsMixin
from apps.database.models.base import Base


class User(IDMixin, TimestampsMixin, Base):
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, unique=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
