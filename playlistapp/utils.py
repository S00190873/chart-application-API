from . import app, db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def check_database_connection():
    try:
        with app.app_context():
            # Obtain a connection from the engine
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
        print("Database connection successful.")
    except SQLAlchemyError as e:
        print(f"Database connection error: {e}")
        exit(1)
