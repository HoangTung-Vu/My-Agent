import re
import html
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class HTMLProcessor:
    """
    Process HTML content from web searches to extract useful information.
    This class handles parsing, cleaning, and extracting structured data from HTML.
    """

    def __init__(self):
        self.soup = None
        
    def process_html(self, html_content: str) -> Dict[str, Any]:
        """
        Process HTML content and extract useful information.
        
        Args:
            html_content: The raw HTML content as a string
        
        Returns:
            Dictionary containing extracted information:
            - title: Page title
            - description: Meta description
            - main_content: Main textual content
            - metadata: Dictionary of meta tags
            - links: List of links
            - images: List of image URLs
            - structured_data: Any structured data found
        """
        if not html_content:
            logger.warning("Empty HTML content provided")
            return self._empty_result()
        
        try:
            # Parse the HTML
            self.soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract information
            result = {
                "title": self.extract_title(),
                "description": self.extract_meta_description(),
                "main_content": self.extract_main_content()
            }
            
            return result
        except Exception as e:
            logger.error(f"Error processing HTML: {str(e)}")
            return self._empty_result()

    def extract_title(self) -> str:
        """Extract the page title."""
        if not self.soup:
            return ""
        
        title_tag = self.soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def extract_meta_description(self) -> str:
        """Extract meta description."""
        if not self.soup:
            return ""
        
        meta_desc = self.soup.find('meta', attrs={'name': 'description'}) or \
                    self.soup.find('meta', attrs={'property': 'og:description'})
        
        if meta_desc:
            return meta_desc.get('content', '').strip()
        return ""
    
    def extract_main_content(self) -> str:
        """
        Extract the main content from the HTML.
        Uses heuristics to identify the main content area.
        """
        if not self.soup:
            return ""
        
        # Try to find the main content using common selectors
        main_selectors = [
            'article', 'main', '.main-content', '#main-content',
            '.content', '#content', '.post-content', '.entry-content'
        ]
        
        for selector in main_selectors:
            main = self.soup.select_one(selector)
            if main:
                # Clean the content
                for tag in main.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    tag.decompose()
                
                text = main.get_text(separator='\n').strip()
                return self._clean_text(text)
        
        # If no main content found with selectors, extract body text
        if self.soup.body:
            for tag in self.soup.body.find_all(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            
            text = self.soup.body.get_text(separator='\n').strip()
            return self._clean_text(text)[:2000]
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Unescape HTML entities
        text = html.unescape(text)
        # Remove leading/trailing whitespace
        return text.strip()
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return an empty result structure."""
        return {
            "title": "",
            "description": "",
            "main_content": ""
        }


def process_html_content(html_content: str) -> str:
    """
    Process HTML content and extract useful information.
    
    Args:
        html_content: Raw HTML content as a string
        
    Returns:
        String containing the concatenated title, description, and main content.
    """
    processor = HTMLProcessor()
    result_dict = processor.process_html(html_content)
    
    concatenated_text = ""
    
    if result_dict["title"]:
        concatenated_text += f"Title: {result_dict['title']}\n\n"
    
    if result_dict["description"]:
        concatenated_text += f"Description: {result_dict['description']}\n\n"
    
    if result_dict["main_content"]:
        concatenated_text += f"Content: {result_dict['main_content']}"
    
    return concatenated_text.strip()

