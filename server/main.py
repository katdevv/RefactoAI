from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.backend.routers.routes import router as tasks_router

app = FastAPI(title="RefactoAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

app.include_router(tasks_router)
