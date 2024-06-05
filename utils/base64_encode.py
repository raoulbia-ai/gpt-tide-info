import base64

api_key = "<api-key-here>"
combined_string = f"{api_key}:dummy"
encoded_credentials = base64.b64encode(combined_string.encode()).decode("utf-8")
print(encoded_credentials)