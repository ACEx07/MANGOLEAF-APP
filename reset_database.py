"""
Reset the database to its initial state and purge user data
"""

from dotenv import load_dotenv
from sqlalchemy.sql import text

from mangoleaf import Connection


def main():
    # Establish a connection to the database
    db_engine = Connection().get()

    # Create schema from SQL file
    with open("reset_dynamic_tables.sql") as f:
        sql_commands = f.read()

    print("Reset dynamic tables")
    with db_engine.connect() as connection:
        for command in sql_commands.split(";"):
            if command.strip():
                connection.execute(text(command))
        connection.commit()


if __name__ == "__main__":
    load_dotenv(".streamlit/secrets.toml")
    main()
