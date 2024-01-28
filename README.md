
# Semantic Web Application

This Semantic Web Application is designed to interact with an RDF database, execute SPARQL queries, and manage user preferences. It utilizes Apache Jena Fuseki as the RDF database backend.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed
- Apache Jena Fuseki server running and accessible
- Required Python libraries installed (rdflib, SPARQLWrapper, requests)

## Installation

Clone the repository to your local machine:

```sh
git clone https://gitlab.emse.fr/minh-hoang.huynh/semantic-web-project.git
cd semantic-web-app
```

Install the necessary Python dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

1. **Apache Jena Fuseki Setup**: 
   Ensure that your Apache Jena Fuseki server is up and running. The default endpoint for the application is set to `http://localhost:3030/`. If your server is running on a different endpoint, you'll need to adjust the application configuration accordingly.

   The application is designed to work with the following available services on the Apache Jena Fuseki server:

   - Graph Store Protocol (Read): `/webproject/get`
   - Graph Store Protocol: `/webproject/`
   - Graph Store Protocol: `/webproject/data`
   - SPARQL Query: `/webproject/query`
   - SPARQL Query: `/webproject/`
   - SPARQL Query: `/webproject/sparql`
   - SPARQL Update: `/webproject/update`
   - SPARQL Update: `/webproject/`

   These services enable the application to perform a range of operations, including reading from and writing to the RDF store, executing SPARQL queries, and updating RDF data.

2. **Update Configuration (Optional)**: 
   If your Apache Jena Fuseki server uses a different set of endpoints, or if you have customized your Fuseki setup, you may need to update the configuration settings in the application to align with your server's setup. This includes updating the endpoint URLs in the application code where Apache Jena Fuseki server interactions are defined.

## Running the Application

The application is designed to be run via the command line interface (CLI). Below are the primary operations you can perform, along with the necessary commands:


## JSON-LD Parsing Operations

This section of the application is designed to parse JSON-LD data from various sources, particularly focusing on services, restaurants, and their offers. It scrapes and processes data.

### Prerequisites for JSON-LD Parsing

Ensure the following conditions are met before you begin JSON-LD parsing:

- Internet connection to access the specified URLs.
- Correct setup of the base URLs in the `jsonld_parser.py` script.

### JSON-LD Parsing Commands

The application allows for parsing JSON-LD data related to delivery services, restaurants, and offers through specific CLI commands. Below are the commands and their descriptions:

1. **Parse Delivery Services Data**:
   To parse JSON-LD data for all delivery services, use the following command:
   ```sh
   python main.py jsonld service
   ```
   This command scrapes service-related data.

2. **Parse Restaurant Data**:
   For parsing JSON-LD data for restaurants, execute:
   ```sh
   python main.py jsonld restaurant
   ```
   This retrieves restaurant data from specified URLs and processes it.

3. **Parse Offers Data**:
   To parse offers data related to the restaurants, run:
   ```sh
   python main.py jsonld offer
   ```
   This command focuses on scraping and processing offers available at various restaurants.

### Output

The results of JSON-LD parsing are saved in the specified directory structure. The files will be located in `data/ttl/`, categorized into `service/`, `restaurant/`, and `offer/` subfolders.

### Customization

You can modify the base URLs or the scraping logic in the `jsonld_parser.py` file according to your specific requirements or if the structure of the source data changes.


### Convert JSON-LD to RDF

- **Convert JSON-LD Files to RDF**:
  This feature allows you to convert JSON-LD files to RDF (Turtle) format. Provide the path to the folder containing your JSON-LD files.
  ```sh
  python main.py convert_jsonld --input_folder "path/to/jsonld/folder"
  ```
  The command processes all JSON-LD files in the specified folder and converts them to RDF. The converted files will be saved in the same directory structure with a `.ttl` extension.

### RDF Data Operations

These commands interact with the RDF data in your Apache Jena Fuseki server.

- **Query RDF Data**:
  Execute a SPARQL query against the RDF dataset. Replace `"YOUR_SPARQL_QUERY"` with your actual query.
  ```sh
  python main.py rdf query --query "YOUR_SPARQL_QUERY"
  ```

- **Upload RDF Data and Validate with SHACL**:
  Upload RDF data to a specific graph in your RDF store and validate it using SHACL shapes. Replace `"path/to/your/file.ttl"` with the path to your Turtle file, `"http://example.org/your-graph"` with the URI of your target graph, and `"path/to/shacl_shapes.ttl"` with the path to your SHACL shapes file.

  ```sh
  python main.py rdf upload --file path/to/your/file.ttl --graph_uri http://example.org/your-graph --shacl path/to/shacl_shapes.ttl
  ```

- **Update RDF Data**:
  Perform a SPARQL UPDATE on your RDF dataset. Replace `"YOUR_SPARQL_UPDATE_QUERY"` with your SPARQL update command.
  ```sh
  python main.py rdf update --update_query "YOUR_SPARQL_UPDATE_QUERY"
  ```

- **Delete a Graph**:
  Remove an entire graph from the RDF store. Replace `"http://example.org/your-graph"` with the URI of the graph you wish to delete.
  ```sh
  python main.py rdf delete --graph_uri "http://example.org/your-graph"
  ```
### SPARQL Query Operations

This section details commands for interacting with the RDF data via SPARQL queries.

- **Fetch All Restaurant Data**:
  Retrieves a list of all restaurants, including their names and other details.
  ```sh
  python main.py sparql restaurant
  ```

- **Fetch Specific Restaurant by Name**:
  Retrieve detailed information about a specific restaurant, identified by name.
  ```sh
  python main.py sparql restaurant_name --name "Restaurant Name"
  ```

- **Fetch Restaurants Open on Specific Day and Time**:
  Find restaurants that are open at a particular time on a specified day. Replace `Friday`, `09:00`, and `22:00` with your desired day and time range.
  ```sh
  python main.py sparql open_by_day_time --day "Friday" --open_time "09:00" --close_time "22:00"
  ```

- **Fetch Restaurants in a Specific Geographical Area**:
  List restaurants located within a specified geographical area. The `central_lat` and `central_long` represent the center of the area, while `lat_range` and `long_range` define the radius around this point.
  ```sh
  python main.py sparql in_area --central_lat 48.8566 --central_long 2.3522 --lat_range 0.1 --long_range 0.1
  ```

- **Fetch Restaurants by Price Range**:
  Retrieve restaurants offering menu items within a specific price range. The `max_price` parameter determines the upper limit of the price range.
  ```sh
  python main.py sparql price_range --max_price 20.0
  ```

### Fetching Restaurants Based on Combined User Preferences

This feature allows you to query restaurants based on combined user preferences, including location, opening hours, and price range. The user preferences are fetched from an RDF graph stored in the default graph of your Apache Jena Fuseki server.

#### Command Usage

- To fetch restaurants based on combined user preferences, use the following command:
```sh
python main.py sparql combined_prefs --user_prefs_uri "http://localhost:3030/webproject"
```

- This command queries restaurants that match the preferences set by the user, such as location proximity, opening hours, and menu prices.

#### Required Argument

- `--user_prefs_uri`: This argument specifies the URI of your Apache Jena Fuseki server where the user preferences are stored. In this example, it points to the default graph of the Fuseki server (`http://localhost:3030/webproject`). If your user preferences are stored in a different graph or server, update this URI accordingly.

#### Testing with `pref-charpenay.ttl`

- For testing, the `pref-charpenay.ttl` file, containing sample user preference data, is uploaded to the default graph of the Apache Jena Fuseki server. This file includes information such as the user's location coordinates and price preferences.

#### Output

- The command outputs a list of restaurants that match the user's preferences, sorted by their proximity to the user's location. Each entry includes the restaurant's name, distance from the user, opening days, opening and closing times, and menu prices.



### Delivery Service Data Query

- **Fetch Delivery Services Data**:
  This command retrieves information about delivery services, including their names, countries, and localities.
  ```sh
  python main.py sparql delivery_services
  ```

### Setting User Preferences

Use the following command to set user preferences. This feature will prompt you to input various personal preferences, which will then be serialized into RDF format and can be saved locally or published to your Apache Jena Fuseki server.

- **Command to Set User Preferences**:
  ```sh
  python main.py set_preferences
  ```

- **Prompts and Inputs**:
  When you run this command, you will be prompted to enter:
  - Your name (e.g., "John Doe")
  - Your postal code (e.g., "12345")
  - Your locality (e.g., "Springfield")
  - The maximum price you're willing to pay for a service (in EUR, e.g., "20")
  - Your geographical longitude (e.g., "4.567")
  - Your geographical latitude (e.g., "2.56")

  After providing these details, an RDF graph representing your preferences is created.

- **Configuration for Fuseki Server**:
  By default, the application is configured to publish this data to an Apache Jena Fuseki server at the endpoint `http://localhost:3030/webproject/data`. Ensure your Apache Jena Fuseki server is running and accessible at this endpoint. If your server uses a different endpoint, modify the `fuseki_endpoint` variable in the script accordingly.

- **Saving and Publishing**:
  The user preferences RDF graph can be saved as a Turtle file (`user_preferences.ttl`) and/or published directly to the configured Fuseki server. The script will perform these actions based on its current configuration and prompts.

## Contributing

If you wish to contribute to this project, please fork the repository and submit a pull request.

## MIT License

Copyright (c) 2024 Group Semantic Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


