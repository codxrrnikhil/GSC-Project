from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes.content import router as content_router
from app.api.v1.routes.fingerprint import router as fingerprint_router
from app.api.v1.routes.crawler import router as crawler_router
from app.api.v1.routes.health import router as health_router
from app.api.test_db import router as test_db_router
from app.api.users import router as user_router
from app.core.database import get_database


app = FastAPI(title="Backend Service")
app.state.db = get_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(fingerprint_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(test_db_router)
app.include_router(crawler_router)

from app.api.v1.routes import content

app.include_router(content_router, prefix="/api/v1")


@app.post("/test-db")
def test_insert():
    db = get_database()
    data = {"name": "test_user"}
    result = db.test.insert_one(data)
    return {"inserted_id": str(result.inserted_id)}


@app.get("/test-db")
def test_read():
    db = get_database()
    data = list(db.test.find({}, {"_id": 0}))
    return data