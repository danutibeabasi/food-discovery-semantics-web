import os
import json
from rdflib import Graph

def convert_file_jsonld_to_rdf(file_path, output_filename):
    """
    Convert a JSON-LD file to a Turtle file.
    """
    with open(file_path, 'r', encoding='utf-8') as json_file:
        jsonld_data = json.load(json_file)

    g = Graph()
    g.parse(data=json.dumps(jsonld_data), format='json-ld')

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(g.serialize(format='turtle'))



def process_jsonld_folders(base_folder):
    """
    Process all JSON-LD files in a directory and its subdirectories.
    """
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                output_path = file_path.replace('jsonld', 'ttl').replace('.json', '.ttl')
                convert_file_jsonld_to_rdf(file_path, output_path)