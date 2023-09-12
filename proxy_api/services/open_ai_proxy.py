import os
import openai
import json
from dotenv import load_dotenv
load_dotenv(f'{os.path.dirname(__file__)}/../../.env')

openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

def query_open_ai(patient: dict, entries: list, category: str, role: str):

    if category == 'all':
        category = 'clinical measurements'

    # TODO - actual data restructuring / prompt work here...

    # Commenting out role_map for now as we focus on patient experience only
    #role_map = { 
    #    'nurse': "I am a nurse treating this patient:", 
    #    'patient': "I am this patient:" }
    #if role not in role_map.keys():
    #    role = 'patient'

   # print(entries)

    setup_prompt = """You play the role of a tumor board member and a Precision Medicine expert.
        Read data about the following patient and respond to their questions. 
        Provide references for any clinical advice from well trusted authorities. 
        Explain your answers using simple and concise language."""

    response = openai.ChatCompletion.create(
        engine=openai_deployment_name,
        messages=[
            {"role": "system", "content": setup_prompt},
            {"role": "user", "content": f'this is the patient data: {json.dumps(clean_patient(patient))}'},
            {"role": "user", "content": f'this is the clinical data: {json.dumps(clean_entries(entries))}'},
            {"role": "user", "content": f"""
             As an active participant in a tumor board meeting, try to answer as many of the following questions: 
             What is the patient's medical history, including any comorbidities or previous treatments?
What are the histological and molecular characteristics of the tumor?
What is the stage and grade of the cancer?
Are there any genetic mutations or biomarkers that can guide treatment decisions?
What are the imaging findings, and what do they indicate about the extent of the disease?
What are the potential treatment options, including surgery, radiation, and systemic therapies?
What are the expected outcomes and potential side effects of the proposed treatments?
Are there any ongoing clinical trials that the patient might be eligible for?
What are the patient's preferences and values regarding treatment and quality of life?
Are there any psychosocial or financial considerations that might affect the patient's treatment plan?
What is the recommended follow-up plan to monitor the patient's response to treatment and adjust the treatment plan as necessary?
Are there any multidisciplinary interventions needed, such as input from nutritionists, physical therapists, or social workers?
Are there any ethical considerations or potential conflicts of interest to be aware of?
What is the consensus of the board regarding the best course of action for this patient?
How will the treatment plan be communicated to the patient, and how will their consent be obtained? 
             
             Develop a comprehensive and individualized treatment plan that considers all aspects of the patient's condition and circumstances.
             Format your response as HTML body."""}
        ],
        temperature=0,
        max_tokens=1200,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)

    return response


def try_get_val(input: dict, key: str) -> str:
    try:
        return input[key]
    except:
        return ""


def clean_patient(input: dict) -> dict:
    clean_patient = {
        "name": f"{try_get_val(input['name'][0], 'given')[0]} {try_get_val(input['name'][0], 'family')}",
        "gender": try_get_val(input, 'gender'),
        "birthDate": try_get_val(input,'birthDate'),
        "address": f"{try_get_val(input['address'][0], 'line')[0]}, {try_get_val(input['address'][0], 'city')}, {try_get_val(input['address'][0], 'state')}, {try_get_val(input['address'][0], 'postalCode')}, {try_get_val(input['address'][0], 'country')}",
        "maritalStatus": try_get_val(try_get_val(input, 'maritalStatus'), 'text')
    }
    return clean_patient


def clean_entries(entries: list):
    for entry in entries:
        entry.pop('fullUrl', None)
        entry.pop('search', None)
        entry['resource'].pop('meta', None)
        entry['resource'].pop('subject', None)
        entry['resource'].pop('id', None)
        entry['resource'].pop('context', None)
        entry['resource'].pop('reasonReference', None)
        entry['resource'].pop('medicationReference', None)
        if entry['resource']['resourceType'] == 'CommunicationRequest' or \
            entry['resource']['resourceType'] == 'Encounter' or \
            entry['resource']['resourceType'] == 'Questionnaire' or \
            entry['resource']['resourceType'] == 'QuestionnaireResponse':
            entry = {}
    
    return entries
