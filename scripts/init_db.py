from app.db import Base, engine
from app import models  # noqa: F401

def main():
    Base.metadata.create_all(bind=engine)
    print("DB initialized.")

if __name__ == "__main__":
    main()
