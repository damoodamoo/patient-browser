import json
#from nltk.corpus import stopwords
#import nltk

# Download NLTK data files (needed for stopwords)
#nltk.download('stopwords')

def clean_text(text):
    """
    Function to clean text by removing stopwords and non-alphanumeric characters.
    """
    if not text:
        return text
    
    stop_words = set() #set(stopwords.words('english'))
    words = text.split()
    clean_words = [word for word in words if word.isalnum() and word.lower() not in stop_words]
    return ' '.join(clean_words)

def extract_medically_important_info(entry):
    """
    Function to extract medically important information from the entry.
    """
    resource_type = entry['resource']['resourceType']
    new_entry = {}
    resource_keys = ['code', "component", "effectiveDateTime", 'onset', "performedPeriod", "reasonReference", 'recordedDate', 'text', 'value', 'valueQuantity']
    if resource_type == 'Patient':
        # Extract patient details
        patient_details = {key: entry['resource'].get(key) for key in ['id', 'gender', 'birthDate', 'name'] if key in entry['resource']}
        new_entry['resource'] = {'resourceType': 'Patient', **patient_details}
    elif resource_type in ['Observation', 'Condition', 'MedicationStatement', 'Procedure']:
        # Extract details for other resource types
        details = {key: entry['resource'].get(key) for key in resource_keys if key in entry['resource']}
        new_entry['resource'] = {'resourceType': resource_type, **details}
    return new_entry

def clean_file(input_file_path, output_file_path):
    # Read the JSON file
    with open(input_file_path, 'r') as file:
        data = json.load(file)
    
    # Extract medically important information
    medically_important_info = [extract_medically_important_info(entry) for entry in data['entry']]
    
    # Update the 'entry' field in the original data
    data['entry'] = medically_important_info
    
    # Write the cleaned data to a new JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(data, output_file, indent=4)

def clean_fhir_directory(input_directory, output_directory=None):
    import os
    if not output_directory:
        output_directory = input_directory
    for file in os.listdir(input_directory):
        if file.endswith(".json"):
            clean_file(os.path.join(input_directory, file), 
                       os.path.join(output_directory, file.replace('.json', '_cleaned.json')))

if __name__ == '__main__':
    clean_fhir_directory('temp', 'temp2')