from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from models import Signup, SignupBase
from database import create_db, engine

# Create the FastAPI app instance
app = FastAPI()

# CORS middleware allows the frontend (a different origin/port) to talk to this API
# Without this, browsers block requests from lochhavenlakes.org to our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # * means allow any origin — we'll lock this down later
    allow_methods=["*"],  # allow GET, POST, etc.
    allow_headers=["*"],  # allow any headers
)

# This runs automatically when the server starts
# It creates the database tables if they don't exist yet
@app.on_event("startup")
def on_startup():
    create_db()

# GET request to /signups — returns all signups from the database
@app.get("/signups")
def get_signups():
    with Session(engine) as session:
        signups = session.exec(select(Signup)).all()
        return signups

# GET request to the root path — just confirms the API is running
@app.get("/")
def read_root():
    return {"message": "Loch Haven Lakes API"}

# POST request to /signup — receives name and email, saves to database
@app.post("/signup")
def create_signup(data: SignupBase):
    # Convert the incoming data into a full Signup with id and timestamp
    signup = Signup.model_validate(data.model_dump())
    with Session(engine) as session:
        session.add(signup)      # stage the record to be saved
        session.commit()         # actually write it to the database
        session.refresh(signup)  # reload it from db to get the auto-assigned id
        return signup            # send the saved record back as confirmation