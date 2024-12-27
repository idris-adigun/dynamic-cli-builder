# Action Functions
def fetch_data(url: str, headers: str = None):
    import json
    import requests

    headers_dict = json.loads(headers) if headers else {}
    response = requests.get(url, headers=headers_dict)
    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())

def greet_user(name: str):
    print(f"Hello, {name}!")

# Action Registry
ACTIONS = {
    "fetch_data": fetch_data,
    "greet_user": greet_user,
}