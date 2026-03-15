from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from models import (
    Signup, SignupBase,
    IncidentLitter, IncidentLitterCreate,
    IncidentWildlife, IncidentWildlifeCreate,
    IncidentWaterQuality, IncidentWaterQualityCreate,
)
from database import create_db, engine
from datetime import datetime
import httpx
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

# Create the FastAPI app instance
app = FastAPI()

# CORS middleware allows the frontend (a different origin/port) to talk to this API
# Without this, browsers block requests from lochhavenlakes.org to our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lochhavenlakes.org", "http://localhost:4321"],
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

# POST /upload-photo — uploads image to Supabase Storage, returns public URL
@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...)):
    contents = await file.read()
    filename = f"{datetime.utcnow().timestamp()}-{file.filename}"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/incident-photos/{filename}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": file.content_type,
            },
            content=contents,
        )
    if response.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/incident-photos/{filename}"
        return {"url": public_url}
    return {"error": "Upload failed"}

# POST /report/litter
@app.post("/report/litter")
def create_litter_report(data: IncidentLitterCreate):
    incident = IncidentLitter.model_validate(data.model_dump())
    with Session(engine) as session:
        session.add(incident)
        session.commit()
        session.refresh(incident)
        return incident

# POST /report/wildlife
@app.post("/report/wildlife")
def create_wildlife_report(data: IncidentWildlifeCreate):
    incident = IncidentWildlife.model_validate(data.model_dump())
    with Session(engine) as session:
        session.add(incident)
        session.commit()
        session.refresh(incident)
        return incident

# POST /report/water-quality
@app.post("/report/water-quality")
def create_water_quality_report(data: IncidentWaterQualityCreate):
    incident = IncidentWaterQuality.model_validate(data.model_dump())
    with Session(engine) as session:
        session.add(incident)
        session.commit()
        session.refresh(incident)
        return incident

# GET /reports — returns all published incidents across all types
@app.get("/reports")
def get_reports():
    with Session(engine) as session:
        litter = session.exec(select(IncidentLitter).where(IncidentLitter.status == "published")).all()
        wildlife = session.exec(select(IncidentWildlife).where(IncidentWildlife.status == "published")).all()
        water = session.exec(select(IncidentWaterQuality).where(IncidentWaterQuality.status == "published")).all()
        return {"litter": litter, "wildlife": wildlife, "water_quality": water}

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