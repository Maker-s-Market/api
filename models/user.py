import datetime
import enum
from uuid import uuid4

from fastapi import Depends
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship, Session

from db.database import Base, get_db
from models.wishList import Wishlist
from schemas.user import CreateUser, UserUpdate

followers = Table(
    'followers',
    Base.metadata,
    Column('follower_id', String(50), ForeignKey('user.id')),
    Column('followed_id', String(50), ForeignKey('user.id'))
)


def random_uuid():
    return str(uuid4())


class Role(enum.Enum):
    Client = "Client"
    Seller = "Seller"  # # TODO - remover
    Premium = "Premium"


class User(Base):
    __tablename__ = "user"
    # email and password are AWS cognito matters, not ours!

    id = Column(String(50), primary_key=True, index=True, default=random_uuid)
    name = Column(String(200), index=True, nullable=False)
    username = Column(String(200), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    city = Column(String(200), index=True, nullable=False)
    region = Column(String(200), index=True, nullable=False)
    photo = Column(String(200), index=True, nullable=False)
    role = Column(Enum(Role))
    avg_rating = Column(Float, index=True, default=0)
    created_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime(timezone=True), index=True, default=datetime.datetime.now(),
                        nullable=False)
    is_active = Column(Integer, index=True, default=True, nullable=False)
    # POR CAUSA DO RGPD
    deleted_at = Column(DateTime(timezone=True), index=True, nullable=True)  # TODO - remover

    wishlist_id = Column(String(50), ForeignKey("wishlist.id"))
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
            return True
        else:
            return False

    def is_following(self, user):
        return any(follower.id == user.id for follower in self.followed)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "city": self.city,
            "region": self.region,
            "photo": self.photo,
            "role": self.role,
            "average_rating": self.avg_rating,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at,
            "is_active": self.is_active,
            "wishlist_id": self.wishlist_id,
        }

    def information(self, followed_bool: bool = True):
        info = {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "city": self.city,
            "region": self.region,
            "photo": self.photo,
            "average_rating": self.avg_rating,
            "created_at": self.created_at,
        }
        if followed_bool:
            info["followed"] = [user.information(followed_bool=False) for user in self.followed]
        return info

    def update_avg(self, db: Session, avg: float):
        self.avg_rating = avg
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session = Depends(get_db)):
        db.delete(self)
        db.commit()
        return self

    def active(self, db: Session = Depends(get_db)):
        self.is_active = True
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)
        return self

    def update(self, user: UserUpdate, db: Session = Depends(get_db)):
        self.name = user.name
        self.city = user.city
        self.region = user.region
        self.photo = user.photo
        self.updated_at = datetime.datetime.now()
        db.commit()
        db.refresh(self)
        return self


def save_user(new_user: CreateUser, db: Session = Depends(get_db)):
    wishlist = Wishlist(products=[])
    db.add(wishlist)
    db.commit()
    db.refresh(wishlist)

    db_user = User(name=new_user.name,
                   username=new_user.username,
                   email=new_user.email,
                   city=new_user.city,
                   region=new_user.region,
                   photo=new_user.photo,
                   role=Role.Client,
                   wishlist_id=wishlist.id,
                   is_active=False)
    
    db_user.is_active = False
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
