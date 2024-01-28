"""
jsonld_parser.py

This script parse all the jsonld data on the website coopcycle.com.
for every delivery services, restaurants and theirs offers.
"""

import os
import sys
import json
import requests
import re
from bs4 import BeautifulSoup
from rdflib import Graph

"""
FUNCTIONS TO SAVE JSON
"""
def save_json(output_file, jsonld_data):
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    with open(output_file, 'w+', encoding='utf-8') as jsonld_file:
        json.dump(jsonld_data, jsonld_file, indent=2)


"""
FUNCTIONS TO SCRAPE DATA FROM WEBSITE
"""
def scrape_json_coopcycle_services(url = "https://coopcycle.org/coopcycle.json"):
    """
    Download and save coopcycle.json containing all delivery services.
    """
    # Download the JSON content from the URL
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}", file=sys.stderr)


def scrape_jsonld(url):
    """
    Scrape JSON-LD data from a given URL.

    Args:
        url (str): The URL to fetch JSON-LD data from.

    Returns:
        list: A list of dictionaries representing JSON-LD data found on the page.
             Each dictionary corresponds to a JSON-LD script tag.

    Raises:
        requests.exceptions.RequestException: If there is an error making the HTTP request.
    """
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad requests

        # Scrape the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all script tags containing JSON-LD data
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})

        # Extract and scrape each JSON-LD script
        json_ld_data = []
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON-LD data: {e}")
        return json_ld_data

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}")
        return None


def scrape_html(url):
    """
    Scrape HTML code by 'id' element
    Returns:
        str: HTML content
    """
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad requests

        return response.text

    except requests.exceptions.RequestException as e:
        print(f"Error making the request: {e}", file=sys.stderr)
        return None


"""
FUNCTIONS TO EXTRACT DATA
"""
def extract_coopcycle_service_urls(field="coopcycle_url"):
    """
    Extract coopcycle_url of each service from coopcycle.json

    Returns:
        list: List of service coopcycle_url .
    """
    # Read the contents of the file
    with open('data/coopcycle.json', 'r', encoding='utf-8') as file:
        json_data = file.read()

    try:
        # Extract the JSON string into a list of dictionaries
        json_data_list = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
        return []

    coopcycle_urls = [entry.get(field) for entry in json_data_list]
    return [url for url in coopcycle_urls if url is not None]


def extract_restaurant_urls(url):
    """
    Extract restaurant urls from {service}.coopcycle.org/en/shops

    Args:
        url: the restaurant url
        id: HTML fragment id in which to look for data

    Returns: list of restaurant urls
    """
    restaurant_urls = []

    # Scrape the list of shops
    html_raw = scrape_html(url)
    soup = BeautifulSoup(html_raw, 'html.parser')

    # Find html with id="shop-list"
    shop_list_html = soup.find(id='shops-list')
    if shop_list_html:
        # Find all <a> tags within the container
        url_elements = soup.find_all('a', href=True)

        # Extract the href attribute from each <a> tag
        for url in url_elements:
            href = url.get('href', '')
            # Check if the url starts with "/en/restaurant/"
            if href.startswith('/en/restaurant/'):
                restaurant_urls.append(href)
    return restaurant_urls


def extract_offer_jsonld(restaurant_url: str):
    """
    Scrape HTML content, extract menu items, returning in a schema.org description in JSON-LD.

    Parameters:
    - url (str): The base URL of the website.
    - id (str): The ID fragment of the offer page.

    Returns:
    - dict: A dictionary containing menu data in JSON-LD format.
    """

    html_raw = scrape_html(restaurant_url)

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_raw, 'html.parser')

    html_code = soup.find(id='menu')
    if not html_code:
        return {}

    restaurant_data = {
        "@context": "http://schema.org",
        "@id": restaurant_url,
        "hasMenu": ""  # Linking the menu to the restaurant
    }

    # Use regular expression to extract the service name and restaurant ID
    match = re.search(r'https?://(.+?\.coopcycle\.org)/.*?/(\d+)(?:-[^/]+)?/?$', restaurant_url)
    if match:
        service_domain = match.group(1)
        restaurant_id = match.group(2)
        restaurant_data['@id'] = f"https://{service_domain}/api/restaurants/{restaurant_id}"

    # Create a dictionary to store menu data
    menu_data = {
        "@context": "http://schema.org",
        "@type": "Menu",
        "@id": f"{restaurant_url}#menu",  # Unique identifier for the menu
        "hasMenuSection": []
    }

    # Extract menu sections
    menu_sections = soup.find_all('div', class_='restaurant-menu-section')
    for menu_section in menu_sections:
        # Get the menu section name (h2 title just before the section)
        section_name = menu_section.find_previous('h2').text.strip()

        # Create a dictionary for menu section
        section_data = {
            "@context": "http://schema.org",
            "@type": "MenuSection",
            "name": section_name,
            "hasMenuItem": []
        }

        # Extract items in the section
        section_items = menu_section.find_all('div', class_='restaurant-menu-section-item')
        for menu_item in section_items:
            # Store variables for item data
            item_name = menu_item.find('h5', class_='menu-item-name')
            item_description = menu_item.find('small', class_='menu-item-description')
            item_price = menu_item.find('span', class_='menu-item-price')
            item_image = menu_item.find('img')
            item_allergens = menu_item.find('small', class_='menu-item-allergens')

            # Create a dictionary for item data
            item_data = {
                "@context": "http://schema.org",
                "@type": "MenuItem",
                "name": item_name.text.strip() if item_name else None,
                "description": item_description.text.strip() if item_description else None,
                "offers": {
                    "@type": "Offer",
                    "price": item_price.text.strip() if item_price else None,
                },
                "image": item_image['src'] if item_image else None,
            }

            # Add allergens if present
            if item_allergens:
                item_data['nutrition'] = item_allergens.find('span').text.strip().split(', ')

            # Add the item to the section
            section_data['hasMenuItem'].append(item_data)

        # Add the section to the menu
        menu_data['hasMenuSection'].append(section_data)

    restaurant_data["hasMenu"] = {"@id": f"{restaurant_url}#menu"}

    return [
        restaurant_data,
        menu_data
    ]


"""
FUNCTIONS TO RETRIEVE DATA
"""
def get_restaurant_jsonld():
    # Retrieve the list of coopcycle services.
    service_urls = extract_coopcycle_service_urls()

    # Looking at {service}.coopcycle.org/en/shops
    for i, service_url in enumerate(service_urls):
        service = service_url.split("://")[1].split(".coopcycle.org")[0]

        # Get the restaurant list
        restaurant_urls = extract_restaurant_urls(service_url + '/en/shops')
        if not restaurant_urls:
            print(f"{i:<6}{service_url:<90}Cannot find shops-list", file=sys.stderr)
            continue

        for restaurant_url in restaurant_urls:
            # Extract the 'id' and 'name'
            restaurant_id, restaurant_name = restaurant_url.split("/")[3].split("-", 1)

            # Get the restaurant
            restaurant_jsonld = scrape_jsonld(service_url + restaurant_url)
            if not restaurant_jsonld:
                print(f"{i:<3}{restaurant_id:<3}{service_url + restaurant_url:<90}Cannot find JSON-LD", file=sys.stderr)
                continue
            
            # Correct the data received
            for restaurant in restaurant_jsonld:
                # Correct restaurant @id, sameAs
                restaurant["@id"] = service_url + restaurant["@id"]
                restaurant["sameAs"] = {"@id": service_url + restaurant_url,
                                        "sameAs": restaurant["@id"]}
                restaurant["url"] = service_url + restaurant_url
                # Correct restaurant adress @context
                restaurant["address"]["@context"] = service_url
            # Add service reference
            restaurant_jsonld.append({"@id": service_url, "areaServed": {"@id": service_url + restaurant_url}})

            output_file = f'data/jsonld/restaurant/{i}-{service}/{restaurant_id}-{restaurant_name}.json'
            save_json(output_file, restaurant_jsonld)
            print(f"{i:<3}{restaurant_id:<3}{service_url + restaurant_url:<90}JSON-LD written into {output_file}")


def get_offer_jsonld():
    # Retrieve the list of coopcycle services.
    coopcycle_urls = extract_coopcycle_service_urls()
    # Looking at {service}.coopcycle.org/en/shops
    for i, url in enumerate(coopcycle_urls):
        service = url.split("://")[1].split(".coopcycle.org")[0]
        # Get the restaurant list
        restaurant_urls = extract_restaurant_urls(url + '/en/shops')
        if not restaurant_urls:
            print(f"{i:<6}{url:<90} Cannot find shops-list", file=sys.stderr)
            continue

        # Looking at /restaurant/{id}-[name}
        for restaurant_url in restaurant_urls:
            # Extract the 'id' and 'name'
            restaurant_id, restaurant_name = restaurant_url.split("/")[3].split("-", 1)

            # Get the offer
            jsonld_offer = extract_offer_jsonld(url + restaurant_url)
            if not jsonld_offer:
                print(
                    f"{i:<3}{restaurant_id:<3}{url + restaurant_url:<90} Cannot find offer 'menu' for {restaurant_name}",
                    file=sys.stderr)
                continue

            output_file = f'data/jsonld/offer/{i}-{service}/{restaurant_id}-{restaurant_name}.json'
            save_json(output_file, jsonld_offer)
            print(f"{i:<3}{restaurant_id:<3}{url + restaurant_url:<90} JSON-LD written into {output_file}")


def get_service_jsonld():
    # Save the coopcycle.json file
    filename = 'data/coopcycle.json'
    coopcycle_data = scrape_json_coopcycle_services()
    save_json(filename, coopcycle_data)

    # Read the coopcycle.json file
    with open(filename,'r', encoding='utf-8') as file:
        json_data = json.load(file)

    for i, service in enumerate(json_data):
        jsonld_data = []

        # Detect a CoopCycle URL in any item of the JSON
        detected_coopcycle_url = None
        for key, value in service.items():
            if isinstance(value, str) and "coopcycle.org" in value:
                detected_coopcycle_url = value
                break

        # Generate the URL based on the detected CoopCycle URL
        if detected_coopcycle_url:
            item_url = detected_coopcycle_url.split("/", 3)[0] + "//" + detected_coopcycle_url.split("/", 3)[2]
            item_coopcycle_url = item_url
        else:
            continue

        item = {
            "@context": "http://schema.org/",
            "@id": item_coopcycle_url,
            "@type": "Service",
            "name": service.get("name", None),
            "provider": {
                "@type": "Organization",
                "name": "CoopCycle"
            },
            "serviceType": "DeliveryService",
            "areaServed": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": service.get("city", None),
                    "addressCountry": service.get("country", None)
                }
            },
            "sameAs": [url for url in [
                item_coopcycle_url if item_url != item_coopcycle_url else None,
                service.get("facebook_url", None),
                service.get("twitter_url", None),
                service.get("instagram_url", None)
            ] if url is not None],
            "url": item_url,  # Use the generated URL as "url"
            "description": [
                {
                    "@type": "Text",
                    "@value": service.get("text", {}).get(lang, None),
                    "@language": lang
                }
                for lang in service.get("text", {})
            ],
        }

        if "latitude" in service and "longitude" in service:
            item["areaServed"]["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": service.get("latitude", None),
                "longitude": service.get("longitude", None)
            }

        jsonld_data.append(item)

        # Save the JSON-LD data to individual files
        service_name = item_coopcycle_url.split("://")[1].split(".coopcycle.org")[0]
        output_file = f'data/jsonld/service/{i}-{service_name}.json'
        save_json(output_file, jsonld_data)
        print(f"{i:<6}{item_coopcycle_url:90}JSON-LD written into {output_file}")



#Uncomment to run the script as a standalone program

# """
# MAIN SCRIPT
# """
# if __name__ == "__main__":
#     # get_service_jsonld()
#     get_restaurant_jsonld()
#     # get_offer_jsonld()