import subprocess

curl_command = [
    "curl",
    "-X", "POST",
    external_service_url,
    "-H", "Content-Type: application/json",
    "-d", payload_json
]