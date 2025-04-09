import requests
import json

# URL of your API endpoint
api_url = "http://127.0.0.1:8000/api/v1/check-rental"

# Test data
payload = {
    "product_id": 1,
    "rental_period_id": 2,  # Updated to match the pricing record
    "region_id": 1,
    "pricing_id": 1
}

# Headers
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Make the request
try:
    response = requests.post(api_url, data=json.dumps(payload), headers=headers)
    
    # Print status code and response
    print(f"Status Code: {response.status_code}")
    print("Response Headers:", response.headers)
    print("Response Content:", response.text)
    
    # Try to parse JSON response
    try:
        json_response = response.json()
        print("\nParsed JSON Response:", json.dumps(json_response, indent=2))
    except json.JSONDecodeError:
        print("\nResponse is not valid JSON")
        
except Exception as e:
    print(f"Error making request: {e}")
