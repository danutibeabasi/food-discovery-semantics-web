from SPARQLWrapper import SPARQLWrapper, JSON

class SPARQLQueries:
    def __init__(self, sparql_endpoint):
        self.sparql = SPARQLWrapper(sparql_endpoint)

    def execute_query(self, query):
        """
        Execute a given SPARQL query and return the results.
        """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        try:
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_restaurant_data(self):
        """
        Fetches restaurant data including name, images, address, description, and telephone.
        """
        query = """
        PREFIX ns1: <http://schema.org/>

        SELECT ?restaurantName (GROUP_CONCAT(DISTINCT ?image; separator=", ") AS ?images) 
            (GROUP_CONCAT(DISTINCT ?streetAddress; separator=", ") AS ?addresses) 
            ?description ?telephone
        WHERE {
            ?restaurant a ns1:Restaurant ;
                        ns1:name ?restaurantName ;
                        ns1:description ?description ;
                        ns1:image ?image ;
                        ns1:address ?address .

            ?address ns1:streetAddress ?streetAddress ;
                    ns1:telephone ?telephone .
        } 
        GROUP BY ?restaurantName ?description ?telephone
        ORDER BY ?restaurantName
        LIMIT 500
        """
        results = self.execute_query(query)
        return self.format_restaurant_data(results)


    def get_restaurant_data_by_name(self, restaurant_name):
        """
        Fetches data for a specific restaurant by name.

        Args:
            restaurant_name (str): The name of the restaurant.

        Returns:
            list: Formatted data of the specified restaurant.
        """
        query = """
        PREFIX ns1: <http://schema.org/>

        SELECT ?restaurantName (GROUP_CONCAT(DISTINCT ?image; separator=", ") AS ?images) 
            (GROUP_CONCAT(DISTINCT ?streetAddress; separator=", ") AS ?addresses) 
            ?description ?telephone
        WHERE {
            ?restaurant a ns1:Restaurant ;
                        ns1:name ?restaurantName ;
                        ns1:description ?description ;
                        ns1:image ?image ;
                        ns1:address ?address .
            FILTER regex(?restaurantName, "%s", "i")

            ?address ns1:streetAddress ?streetAddress ;
                     ns1:telephone ?telephone .
        } 
        GROUP BY ?restaurantName ?description ?telephone
        ORDER BY ?restaurantName
        LIMIT 500
        """ % restaurant_name.replace('"', '\\"')  # Safeguard against quote characters in names

        results = self.execute_query(query)
        return self.format_restaurant_data(results)


    @staticmethod
    def format_restaurant_data(query_results):
        """
        Formats the raw results from the restaurant data query.
        """
        formatted_results = []
        for result in query_results:
            first_image = result['images']['value'].split(", ")[0] if 'images' in result else ""
            first_address = result['addresses']['value'].split(", ")[0] if 'addresses' in result else ""

            restaurant_data = {
                'name': result['restaurantName']['value'],
                'description': result['description']['value'],
                'image': first_image,
                'address': first_address,
                'telephone': result['telephone']['value']
            }
            formatted_results.append(restaurant_data)
        return formatted_results


    def get_restaurants_by_day_and_time(self, day, open_time, close_time):
        """
        Fetches restaurants open on a specific day within a specified time range.

        Args:
            day (str): The day of the week (e.g., 'Friday').
            open_time (str): Opening time (e.g., '11:30').
            close_time (str): Closing time (e.g., '14:00').

        Returns:
            list: Formatted data of restaurants open at the given day and time range.
        """
        query = f"""
        PREFIX ns1: <http://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?restaurantName ?openDay ?opens ?closes 
        WHERE {{
            ?restaurant a ns1:Restaurant ;
                        ns1:name ?restaurantName ;
                        ns1:openingHoursSpecification ?ohs.

            ?ohs ns1:dayOfWeek ?openDay ;
                 ns1:opens ?opens ;
                 ns1:closes ?closes.

            FILTER (CONTAINS(STR(?openDay), "{day}"))
            FILTER (STR(?opens) <= "{open_time}" && STR(?closes) >= "{close_time}")
        }}
        ORDER BY ?restaurantName
        """
        results = self.execute_query(query)
        return self.format_open_hours_data(results)

    @staticmethod
    def format_open_hours_data(query_results):
        """
        Formats the raw results from the open hours query.
        """
        formatted_results = []
        for result in query_results:
            data = {
                'name': result['restaurantName']['value'],
                'open_day': result['openDay']['value'],
                'opens': result['opens']['value'],
                'closes': result['closes']['value']
            }
            formatted_results.append(data)
        return formatted_results
    

    def get_restaurants_in_area(self, central_lat, central_long, lat_range, long_range):
        """
        Fetches restaurants within a specific geographical area.

        Args:
            central_lat (float): Central latitude of the area.
            central_long (float): Central longitude of the area.
            lat_range (float): Latitude range around the central point.
            long_range (float): Longitude range around the central point.

        Returns:
            list: Formatted data of restaurants within the specified area.
        """
        query = f"""
        PREFIX ns1: <http://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?restaurant ?restaurantName ?latitude ?longitude WHERE {{
          ?restaurant a ns1:Restaurant ;
                      ns1:name ?restaurantName ;
                      ns1:address ?address.

          ?address ns1:geo ?geo.

          ?geo ns1:latitude ?lat ;
               ns1:longitude ?long.

          # Convert latitude and longitude to decimal
          BIND(xsd:decimal(?lat) AS ?latitude)
          BIND(xsd:decimal(?long) AS ?longitude)

          FILTER (
            ?latitude <= (xsd:decimal("{central_lat}") + xsd:decimal("{lat_range}")) &&
            ?latitude >= (xsd:decimal("{central_lat}") - xsd:decimal("{lat_range}")) &&
            ?longitude <= (xsd:decimal("{central_long}") + xsd:decimal("{long_range}")) &&
            ?longitude >= (xsd:decimal("{central_long}") - xsd:decimal("{long_range}"))
          )
        }}
        LIMIT 10
        """
        results = self.execute_query(query)
        return self.format_geographical_data(results)

    @staticmethod
    def format_geographical_data(query_results):
        """
        Formats the raw results from the geographical area query.
        """
        formatted_results = []
        for result in query_results:
            data = {
                'restaurant': result['restaurant']['value'],
                'name': result['restaurantName']['value'],
                'latitude': result['latitude']['value'],
                'longitude': result['longitude']['value']
            }
            formatted_results.append(data)
        return formatted_results
    
    def get_restaurants_by_price_range(self, max_price):
        """
        Fetches restaurants offering menu items below a specified price.

        Args:
            max_price (float): The maximum price for menu items.

        Returns:
            list: Formatted data of restaurants with menu items within the specified price range.
        """
        query = f"""
        PREFIX ns1: <http://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?restaurantName ?menuItemName ?priceLiteral
        WHERE {{
            ?restaurant a ns1:Restaurant ;
                        ns1:name ?restaurantName ;
                        ns1:hasMenu ?menu.

            ?menu ns1:hasMenuSection ?menuSection.

            ?menuSection ns1:hasMenuItem ?menuItem.

            ?menuItem ns1:name ?menuItemName ;
                      ns1:offers/ns1:price ?priceLiteral.

            # Extract the numeric part of the price
            BIND(REPLACE(?priceLiteral, "€", "") AS ?priceNumeric)
            BIND(xsd:decimal(?priceNumeric) AS ?price)

            FILTER (?price <= {max_price})
        }}
        ORDER BY ?restaurantName ?price
        """
        results = self.execute_query(query)
        return self.format_price_range_data(results)

    @staticmethod
    def format_price_range_data(query_results):
        """
        Formats the raw results from the price range query.
        """
        formatted_results = []
        for result in query_results:
            data = {
                'name': result['restaurantName']['value'],
                'menuItem': result['menuItemName']['value'],
                'price': result['priceLiteral']['value']
            }
            formatted_results.append(data)
        return formatted_results
    
    def get_delivery_services(self):
        """Fetch delivery services with their location details."""
        query = """
        PREFIX ns1: <http://schema.org/>

        SELECT DISTINCT ?serviceName ?addressCountry ?addressLocality WHERE {
          ?service a ns1:Service ;
                   ns1:serviceType "DeliveryService" ;
                   ns1:name ?serviceName ;
                   ns1:areaServed/ns1:address [ a ns1:PostalAddress ;
                                                ns1:addressCountry ?addressCountry ;
                                                ns1:addressLocality ?addressLocality ] .
        }
        """
        results = self.execute_query(query)
        return self.format_delivery_service_data(results)
    
    
    @staticmethod
    def format_delivery_service_data(query_results):
        """
        Formats the raw results from the delivery service query.
        """
        formatted_results = []
        for result in query_results:
            service_name = result.get("serviceName", {}).get("value", "Unknown")
            address_country = result.get("addressCountry", {}).get("value", "Not available")
            address_locality = result.get("addressLocality", {}).get("value", "Not available")
            formatted_results.append({
                'service_name': service_name,
                'country': address_country,
                'locality': address_locality
            })
        return formatted_results
    
    def query_restaurants_based_on_combined_preferences(self, user_prefs_uri):
        """
        Fetches restaurants based on combined user preferences including location, time, and price range.

        Args:
            user_prefs_uri (str): The URI of the user preference RDF graph.

        Returns:
            list: Formatted data of restaurants matching the user preferences.
        """
        query = f"""
        PREFIX ns1: <http://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?restaurant ?restaurantName ?distance ?openDay ?opens ?closes ?price
        WHERE {{
            # Fetch user's location and price preferences
            ?user a ns1:Person ;
                  ns1:seeks/ns1:availableAtOrFrom/ns1:geoWithin/ns1:geoMidpoint [ 
                      ns1:latitude ?userLat ;
                      ns1:longitude ?userLong
                  ] ;
                  ns1:seeks/ns1:priceSpecification/ns1:maxPrice ?maxPrice.

            # Fetch restaurant details
            ?restaurant a ns1:Restaurant ;
                        ns1:name ?restaurantName ;
                        ns1:geo [ ns1:latitude ?lat ; ns1:longitude ?long ] ;
                        ns1:openingHoursSpecification ?ohs.
                    
            ?ohs ns1:dayOfWeek ?openDay ;
                 ns1:opens ?opens ;
                 ns1:closes ?closes.

            OPTIONAL {{
                ?restaurant ns1:hasMenu/ns1:hasMenuSection/ns1:hasMenuItem/ns1:offers/ns1:price ?priceLiteral.
                BIND(REPLACE(?priceLiteral, "€", "") AS ?priceNumeric)
                BIND(xsd:decimal(?priceNumeric) AS ?price)
            }}

            # Calculate approximate distance (in degrees)
            BIND(((?lat - ?userLat) * (?lat - ?userLat) + (?long - ?userLong) * (?long - ?userLong)) AS ?distance)

            FILTER ((?distance <= 0.9) || ?price <= ?maxPrice)
        }}
        ORDER BY ?distance ?price
        LIMIT 10
        """
        results = self.execute_query(query)
        return self.format_combined_preferences_data(results)

    @staticmethod
    def format_combined_preferences_data(query_results):
        """
        Formats the raw results from the combined preferences query.
        """
        formatted_results = []
        for result in query_results:
            data = {
                'restaurant': result.get('restaurant', {}).get('value', 'Unknown'),
                'name': result.get('restaurantName', {}).get('value', 'Unknown'),
                'distance': result.get('distance', {}).get('value', 'Unknown'),
                'open_day': result.get('openDay', {}).get('value', 'Unknown'),
                'opens': result.get('opens', {}).get('value', 'Unknown'),
                'closes': result.get('closes', {}).get('value', 'Unknown'),
                'price': result.get('price', {}).get('value', 'Unknown')
            }
            formatted_results.append(data)
        return formatted_results