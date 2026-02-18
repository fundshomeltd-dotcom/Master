from fastapi import FastAPI

from src.api.routes import router
from src.config.settings import settings
from src.db.base import Base
from src.db.session import engine
from src.scheduler import start_scheduler

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    start_scheduler()


@app.get("/health")
def health_check():
    return {"status": "ok"}
