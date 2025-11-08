from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from itertools import count
from typing import Annotated
import uvicorn

import model
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI(
    title="WiseCook",
    version="0.1.0",
    description="A minimal, generic FastAPI application with simple in-memory recipe storage.",
)

model.Base.metadata.create_all (bind = engine)
_id_counter = count(1)

#data validation

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]


@app.post('/users/', status_code=status.HTTP_201_CREATED)
async def create_user(user:UserBase, db:db_dependency):
    db_user = model.User(**user.dict())
    db.add(db_user)

# In-memory "database"

@app.on_event("startup")
async def startup_event():
    # seed with a couple of examples
    r1 = Recipe(id=next(_id_counter), title="Tomato Pasta", ingredients=["tomato", "pasta", "olive oil"], instructions="Cook pasta and toss with sauce.")
    r2 = Recipe(id=next(_id_counter), title="Avocado Toast", ingredients=["bread", "avocado", "salt"], instructions="Toast bread, mash avocado, season.")
    _recipes[r1.id] = r1
    _recipes[r2.id] = r2


@app.get("/", response_model=dict)
async def read_root():
    return {"service": "Recipe Recommender", "version": app.version}


@app.get("/health", response_model=dict)
async def health():
    return {"status": "ok"}



if __name__ == "__main__":

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)