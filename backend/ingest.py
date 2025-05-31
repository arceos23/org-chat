import os
import json
import psycopg

POSTGRES_URL = f"postgresql://{os.environ.get('PG_LOCAL_USER')}:{os.environ.get('PG_LOCAL_PASSWORD')}@localhost:{os.environ.get('PG_PORT')}"


def main():
    try:
        with open("./people.json", "r") as file:
            data = json.load(file)

            with psycopg.connect(POSTGRES_URL) as conn:
                with conn.cursor() as cur:
                    for person in data["people"]:
                        # Insert organization
                        organization = person["organization"]
                        organization_id = cur.execute(
                            """
                                WITH e AS (
                                    INSERT INTO organization (name)
                                    VALUES (%s)
                                    ON CONFLICT (name) DO NOTHING
                                    RETURNING id
                                )
                                SELECT *
                                FROM e
                                UNION
                                    SELECT id
                                    FROM organization
                                    WHERE name = %s;
                            """,
                            [organization, organization],
                        ).fetchone()[0]

                        # Insert title
                        title = person["title"]
                        title_id = cur.execute(
                            """
                                WITH e AS (
                                    INSERT INTO title (name)
                                    VALUES (%s)
                                    ON CONFLICT (name) DO NOTHING
                                    RETURNING id
                                )
                                SELECT *
                                FROM e
                                UNION
                                    SELECT id
                                    FROM title
                                    WHERE name = %s;
                            """,
                            [title, title],
                        ).fetchone()[0]

                        # Insert person
                        cur.execute(
                            """
                                INSERT INTO person (name, title_id, organization_id, about)
                                VALUES (%s, %s, %s, %s);
                            """,
                            [
                                person["name"],
                                title_id,
                                organization_id,
                                person["about"],
                            ],
                        )
                    conn.commit()

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")


if __name__ == "__main__":
    main()
