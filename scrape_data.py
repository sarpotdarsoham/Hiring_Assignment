import requests
from bs4 import BeautifulSoup

# URL of the webpage to scrape
url = "https://en.wikipedia.org/wiki/Altera"

# Fetch the webpage content
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Extracting headings (e.g., H2 tags)
headings = soup.find_all('h2')
print("Headings:")
for heading in headings:
    print(heading.text.strip())

# Extracting paragraphs
paragraphs = soup.find_all('p')
print("\nParagraphs:")
for paragraph in paragraphs[:3]:  # Limiting to first 3 paragraphs for simplicity
    print(paragraph.text.strip())

# Save the extracted data into a text file
with open("extracted_data.txt", "w") as file:
    file.write("Headings:\n")
    for heading in headings:
        file.write(heading.text.strip() + "\n")

    file.write("\nParagraphs:\n")
    for paragraph in paragraphs[:3]:
        file.write(paragraph.text.strip() + "\n")
