from sqlalchemy import Column, Integer, String, DateTime, func, DECIMAL, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from env import DB


engine = create_engine(
    f'mysql+pymysql://{DB["user"]}:{DB["password"]}@{DB["host"]}:{DB["port"]}/{DB["db_name"]}',
    echo=False,
    encoding="utf8",
    connect_args={"charset": "utf8mb4",
                  "binary_prefix": True,
                  }
)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class BaseModel(Base):

    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Hotel(BaseModel):

    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True)
    unique_hotel_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    stars = Column(Integer)
    rating = Column(DECIMAL(3, 1))
    description = Column(Text(collation='utf8mb4_unicode_ci'))
    highlights = Column(Text(collation='utf8mb4_unicode_ci'))
    image = Column(String(255, collation='utf8mb4_unicode_ci'))
    address = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    country = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    rooms = relationship("Room", back_populates="hotel", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        self.unique_hotel_id = kwargs["unique_hotel_id"]
        self.name = kwargs["name"]
        self.stars = kwargs["stars"]
        self.rating = kwargs["rating"]
        self.description = kwargs["description"]
        self.highlights = kwargs["highlights"]
        self.image = kwargs["images"][0]["path"]
        self.address = kwargs["address"]
        self.country = kwargs["country"]

    def __repr__(self):
        return f"<Hotel({self.name})>"

    def update(self, new_hotel):

        self.name = new_hotel.name
        self.stars = new_hotel.stars
        self.rating = new_hotel.rating
        self.description = new_hotel.description
        self.highlights = new_hotel.highlights
        self.image = new_hotel.image
        self.address = new_hotel.address
        self.country = new_hotel.country

        room_id_list = []

        rooms_for_delete = []

        for old_room in self.rooms:
            room_id_list.append(old_room.unique_room_id)
            for new_room in new_hotel.rooms:
                if new_room.unique_room_id == old_room.unique_room_id:
                    old_room.update(new_room)
                    break
            else:
                rooms_for_delete.append(old_room)

        for old_room in rooms_for_delete:
                self.rooms.remove(old_room)

        rooms_for_append = []

        for new_room in new_hotel.rooms:
            if new_room.unique_room_id not in room_id_list:
                rooms_for_append.append(new_room)

        for new_room in rooms_for_append:
            new_hotel.rooms.remove(new_room)
            self.rooms.append(new_room)

        return None


class Room(BaseModel):

    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String(255, collation='utf8mb4_unicode_ci'))
    hotel_id = Column(Integer, ForeignKey('hotels.id', ondelete="CASCADE"), nullable=False)
    hotel = relationship("Hotel", back_populates="rooms")
    unique_room_id = Column(Integer, unique=True, nullable=False)
    description = Column(Text(collation='utf8mb4_unicode_ci'))
    image = Column(String(255, collation='utf8mb4_unicode_ci'))
    conditions = relationship("RoomConditions", back_populates="room", cascade="all, delete-orphan")

    def __init__(self, **kwargs):

        self.name = kwargs["name"]
        self.unique_room_id = kwargs["room_id"]
        self.description = kwargs["description"]
        self.image = kwargs["image"]

    def update(self, new_room):

        self.name = new_room.name
        self.description = new_room.description
        self.image = new_room.image

        block_id_list = []

        conditions_for_delete = []

        for old_condition in self.conditions:
            block_id_list.append(old_condition.unique_block_id)
            for new_condition in new_room.conditions:
                if new_condition.unique_block_id == old_condition.unique_block_id:
                    old_condition.update(new_condition)
                    break
            else:
                conditions_for_delete.append(old_condition)

        for old_condition in conditions_for_delete:
            self.conditions.remove(old_condition)

        conditions_for_append = []

        for new_condition in new_room.conditions:
            if new_condition.unique_block_id not in block_id_list:
                conditions_for_append.append(new_condition)

        for new_condition in conditions_for_append:
            new_room.conditions.remove(new_condition)
            self.conditions.append(new_condition)

        return None

    def __repr__(self):
        return f"<Room({self.name})>"


class RoomConditions(BaseModel):

    __tablename__ = 'room_conditions'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.id', ondelete="CASCADE"), nullable=False)
    room = relationship("Room", back_populates="conditions")
    unique_block_id = Column(String(255, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
    max_sleeps = Column(Integer)
    price = Column(DECIMAL(10, 2))
    currency = Column(String(255, collation='utf8mb4_unicode_ci'))
    conditions = Column(Text(collation='utf8mb4_unicode_ci'))

    def __init__(self, **kwargs):

        self.unique_block_id = kwargs["block_id"]
        self.max_sleeps = kwargs["occupancy"]
        self.price = kwargs["price"]
        self.currency = kwargs["currency"]
        self.conditions = kwargs["conditions"]

    def update(self, new_condition):

        self.max_sleeps = new_condition.max_sleeps
        self.price = new_condition.price
        self.currency = new_condition.currency
        self.conditions = new_condition.conditions

        return None

    def __repr__(self):
        return f"<Condition({self.unique_block_id})>"


Base.metadata.create_all(engine)
