from fastapi import FastAPI
from app.routers import auth
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import stripe

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stripe.api_key = ""

app.include_router(auth.router, prefix="/api")

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        reload=True,
        workers=1
    )