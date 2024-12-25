# src/instagram_api/utils.py (or wherever you keep this function)

import logging
from urllib.parse import urlparse, parse_qs

from src.utils.errors_handler import InvalidQueryParameter  # new custom exception

logger = logging.getLogger(__name__)

def extract_code_from_url(url: str):
    parsed_url = urlparse(url)
    # Construct the base URL (redirect URI)
    redirect_uri = f"https://{parsed_url.netloc}{parsed_url.path}"
    logger.debug(f"Parsed redirect URI: {redirect_uri}")

    query_params = parse_qs(parsed_url.query)
    code = query_params.get('code', [None])[0]
    logger.debug(f"Extracted 'code' param from URL: {code}")

    if code is None:
        logger.error("Missing 'code' parameter in the URL")
        raise InvalidQueryParameter("The 'code' query parameter is required and missing.")

    return redirect_uri, code
