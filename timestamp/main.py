from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from timestamp import routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.root.router)
app.include_router(routes.timestamp.router)
app.include_router(routes.auth.router)
