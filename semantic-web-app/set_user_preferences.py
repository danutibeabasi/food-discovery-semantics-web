import requests
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, Namespace


def publish_to_fuseki(graph, fuseki_endpoint):
    """
    Publish an RDF graph to an Apache Jena Fuseki server.
    """
    headers = {'Content-Type': 'text/turtle'}
    data = graph.serialize(format='turtle')
    response = requests.post(fuseki_endpoint, headers=headers, data=data)

    if response.status_code in [200, 201]:
        print("Graph successfully published to Apache Jena Fuseki.")
    else:
        print(f"Failed to publish graph: {response.status_code} {response.reason}")



def set_user_preferences():
    # Namespaces
    SCHEMA = Namespace("http://schema.org/")

    # Create a new RDF graph
    graph = Graph()

    # Create a URI for the user
    user_uri = URIRef("#me")

    # Add user to the graph
    graph.add((user_uri, RDF.type, SCHEMA.Person))

    # Ask user for their name
    name = input("What is your name? ")
    graph.add((user_uri, SCHEMA.name, Literal(name)))

    # Ask for address details
    postal_code = input("What is your postal code? ")
    address_locality = input("What is your locality? ")
    address = URIRef("#address")
    graph.add((address, RDF.type, SCHEMA.PostalAddress))
    graph.add((address, SCHEMA.postalCode, Literal(postal_code)))
    graph.add((address, SCHEMA.addressLocality, Literal(address_locality)))
    graph.add((user_uri, SCHEMA.address, address))

    # Ask for food preferences
    max_price = input("What is the maximum price you are willing to pay (in EUR)? ")
    seeks = URIRef("#seeks")
    graph.add((seeks, RDF.type, SCHEMA.Demand))
    graph.add((seeks, SCHEMA.priceSpecification, Literal(max_price)))

    # Ask for location preference
    longitude = input("What is your longitude? ")
    latitude = input("What is your latitude? ")
    geo_midpoint = URIRef("#geoMidpoint")
    graph.add((geo_midpoint, RDF.type, SCHEMA.GeoCoordinates))
    graph.add((geo_midpoint, SCHEMA.longitude, Literal(longitude, datatype=SCHEMA.Float)))
    graph.add((geo_midpoint, SCHEMA.latitude, Literal(latitude, datatype=SCHEMA.Float)))
    graph.add((seeks, SCHEMA.availableAtOrFrom, geo_midpoint))

    # Print out the RDF graph in Turtle format
    print(graph.serialize(format="turtle"))

    # Save to a file
    with open("user_preferences.ttl", "w") as f:  
        f.write(graph.serialize(format="turtle"))

    # Publish to a Linked Data Platform
    fuseki_endpoint = "http://localhost:3030/webproject/data"  
    publish_to_fuseki(graph, fuseki_endpoint)
    

    
    
    
    
    



