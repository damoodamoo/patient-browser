import os
import openai
import json
import tiktoken
import yaml
from langchain.llms import AzureOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv(f'{os.path.dirname(__file__)}/../../.env')

openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

#Load json data from file
prompt_messages = json.load(open(os.getenv("PROMPT"), 'r'))
#Convert every element in the list to a tuple
prompt_messages = [(x[0], x[1]) for x in prompt_messages]

#print (prompt_messages)
'''
prompt_messages = [
        ("system", "You are a knowledgeable medical doctor."),
        ("system", "I am this patient:"),
        ("system", "{patient_yaml}"),
        ("system", "And these are my clinical measurements in FHIR format:"),
        ("system", "{entries_yaml}"), 
        ("system", "write me a short summary of my {category} that a child would understand, highlighting any areas that need attention"),
        ("system", "In a separate section that should start with word ANOMALIES: indicate any health anomalies."),
        ]
'''

def query_open_ai(patient: dict, entries: list, category: str, return_input: bool = False):

    #Open text file for appending
    #data_file = open("openai_data.txt", "a")

    if category == 'all':
        category = 'clinical measurements'

    # TODO - actual data restructuring / prompt work here...
    patient_json = json.dumps(patient)
    patient_yaml = yaml.dump(patient)
    entries_json = json.dumps(entries)
    entries_yaml = yaml.dump(entries)

    # Write the data to the file
    #data_file.write(f'patientjson: {patient_json}\n')
    #data_file.write(f'entriesjson: {entries_json}\n')

    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    patient_json_encode = encoding.encode(patient_json)
    entries_json_encode = encoding.encode(entries_json)
    patient_yaml_encode = encoding.encode(patient_yaml)
    entries_yaml_encode = encoding.encode(entries_yaml)
    # Get the optimized data with corrections for observation data extraction
    #optimized_entries_data = optimize_json({ "patient" : json.loads(patient_json), "entries" : json.loads(entries_json)})
    #optimized_patient_json = json.dumps(optimized_entries_data["patient"])
    #optimized_entries_json = json.dumps(optimized_entries_data["entries"])
    #optimized_entries_yaml = yaml.dump(optimized_entries_data)
    #optimized_patient_json_encode = encoding.encode(optimized_patient_json)
    #optimized_entries_json_encode = encoding.encode(optimized_entries_json)
    #optimized_entries_yaml_encode = encoding.encode(optimized_entries_yaml)

    print(f'patientjsonencode: {len(patient_json_encode)}')
    print(f'entriesjsonencode: {len(entries_json_encode)}')
    print(f'patientyamlencode: {len(patient_yaml_encode)}')
    print(f'entriesyamlencode: {len(entries_yaml_encode)}')
    #print(f'optimizedpatientjsonencode: {len(optimized_patient_json_encode)}')
    #print(f'optimizedentriesjsonencode: {len(optimized_entries_json_encode)}')

    # If patientyamlencode + entriesyamlencode > 13000, cut it down to 13000
    if len(patient_yaml_encode) + len(entries_yaml_encode) > 13000:
        entries_yaml_encode = entries_yaml_encode[:13000-len(patient_yaml_encode)]
        entries_yaml = encoding.decode(entries_yaml_encode)

    template = ChatPromptTemplate.from_messages(messages = prompt_messages)
    
    messages = template.format_messages(
            patient_yaml=patient_yaml,
            entries_yaml=entries_yaml,
            category=category
    )

    '''
    query_messages = [
            {"role": "system", "content": "You are a knowledgeable medical doctor."},
            {"role": "system", "content": "I am this patient:"},
            {"role": "system", "content": patient_yaml}, # optimized_patient_json - worse results
            {"role": "system", "content": "And these are my clinical measurements in FHIR format:"},
            {"role": "system", "content": entries_yaml}, # optimized_entries_json - worse results
            {"role": "system", "content": f'write me a short summary of my {category} that a child would understand, highlighting any areas that need attention'},
            {"role": "system", "content": "In a separate section that should start with word ANOMALIES: indicate any health anomalies."},]
    '''

    # Write query data to file
    #data_file.write(f'querymessages: {query_messages}\n')

    '''
    llm = AzureOpenAI(deployment_name=os.getenv("OPENAI_DEPLOYMENT_NAME"),
                      model_name="gpt-35-turbo-16k", 
                      max_tokens=1200,
                      openai_api_base=os.getenv("OPENAI_API_BASE"),
                      openai_api_key=os.getenv("OPENAI_API_KEY"),
                      openai_api_type="azure",
                      openai_api_version="2023-03-15-preview",
                      temperature=0,
                      top_p=0.95,
                      frequency_penalty=0,
                      presence_penalty=0,)
    '''
    llm = ChatOpenAI(max_tokens=1200,
                     engine=openai_deployment_name,
                     openai_api_base=os.getenv("OPENAI_API_BASE"),
                     openai_api_key=os.getenv("OPENAI_API_KEY"),
                     temperature=0,)
    
    response = llm(messages=messages)
    
    '''
    response = openai.ChatCompletion.create(
        engine=openai_deployment_name,
        messages=query_messages,
        temperature=0,
        max_tokens=1200,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    '''

    #Write response to file
    #data_file.write(f'response: {response}\n')

    if return_input:
        return response, messages
    else:
        return response
