import os
from typing import List
from pydantic import BaseModel, UUID4
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI()

POSTGRES_URL = f"postgresql+psycopg://{os.environ.get('PG_LOCAL_USER')}:{os.environ.get('PG_LOCAL_PASSWORD')}@localhost:{os.environ.get('PG_PORT')}"


class Person(BaseModel):
    id: UUID4
    name: str
    title: str
    organization: str
    about: str | None = None


@app.get("/people", response_model=List[Person])
def get_people(offset: int = 0, limit: int = 5) -> List[Person]:
    engine = create_engine(POSTGRES_URL)
    with engine.connect() as connection:
        return connection.execute(
            text(
                """
                    SELECT P.id AS id, P.name AS name, T.name  title, O.name AS organization, P.about AS about
                    FROM person P
                    JOIN title T
                    ON P.title_id = T.id
                    JOIN organization O
                    ON P.organization_id = O.id
                    OFFSET :offset
                    LIMIT :limit;
                """
            ),
            {"offset": offset, "limit": limit},
        )
