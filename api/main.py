from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List
from datetime import datetime

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:mypassword@db:5432/appdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy base model
Base = declarative_base()

# SQLAlchemy model
class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=text("timezone('utc'::text, now())"))

# Pydantic models
class PostBase(BaseModel):
    title: str
    content: str
    image_url: str = None

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostInDB(PostBase):
    post_id: int
    created_at: datetime

# FastAPI application
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/posts/", response_model=PostInDB)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/", response_model=List[PostInDB])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(Post).offset(skip).limit(limit).all()
    return posts

@app.get("/posts/{post_id}", response_model=PostInDB)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=PostInDB)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.post_id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.post_id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"detail": "Post deleted"}