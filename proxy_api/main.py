from fastapi import FastAPI
from services import open_ai_proxy, open_ai_proxy_alerts
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

@app.post("/openai")
def open_ai_alerts(patient_data: FHIRBundle):
    response_alerts, response_medications, response_health_concerns, response_chain_of_thought_alerts_check = open_ai_proxy_alerts.query_open_ai(patient_data.patient, patient_data.entries, patient_data.category, patient_data.role)
    return {"response": response_alerts, "medications": response_medications, "health_conditions":response_health_concerns, "any_alerts_check": response_chain_of_thought_alerts_check}