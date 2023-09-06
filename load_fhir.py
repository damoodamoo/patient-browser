import json
from proxy_api.services.open_ai_proxy import query_open_ai

def load_fhir(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)

    # Initializing an empty dictionary to store resources grouped by resourceType
    resources_by_type = {}

    # Looping through each item in data['entry']
    for item in data['entry']:
        if 'resource' in item:
            resource_type = item['resource'].get('resourceType')
            if resource_type:
                if resource_type not in resources_by_type:
                    resources_by_type[resource_type] = []
                resources_by_type[resource_type].append(item['resource'])

    # Returning the dictionary with resources grouped by resourceType
    print(resources_by_type.keys()) # Let's print the keys to confirm the grouping
    return resources_by_type


resources = load_fhir('temp/Arline53_Rohan584_436a7fef-6640-96ab-2557-77e40e947bc9.json')
data_file = open("openai_data.txt", "w")
data_file.write(f'patient_resources: {resources["Patient"]}\n')
for key in resources.keys():
    if key != 'Patient':
        data_file.write(f'{key}_resources: {resources[key]}\n')
    response = query_open_ai(resources["Patient"][0], resources[key], key)
    data_file.write(f'{key}_response: {response}\n')
data_file.close()
