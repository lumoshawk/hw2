import os
import requests
import re
from bs4 import BeautifulSoup
import json
import sys

def search_scientist(name, select_index=None):
    """
    Search for a scientist on DBLP by name
    If select_index is provided, automatically select that scientist
    Returns the author if found, or a list of matching authors if select_index is None
    """
    # Format the search URL
    search_url = f"https://dblp.org/search/author/api?q={name}&format=json"
    
    print(f"Searching for '{name}' on DBLP...")
    response = requests.get(search_url)
    
    if response.status_code != 200:
        print(f"Error: Failed to search DBLP. Status code: {response.status_code}")
        return None
    
    data = response.json()
    
    # Check if any results were found
    if "hit" not in data["result"]["hits"]:
        print(f"No results found for '{name}'")
        return None
    
    # Get the list of authors matching the search
    hits = data["result"]["hits"]["hit"]
    
    if len(hits) == 0:
        print(f"No results found for '{name}'")
        return None
    
    # Display a list of authors to choose from
    print(f"Found {len(hits)} authors matching '{name}':")
    
    authors_list = []
    for i, hit in enumerate(hits):
        if "info" in hit:
            author_info = hit["info"]
            author_name = author_info.get("author", "Unknown")
            author_url = author_info.get("url", "")
            print(f"{i+1}. {author_name} - {author_url}")
            authors_list.append({
                "name": author_name,
                "url": author_url
            })
    
    # If select_index is provided, use it
    if select_index is not None:
        if 0 <= select_index < len(hits):
            selected = select_index
        else:
            print(f"Invalid selection index: {select_index}")
            return authors_list
    # If there's only one result, select it automatically
    elif len(hits) == 1:
        selected = 0
    else:
        # If no select_index is provided, return the list of authors
        if select_index is None:
            return authors_list
            
        # Ask the user to select an author
        selected = -1
        while selected < 0 or selected >= len(hits):
            try:
                selected = int(input(f"Select an author (1-{len(hits)}): ")) - 1
            except ValueError:
                print("Please enter a valid number.")
    
    selected_author = hits[selected]["info"]
    return {
        "name": selected_author.get("author", "Unknown"),
        "url": selected_author.get("url", "")
    }

def get_publications(url):
    """
    Fetch publications for a given DBLP author URL
    """
    print(f"Fetching publications from {url}...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error: Failed to fetch publications. Status code: {response.status_code}")
        return None
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the publication list
    publications = []
    
    # Look for the publications in the page
    pub_items = soup.select('li.entry')
    
    for item in pub_items:
        pub = {}
        
        # Get the publication title
        title_element = item.select_one('span.title')
        if title_element:
            pub['title'] = title_element.text.strip()
        
        # Get the publication venue
        venue_element = item.select_one('span.venue')
        if venue_element:
            pub['venue'] = venue_element.text.strip()
        
        # Get the publication year
        year_element = item.select_one('span.year')
        if year_element:
            pub['year'] = year_element.text.strip()
        
        # Get the authors
        authors = []
        author_elements = item.select('span.authors a')
        for author in author_elements:
            authors.append(author.text.strip())
        
        if authors:
            pub['authors'] = authors
        
        # Get the type of publication
        pub_type_element = item.find(class_=lambda c: c and c.startswith('publ-'))
        if pub_type_element:
            classes = pub_type_element['class']
            pub_type = next((c for c in classes if c.startswith('publ-')), None)
            if pub_type:
                pub['type'] = pub_type.replace('publ-', '')
        
        # Get the publication URL - first check for DOI link
        pub_links = []
        link_elements = item.select('nav.publ li a')
        for link in link_elements:
            link_url = link.get('href', '')
            link_text = link.text.strip()
            if link_url:
                pub_links.append({
                    'url': link_url,
                    'text': link_text
                })
        
        if pub_links:
            pub['links'] = pub_links
        
        # Get the direct DBLP URL for the publication
        dblp_url_element = item.select_one('li.drop-down > a')
        if dblp_url_element:
            pub['dblp_url'] = dblp_url_element.get('href', '')
        
        publications.append(pub)
    
    return publications

def save_publications(scientist_name, publications, output_dir='./sci_search/data/'):
    """
    Save publications to a JSON file
    """
    # Create a sanitized filename from the scientist's name
    filename = re.sub(r'[^\w\s-]', '', scientist_name).strip().replace(' ', '_')
    filepath = os.path.join(output_dir, f"{filename}_publications.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(publications, f, indent=2, ensure_ascii=False)
    
    return filepath

def display_publications(publications):
    """
    Display publications in a formatted way
    """
    if not publications:
        print("No publications found.")
        return
    
    # Group publications by year
    by_year = {}
    for pub in publications:
        year = pub.get('year', 'Unknown')
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(pub)
    
    # Sort years in descending order
    for year in sorted(by_year.keys(), reverse=True):
        print(f"\n== {year} ==")
        
        # Sort publications within the year
        for pub in by_year[year]:
            title = pub.get('title', 'Untitled')
            venue = pub.get('venue', '')
            authors = ", ".join(pub.get('authors', []))
            pub_type = pub.get('type', 'publication')
            
            print(f"* {title}")
            if authors:
                print(f"  Authors: {authors}")
            if venue:
                print(f"  Venue: {venue}")
            print(f"  Type: {pub_type}")
            print()

def main():
    if len(sys.argv) > 1:
        name = " ".join(sys.argv[1:])
    else:
        name = input("Enter the name of the computer scientist: ")
    
    result = search_scientist(name)
    
    # If result is a list, we need to select one
    if isinstance(result, list):
        if len(result) == 0:
            print("No matching scientists found.")
            return
        
        # Display the list to choose from
        for i, author in enumerate(result):
            print(f"{i+1}. {author['name']} - {author['url']}")
        
        selected = -1
        while selected < 0 or selected >= len(result):
            try:
                selected = int(input(f"Select an author (1-{len(result)}): ")) - 1
            except ValueError:
                print("Please enter a valid number.")
        
        scientist = result[selected]
    else:
        scientist = result
    
    if scientist:
        print(f"Selected: {scientist['name']}")
        publications = get_publications(scientist['url'])
        
        if publications:
            print(f"Found {len(publications)} publications for {scientist['name']}.")
            
            # Save to file
            filepath = save_publications(scientist['name'], publications)
            print(f"Publications saved to {filepath}")
            
            # Display formatted publications
            display_publications(publications)
        else:
            print("No publications found.")
    else:
        print("No scientist selected.")

if __name__ == "__main__":
    main()