import pyshacl
from rdflib import Graph

def validate_rdf_data(rdf_data, shacl_shapes):
    """
    Validate RDF data against SHACL shapes.

    Args:
        rdf_data (Graph): The RDFLib graph object containing RDF data to be validated.
        shacl_shapes (str): SHACL shapes in string format to validate against.

    Returns:
        bool: Indicates if the data conforms to the SHACL shapes.
        str: Validation report.
    """
    try:
        conforms, v_graph, v_text = pyshacl.validate(rdf_data, shacl_graph=shacl_shapes, data_graph_format='turtle', shacl_graph_format='turtle')
        return conforms, v_text
    except Exception as e:
        return False, f"Validation error: {e}"
