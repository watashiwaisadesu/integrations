from urllib.parse import urlparse, parse_qs

def extract_code_from_url(url):
    parsed_url = urlparse(url)
    # redirect_uri = str(request.base_url) + "v1/instagram/handle_code"
    # Construct the base URL
    redirect_uri = f"https://{parsed_url.netloc}{parsed_url.path}"
    print(f"REDIRECT_URL: {redirect_uri}")
    query_params = parse_qs(parsed_url.query)

    # Extract the 'code' parameter
    code = query_params.get('code', [None])[0]
    print(f"CODE: {code}")

    return redirect_uri,code
