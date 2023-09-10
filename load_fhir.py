import json
from proxy_api.services.open_ai_proxy import query_open_ai
from evaluate import evaluate_summary

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

def process_fhir(file_name, print_output=False):
    print(f'Processing {file_name}')
    resources = load_fhir(file_name)
    responses = []
    if print_output:
        output_file_name = file_name.replace('.json', '_output.txt')
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
        eval_result = evaluate_summary(json.dumps(resources[key]), response)
        if data_file:
            data_file.write(f'{key}_evaluate: {eval_result}\n')
    if data_file:
        data_file.close()
    return responses

# Function that takes all JSON files in input directory and processes them
def process_fhir_directory(input_directory, print_output=False):
    import os
    for file in os.listdir(input_directory):
        if file.endswith(".json"):
            process_fhir(os.path.join(input_directory, file), print_output)

if __name__ == '__main__':
    # Process directory specified as input to the script
    import sys
    if len(sys.argv) > 1:
        process_fhir_directory(sys.argv[1], True)
    else:
        process_fhir_directory('temp', True)