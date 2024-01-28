import requests
from rdflib import Graph

class RDFHandler:
    def __init__(self, fuseki_base_url):
        self.fuseki_base_url = fuseki_base_url
        self.query_endpoint = f"{fuseki_base_url}/webproject/query"
        self.update_endpoint = f"{fuseki_base_url}/webproject/update"
        self.graph_store_endpoint = f"{fuseki_base_url}/webproject/data"

    def query_data_from_server(self, query):
        """
        Execute a SPARQL query against the Apache Jena Fuseki server.
        """
        response = requests.post(self.query_endpoint,
                                 data={"query": query},
                                 headers={"Accept": "application/sparql-results+json"})
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def upload_data_to_server(self, data, graph_uri):
        """
        Upload RDF data to the Apache Jena Fuseki server.
        """
        post_url = f"{self.graph_store_endpoint}?graph={graph_uri}"
        headers = {"Content-Type": "text/turtle"}
        response = requests.post(post_url, data=data, headers=headers)
        if response.status_code not in [200, 201]:
            response.raise_for_status()

    def serialize_rdf(self, graph):
        return graph.serialize(format="turtle")

    def deserialize_rdf(self, data):
        graph = Graph()
        graph.parse(data=data, format="turtle")
        return graph

    def update_data_on_server(self, update_query):
        """
        Execute a SPARQL UPDATE query against the Apache Jena Fuseki server.
        """
        response = requests.post(self.update_endpoint,
                                 data={"update": update_query},
                                 headers={"Content-Type": "application/sparql-update"})
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def delete_graph(self, graph_uri):
        """
        Delete a specific graph from the Apache Jena Fuseki server.
        """
        response = requests.delete(f"{self.graph_store_endpoint}?graph={graph_uri}")
        if response.ok:
            return "Graph deleted successfully."
        else:
            response.raise_for_status()

# Example Usage
# if __name__ == "__main__":
#     handler = RDFHandler("http://localhost:3030")

    # Example SPARQL Update Query
    # update_query = """
    # INSERT DATA { <http://example.org/subject> <http://example.org/predicate> "object" }
    # """
    # handler.update_data_on_server(update_query)

    # Example Delete Graph
    # handler.delete_graph("http://example.org/graph")