import argparse
from rdf_handler import RDFHandler
from sparql_queries import SPARQLQueries
from shacl_validation import validate_rdf_data
from set_user_preferences import set_user_preferences
from jsonld_to_rdf_converter import process_jsonld_folders
from jsonld_parser import get_service_jsonld, get_restaurant_jsonld, get_offer_jsonld
from rdflib import Graph

def main():
    parser = argparse.ArgumentParser(description="Semantic Web Application")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    
    # ------------------------
    # JSON-LD Parsing Section
    # ------------------------

    # Subparser for JSON-LD Parsing
    jsonld_parser = subparsers.add_parser('jsonld', help='Operations related to JSON-LD parsing')
    jsonld_subparsers = jsonld_parser.add_subparsers(dest="jsonld_command", help="JSON-LD parsing operations")

    # Subparser for parsing service data
    parser_service = jsonld_subparsers.add_parser('service', help='Parse JSON-LD data for services')
    parser_service.set_defaults(func=get_service_jsonld)

    # Subparser for parsing restaurant data
    parser_restaurant = jsonld_subparsers.add_parser('restaurant', help='Parse JSON-LD data for restaurants')
    parser_restaurant.set_defaults(func=get_restaurant_jsonld)

    # Subparser for parsing offer data
    parser_offer = jsonld_subparsers.add_parser('offer', help='Parse JSON-LD data for offers')
    parser_offer.set_defaults(func=get_offer_jsonld)


    
    # --------------------------------
    # JSON-LD to RDF Converter Section
    # --------------------------------
    # Subparser for JSON-LD to RDF conversion

    parser_jsonld_to_rdf = subparsers.add_parser('convert_jsonld', help='Convert JSON-LD files to RDF format')
    parser_jsonld_to_rdf.add_argument('--input_folder', type=str, required=True, help='Input folder containing JSON-LD files')

    
    
    


    # ------------------------
    # RDF Data Section
    # ------------------------
    
    # RDF Data Section
    rdf_parser = subparsers.add_parser('rdf', help='Operations related to RDF data handling')
    rdf_subparsers = rdf_parser.add_subparsers(dest="rdf_command", help="RDF operations")

    # Ensure each subparser is defined once and uniquely
    parser_query = rdf_subparsers.add_parser('query', help='Query RDF data')
    parser_query.add_argument('--query', type=str, required=True, help='SPARQL query string')

    parser_upload = rdf_subparsers.add_parser('upload', help='Upload RDF data')
    parser_upload.add_argument('--file', type=str, required=True, help='Path to the RDF file')
    parser_upload.add_argument('--graph_uri', type=str, required=True, help='Graph URI to upload data to')
    parser_upload.add_argument('--shacl', type=str, help='Path to the SHACL shapes file (optional)')

    parser_update = rdf_subparsers.add_parser('update', help='Update RDF data')
    parser_update.add_argument('--update_query', type=str, required=True, help='SPARQL update query string')

    parser_delete = rdf_subparsers.add_parser('delete', help='Delete a graph')
    parser_delete.add_argument('--graph_uri', type=str, required=True, help='Graph URI to delete')

   
    # ------------------------
    # User Preferences Section
    # ------------------------

    # Subparser for user preferences
    user_pref_parser = subparsers.add_parser('set_preferences', help='Set user preferences')
    user_pref_parser.set_defaults(func=set_user_preferences)

    


    # ------------------------
    # SPARQL Queries Section
    # ------------------------
    # Subparser for SPARQL query operations
    sparql_parser = subparsers.add_parser('sparql', help='Operations related to SPARQL queries')
    sparql_subparsers = sparql_parser.add_subparsers(dest="sparql_command", help="SPARQL operations")

    # Subparser for fetching restaurant data
    parser_restaurant = sparql_subparsers.add_parser('restaurant', help='Fetch restaurant data')

    # Subparser for fetching restaurants with delivery services
    parser_delivery_services = sparql_subparsers.add_parser('delivery_services', help='Fetch delivery services data')

    # Subparser for fetching specific restaurant data by name
    parser_restaurant_name = sparql_subparsers.add_parser('restaurant_name', help='Fetch data of a specific restaurant by name')
    parser_restaurant_name.add_argument('--name', type=str, required=True, help='Name of the restaurant to query')

    parser_by_day_time = sparql_subparsers.add_parser('open_by_day_time', help='Fetch restaurants open on a specific day and time')
    parser_by_day_time.add_argument('--day', type=str, required=True, help='Day of the week')
    parser_by_day_time.add_argument('--open_time', type=str, required=True, help='Opening time (HH:MM)')
    parser_by_day_time.add_argument('--close_time', type=str, required=True, help='Closing time (HH:MM)')

    parser_in_area = sparql_subparsers.add_parser('in_area', help='Fetch restaurants in a specific geographical area')
    parser_in_area.add_argument('--central_lat', type=float, required=True, help='Central latitude of the area')
    parser_in_area.add_argument('--central_long', type=float, required=True, help='Central longitude of the area')
    parser_in_area.add_argument('--lat_range', type=float, required=True, help='Latitude range around the central point')
    parser_in_area.add_argument('--long_range', type=float, required=True, help='Longitude range around the central point')

    

    # Subparser for fetching restaurants with menu items within a specific price range
    parser_price_range = sparql_subparsers.add_parser('price_range', help='Fetch restaurants with menu items within a specific price range')
    parser_price_range.add_argument('--max_price', type=float, required=True, help='Maximum price for menu items')


    # Subparser for fetching restaurants based on combined user preferences
    parser_combined_prefs = sparql_subparsers.add_parser('combined_prefs', help='Fetch restaurants based on combined user preferences')
    parser_combined_prefs.add_argument('--user_prefs_uri', type=str, required=True, help='URI of the user preferences graph')

   
    args = parser.parse_args()
    

   
    if hasattr(args, 'func'):
        args.func()
    elif args.command == 'rdf':
        handler = RDFHandler("http://localhost:3030")

        # Handling 'query', 'upload', 'update', 'delete' subcommands
        if args.rdf_command == 'query':
            result = handler.query_data_from_server(args.query)
            print(result)
        elif args.rdf_command == 'upload':
            rdf_data = Graph()
            rdf_data.parse(args.file, format="turtle")

            # Perform SHACL validation if provided
            if args.shacl:
                with open(args.shacl, 'r') as shacl_file:
                    shacl_shapes = shacl_file.read()
                conforms, report = validate_rdf_data(rdf_data, shacl_shapes)
                if not conforms:
                    print("RDF data does not conform to SHACL shapes. Validation report:")
                    print(report)
                    return
                else:
                    print("RDF data conforms to SHACL shapes.")

            handler.upload_data_to_server(rdf_data.serialize(format="turtle"), args.graph_uri)
            print(f"Data uploaded successfully to {args.graph_uri}")
        elif args.rdf_command == 'update':
            handler.update_data_on_server(args.update_query)
            print("Data updated successfully.")
        elif args.rdf_command == 'delete':
            handler.delete_graph(args.graph_uri)
            print(f"Graph {args.graph_uri} deleted successfully.")
        else:
            rdf_parser.print_help()

    # SPARQLQueries instance
    elif args.command == 'sparql':
        sparql_queries = SPARQLQueries("http://localhost:3030/webproject/query")

        if args.sparql_command == 'restaurant':
            restaurant_data = sparql_queries.get_restaurant_data()
            for restaurant in restaurant_data:
                print(restaurant)
        elif args.sparql_command == 'restaurant_name':
            restaurant_data = sparql_queries.get_restaurant_data_by_name(args.name)
            for restaurant in restaurant_data:
                print(restaurant)
        elif args.sparql_command == 'open_by_day_time':
            data = sparql_queries.get_restaurants_by_day_and_time(args.day, args.open_time, args.close_time)
            for entry in data:
                print(entry)
        elif args.sparql_command == 'in_area':
            area_data = sparql_queries.get_restaurants_in_area(args.central_lat, args.central_long, args.lat_range, args.long_range)
            for entry in area_data:
                print(entry)
        elif args.sparql_command == 'price_range':
            price_range_data = sparql_queries.get_restaurants_by_price_range(args.max_price)
            for entry in price_range_data:
                print(entry)
        elif args.sparql_command == 'delivery_services':
            delivery_services_data = sparql_queries.get_delivery_services()
            for result in delivery_services_data:
                print(result)
        elif args.sparql_command == 'combined_prefs':
            combined_prefs_data = sparql_queries.query_restaurants_based_on_combined_preferences(args.user_prefs_uri)
            for entry in combined_prefs_data:
                print(entry)

        else:
            sparql_parser.print_help()

    elif args.command == 'convert_jsonld':
        process_jsonld_folders(args.input_folder)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()