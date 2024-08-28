import requests
from bs4 import BeautifulSoup

def scrape_wikipedia_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract headings
    headings = [h2.text.strip() for h2 in soup.find_all('h2')]

    # Extract paragraphs
    paragraphs = [p.text.strip() for p in soup.find_all('p')]

    # Extract tables
    tables = [table.text.strip() for table in soup.find_all('table')]

    # Extract infoboxes or lists
    infobox = soup.find(class_="infobox")
    infobox_data = infobox.text.strip() if infobox else ""

    return {
        "headings": headings,
        "paragraphs": paragraphs,
        "tables": tables,
        "infobox": infobox_data
    }

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Altera"
    data = scrape_wikipedia_page(url)

    # Save the extracted data into a text file
    with open("extended_extracted_data.txt", "w") as file:
        file.write("Headings:\n" + "\n".join(data["headings"]) + "\n\n")
        file.write("Paragraphs:\n" + "\n".join(data["paragraphs"]) + "\n\n")
        file.write("Tables:\n" + "\n".join(data["tables"]) + "\n\n")
        file.write("Infobox:\n" + data["infobox"] + "\n")
