import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class Settings(BaseModel):
    DATABASE_URL: str
    REDIS_URL: str


settings = Settings(
    DATABASE_URL=os.getenv(
        "DATABASE_URL", "postgresql://user@localhost:5432/dbname"
    ),
    REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379"),
)
