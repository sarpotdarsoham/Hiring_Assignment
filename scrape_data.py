import requests
from bs4 import BeautifulSoup
import json
import re
import fitz

def scrape_wikipedia_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    structured_data = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            structured_data.append(data)
        except json.JSONDecodeError:
            continue

    headings = [h2.text.strip() for h2 in soup.find_all('h2')]
    paragraphs = [p.text.strip() for p in soup.find_all('p')]
    tables = [table.text.strip() for table in soup.find_all('table')]
    infobox = soup.find(class_="infobox")
    infobox_data = infobox.text.strip() if infobox else ""

    return {
        "structured_data": structured_data,
        "headings": headings,
        "paragraphs": paragraphs,
        "tables": tables,
        "infobox": infobox_data
    }

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def clean_text(text):
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def save_extracted_data(data, filename="extended_extracted_data.txt"):
    with open(filename, "w") as file:
        if data['structured_data']:
            file.write("Structured Data:\n")
            for item in data['structured_data']:
                file.write(json.dumps(item, indent=2) + "\n\n")
        
        file.write("Headings:\n" + "\n".join(map(clean_text, data["headings"])) + "\n\n")
        file.write("Paragraphs:\n" + "\n".join(map(clean_text, data["paragraphs"])) + "\n\n")
        file.write("Tables:\n" + "\n".join(map(clean_text, data["tables"])) + "\n\n")
        file.write("Infobox:\n" + clean_text(data["infobox"]) + "\n")


def append_pdf_data(pdf_text, filename="extended_extracted_data.txt"):
    with open(filename, "a") as file:
        file.write("\n\nPDF Extracted Content:\n")
        file.write(clean_text(pdf_text) + "\n")

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Altera"
    data = scrape_wikipedia_page(url)
    save_extracted_data(data)
    pdf_file = "P1.pdf"
    pdf_text = extract_text_from_pdf(pdf_file)
    append_pdf_data(pdf_text)
