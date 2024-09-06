import requests
from bs4 import BeautifulSoup
import os

# Starting URL (you can start from the homepage)
start_url = 'https://msec.edu.in/'

# Make the HTTP request
response = requests.get(start_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all links that point to .html files
html_files = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.html')]

# Ensure unique URLs and convert relative URLs to absolute
html_files = list(set([requests.compat.urljoin(start_url, link) for link in html_files]))

# Create a folder to store the files
os.makedirs('scraped_pages', exist_ok=True)

# Iterate through the list of .html pages and scrape content
for html_file in html_files:
    try:
        response = requests.get(html_file)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text_data = soup.get_text()

            # Save the extracted text data to a .txt file
            file_name = os.path.join('scraped_pages', f"{os.path.basename(html_file).replace('.html', '')}.txt")
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(text_data)

            print(f"Text data from {html_file} has been saved to {file_name}.")
        else:
            print(f"Failed to retrieve {html_file}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
