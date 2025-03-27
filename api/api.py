import os
from typing import List
from pydantic import BaseModel, UUID4
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from ollama import Client, chat, ChatResponse

app = FastAPI()

POSTGRES_URL = f"postgresql+psycopg://{os.environ.get('PG_LOCAL_USER')}:{os.environ.get('PG_LOCAL_PASSWORD')}@localhost:{os.environ.get('PG_PORT')}"
OLLAMA_URL = f"http://localhost:{os.environ.get('OL_PORT')}"


class Person(BaseModel):
    id: UUID4
    name: str
    title: str
    organization: str
    about: str | None = None


DOCUMENT_LIMIT = 5


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


@app.get("/chat", response_model=str)
def get_chat(query: str) -> str:
    engine = create_engine(POSTGRES_URL, echo=True)
    with engine.connect() as connection:
        client = Client(
            host=OLLAMA_URL,
        )
        response = client.embeddings(
            model="nomic-embed-text",
            prompt=query,
        )

        rows = connection.execute(
            text(
                """
                    SELECT person_id
                    FROM person_embeddings
                    ORDER BY embedding <=> :query_embedding
                    LIMIT :limit;
                """
            ),
            {"query_embedding": str(response.embedding), "limit": DOCUMENT_LIMIT},
        ).fetchall()

        relevant_person_ids = [str(row.person_id) for row in rows]
        rows = connection.execute(
            text(
                """
                    SELECT P.id AS id, P.name AS name, T.name AS title, O.name AS organization, P.about AS about
                    FROM person P
                    JOIN title T
                    ON P.title_id = T.id
                    JOIN organization O
                    ON P.organization_id = O.id
                    WHERE P.id = ANY(:relevant_person_ids);
                """
            ),
            {"relevant_person_ids": relevant_person_ids},
        )

        context = "\n".join(
            f"name: {person.name}\n"
            f"title: {person.title}\n"
            f"organization: {person.organization}\n"
            f"about: {person.about}"
            for person in rows
        )

        response: ChatResponse = chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": f"{context}\n{query}",
                },
            ],
        )
        return response["message"]["content"]
