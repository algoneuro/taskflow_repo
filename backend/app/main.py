from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, tasks, statistics

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API", version="1.0.0")

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(statistics.router)

@app.get("/")
def root():
    return {"message": "TaskFlow API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}