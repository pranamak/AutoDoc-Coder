from typing import Optional, Set
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import requests, validators
from urllib.parse import urljoin


def fetch_and_clean_api_docs(url: str, source_type: str, visited_urls: Set[str] = None, max_depth: int = 1, current_depth: int = 0) -> Optional[str]:
    """
    Fetches and cleans API documentation from the given URL.

    Args:
    url (str): The URL of the API documentation.
    source_type (str): The type of the source, either "URL" or "PDF".
    max_depth (int): The maximum depth of nested URLs to scrape. Defaults to 1.
    current_depth (int): The current depth of nested URLs to scrape. Defaults to 0.
    visited_urls (Set[str]): A set of URLs that have already been visited. Defaults to an empty set.
    
    Returns:
    Optional[str]: The cleaned API documentation, or None if an error occurred.
    """

    try:
        if source_type == "PDF":
            # Extract text from PDF
            reader = PdfReader(url)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        # Validate URL
        if source_type == "URL":
            if not validators.url(url):
                raise ValueError(f"Invalid URL provided: {url}")

        # Check if URL has already been visited
        if url in visited_urls:
            return ""

        # Add URL to visited set
        visited_urls.add(url)

        # Send GET request to URL
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Try to extract only <main> content if it exists
        main = soup.find("main") or soup.find(id="main") or soup.find(class_="content")
        if main:
            soup = main  # narrow focus

        # 2. Remove unwanted layout elements
        unwanted_selectors = [
            'nav', '[role="navigation"]', '.sidebar', '.navigation', '.navbar'
        ]

        for selector in unwanted_selectors:
            for tag in soup.select(selector):
                tag.decompose()
 
        text = soup.get_text(separator='\n', strip=True)
        sections = [text]

        # Scrape nested URLs
        if current_depth < max_depth:
            nested_urls = []
            for link in soup.find_all("a"):
                href = link.get("href")
                if not href.startswith("http"):
                    href = urljoin(url, href)
                    print(href)
                if href:
                    nested_urls.append(href)
            for nested_url in nested_urls:
                nested_sections = fetch_and_clean_api_docs(nested_url, source_type, visited_urls, max_depth, current_depth + 1)
                if nested_sections:
                    sections.append("\n\n" + nested_sections)

        return "\n\n".join(sections)
    except requests.exceptions.RequestException as e:
        return f"Error fetching API documentation: {e}"
    except ValueError as e:
        raise ValueError(e)
    except Exception as e:
        return f"Error cleaning API documentation: {e}"


if __name__ == "__main__":
    cont = fetch_and_clean_api_docs("https://gtidocs.virustotal.com/reference/scan-url", "URL")
    file_path = "test2_pm.txt"
    with open(file_path, 'w') as file:
        file.write(cont)