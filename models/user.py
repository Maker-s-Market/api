import uuid
import datetime
import enum
from uuid import UUID

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base

from db.base import Base

followers = Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('user.id')),
    Column('followed_id', Integer, ForeignKey('user.id'))
)


class Role(enum.Enum):
    Admin = "Admin"
    Client = "Client"
    Premium = "Premium"


class User(Base):
    __tablename__ = "user"

    #  TODO CHANGE TO uuid
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    # photo = Column(String(200), index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(Enum(Role))
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now().timestamp(),
                        nullable=False)

    # POR CAUSA DO RGPD
    deleted_at = Column(DateTime(timezone=True), index=True, nullable=True)
    is_active = Column(Integer, index=True, default=1, nullable=False)

    wishlist_id = Column(Integer, ForeignKey("wishlist.id"))
    followed = relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref="followers"
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
