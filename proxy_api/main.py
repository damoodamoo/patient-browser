from fastapi import FastAPI
from services import open_ai_proxy
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

class FHIRBundle(BaseModel):
    patient: dict = None
    entries: list = None
    category: str = None
    role: str = None
    question: str = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"])

@app.post("/openai")
def open_ai(patient_data: FHIRBundle):
    response = open_ai_proxy.query_open_ai(
        patient_id=patient_data.patient['id'], # IRL -> replace with session id / user id from aad or something
        patient=patient_data.patient, 
        entries=[] if patient_data.entries is None else patient_data.entries, 
        category=patient_data.category,
        role=patient_data.role,
        question=patient_data.question
    )
    return {"response": response}
