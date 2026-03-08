from sqlmodel import create_engine, SQLModel

DATABASE_URL = "sqlite:///lochhaven.db"

engine = create_engine(DATABASE_URL, echo=True)

def create_db():
    SQLModel.metadata.create_all(engine)