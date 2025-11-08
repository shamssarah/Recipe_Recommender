from datetime import datetime
from database import Base

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Table,
    Float, relationship
)


recipe_tag = Table(
    "recipe_tag",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    recipes = relationship("Recipe", back_populates="author")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    ingredient = []
    instructions = Column(Text)
    rating = Column(Float)
    cook_time_min = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # cuisine = Column(String(100)) #-> preference algorithm 
    # calories = Column (String (100))
    # fiber = Column (String (100))
    # nutrition = Column (String (100))

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("User", back_populates="recipes")

    #one to many relation of recipe to tag
    tags = relationship("Tag", secondary=recipe_tag, back_populates="recipes")

    def __repr__(self):
        return f"<Recipe(id={self.id}, title={self.title})>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    recipes = relationship("Recipe", secondary=recipe_tag, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


