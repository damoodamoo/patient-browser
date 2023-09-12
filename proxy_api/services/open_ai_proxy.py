import os
import openai
import json
import tiktoken
import yaml

from dotenv import load_dotenv
load_dotenv(f'{os.path.dirname(__file__)}/../../.env')

openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

chat_history = {}

def query_open_ai(patient_id: str, patient: dict = None, entries: list = [], category: str = None, role: str = None, question: str = None):

    if category == 'all': 
        category = 'clinical measurements'

    if question == None:
        question = 'write me a short summary of this {category} highlighting any areas that need my attention.'

    setup_prompt = """You play the role of a medical doctor. 
        Read data about the following patient and respond to their questions. 
        Provide online references for any clinical advice.
        Give short responses in simple and concise language."""
    
    init_messages = [
            {"role": "system", "content": setup_prompt},
            {"role": "system", "content": f'this is the patient data: {json.dumps(clean_patient(patient))}'},
            {"role": "system", "content": f'this is the clinical data: {json.dumps(clean_entries(entries))}'},
    ]

    # get or create chat history
    buffer = chat_history.get(patient_id, {"chat_memory": init_messages})

    # add user message to chat history
    buffer["chat_memory"].append({"role": "user", "content": f'{question}. Format your response as HTML body'})

    response = openai.ChatCompletion.create(
        engine=openai_deployment_name,
        messages=buffer["chat_memory"],
        temperature=0,
        max_tokens=1200,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
   
    buffer["chat_memory"].append(response.choices[0].message)
    chat_history[patient_id] = buffer

    #print(chat_history)

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
       # "address": f"{try_get_val(input['address'][0], 'line')[0]}, {try_get_val(input['address'][0], 'city')}, {try_get_val(input['address'][0], 'state')}, {try_get_val(input['address'][0], 'postalCode')}, {try_get_val(input['address'][0], 'country')}",
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
            entry['resource']['resourceType'] == 'Procedure' or \
            entry['resource']['resourceType'] == 'Questionnaire' or \
            entry['resource']['resourceType'] == 'QuestionnaireResponse':
            entry = {}
    
    return entries
    if return_input:
        return response, messages
    else:
        return response
