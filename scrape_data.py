import requests
from bs4 import BeautifulSoup
import re
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

api_key = "AIzaSyAfd_IEh6P2Ssj7SJHeBH1NWzkBhHoV9OM"
search_engine_id = "c60b50ebadc2944c0"

ALLOWED_DOMAINS = ["wikipedia.org", "blogspot.com", "medium.com", "wordpress.com"]

def get_search_results(query, api_key, search_engine_id, num_results=5):
    logger.info(f"Starting search for topic: {query}")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': search_engine_id,
        'num': num_results
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        results = response.json().get('items', [])
        filtered_results = [
            item['link'] for item in results if any(domain in item['link'] for domain in ALLOWED_DOMAINS)
        ]
        logger.info(f"Filtered to {len(filtered_results)} results from allowed domains")
        return filtered_results
    else:
        logger.error(f"Failed to fetch search results. Status code: {response.status_code}")
        return []

def scrape_web_page(url):
    logger.info(f"Scraping URL: {url}")
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='main-content')

            paragraphs = main_content.find_all('p') if main_content else soup.find_all('p')

            text = ' '.join([para.get_text() for para in paragraphs])
            
            filtered_text = filter_unwanted_text(text)

            logger.info(f"Successfully scraped URL: {url}")
            return filtered_text
        else:
            logger.warning(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
            return ""
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return ""

def filter_unwanted_text(text):
    unwanted_phrases = [
        "Terms of Use", "Privacy Policy", "All rights reserved", 
        "reproduction", "NBC", "Internet Explorer", "cookies", "©", "consent"
    ]
    for phrase in unwanted_phrases:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)
    return text

def clean_text(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def save_extracted_data(data, filename="extracted_data.txt"):
    logger.info(f"Saving extracted data to {filename}")
    with open(filename, "w") as file:
        file.write(clean_text(data))
    logger.info("Data saved successfully")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("No topic provided. Usage: python scrape_data.py <topic>")
        sys.exit(1)
    
    topic = ' '.join(sys.argv[1:])
    logger.info(f"Script started for topic: {topic}")
    
    urls = get_search_results(topic, api_key, search_engine_id)
    
    all_text = ""
    for url in urls:
        text = scrape_web_page(url)
        all_text += text + "\n"

    save_extracted_data(all_text)
    
    logger.info("Displaying extracted data:")
    print(all_text.strip())

    logger.info("Script completed successfully")
