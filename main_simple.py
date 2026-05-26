import sys
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

logger.info("Starting application...")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger.info("FastAPI imported")

app = FastAPI()

logger.info("FastAPI app created")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware added")

@app.get("/")
def root():
    logger.info("GET / called")
    return {"status": "ok"}

@app.get("/health")
def health():
    logger.info("GET /health called")
    return {"status": "ok"}

@app.post("/login")
def login(data: dict):
    logger.info("POST /login called")
    return {"token": "test", "user": {"id": 1}}

logger.info("Routes defined")
logger.info("Application ready!")

