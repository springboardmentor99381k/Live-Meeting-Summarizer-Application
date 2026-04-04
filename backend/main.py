import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import process,stream,email_api

app = FastAPI()

#cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # to be changed later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(process.router)
app.include_router(stream.router)
app.include_router(email_api.router)