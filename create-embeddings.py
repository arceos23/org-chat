import os
from sqlalchemy import create_engine, text
from ollama import Client

POSTGRES_URL = f"postgresql+psycopg://{os.environ.get('PG_LOCAL_USER')}:{os.environ.get('PG_LOCAL_PASSWORD')}@localhost:{os.environ.get('PG_PORT')}"
OLLAMA_URL = f"http://localhost:{os.environ.get('OL_PORT')}"


def create_embeddings():
    engine = create_engine(POSTGRES_URL)
    with engine.connect() as connection:
        people = connection.execute(
            text(
                """
                    SELECT P.id, P.name AS name, T.name AS title, O.name AS organization, P.about AS about
                    FROM person P
                    JOIN title T
                    ON P.title_id = T.id
                    JOIN organization O
                    ON P.organization_id = O.id;
                """
            )
        )

        person_prompts, person_ids = [], []
        for person in people:
            person_prompts.append(
                f"name: {person.name}\n"
                f"title: {person.title}\n"
                f"organization: {person.organization}\n"
                f"about: {person.about}"
            )
            person_ids.append(person.id)

        client = Client(
            host=OLLAMA_URL,
        )

        for i, person_prompt in enumerate(person_prompts):
            embedding = client.embeddings(
                model="nomic-embed-text",
                prompt=person_prompt,
            )

            connection.execute(
                text(
                    """
                        INSERT INTO person_embeddings (person_id, embedding)
                        VALUES (:person_id, :embedding);
                    """
                ),
                {"person_id": person_ids[i], "embedding": embedding.embedding},
            )
            connection.commit()


if __name__ == "__main__":
    create_embeddings()
