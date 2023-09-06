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

def process_fhir(file_name, output_file_name=None):
    resources = load_fhir(file_name)
    responses = []
    if output_file_name:
        data_file = open(output_file_name, "w")
    else:
        data_file = None
    if data_file:
        data_file.write(f'patient_resources: {resources["Patient"]}\n')
    for key in resources.keys():
        if key != 'Patient':
            if data_file:
                data_file.write(f'{key}_resources: {resources[key]}\n')
        response = query_open_ai(resources["Patient"][0], resources[key], key)
        responses.append(response)
        if data_file:
            data_file.write(f'{key}_response: {response}\n')
    if data_file:
        data_file.close()
    return responses

if __name__ == '__main__':
    process_fhir('temp/Arline53_Rohan584_436a7fef-6640-96ab-2557-77e40e947bc9.json', 'fhir_data.txt')