"""
earnkaro_client.py
Helper module to build EarnKaro affiliate links programmatically.
"""
import os
import urllib.parse

EARNKARO_API_KEY = os.environ.get("EARNKARO_API_KEY")
EARNKARO_SOURCE_ID = os.environ.get("EARNKARO_SOURCE_ID")

def create_affiliate_link(original_url: str) -> str:
    """
    Creates an EarnKaro affiliate link using redirection format or custom credentials.
    """
    if not original_url:
        return ""
    
    # Clean original URL
    clean_url = original_url.split("?")[0].strip()
    
    # If key and source are present, construct standard API redirect link
    if EARNKARO_API_KEY and EARNKARO_SOURCE_ID:
        encoded_url = urllib.parse.quote_plus(clean_url)
        # EarnKaro redirect structure format
        return f"https://earnkaro.com/connect?api_key={EARNKARO_API_KEY}&source_id={EARNKARO_SOURCE_ID}&link={encoded_url}"
    
    # Fallback/Dummy representation if keys aren't set
    return f"https://earnkaro.com/share?url={urllib.parse.quote_plus(clean_url)}"