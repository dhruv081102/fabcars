import requests
import json

def search_phone_number(phone_number):
    
    # Data to send in the POST request
    data = {
        "event_type": "search_phone_number",
        "phone_number": phone_number
    }
    web_app_url = 'https://script.google.com/macros/s/AKfycbwoARM9xi2WK-fVBH9BPg1zXknFA8qTmVW9e73RLtrAagtAfyeGPaSYi_4vzZn41HzVeg/exec'
    try:
        # Send POST request
        response = requests.post(web_app_url, json=data)
        
        # Raise an exception for HTTP errors
        response.raise_for_status()
        
        # Parse the JSON response
        result = response.json()
        return result

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Print HTTP error
    except requests.exceptions.ConnectionError as conn_err:
        print(f'Connection error occurred: {conn_err}')  # Print connection error
    except requests.exceptions.Timeout as timeout_err:
        print(f'Timeout error occurred: {timeout_err}')  # Print timeout error
    except requests.exceptions.RequestException as req_err:
        print(f'Request error occurred: {req_err}')  # Print general request error
    except json.JSONDecodeError as json_err:
        print(f'JSON decode error: {json_err}')  # Print JSON parsing error
    except Exception as e:
        print(f'An unexpected error occurred: {e}')  # Print any other unexpected error

    return None  # Return None if an error occurs

# Example usage
if __name__ == "__main__":
      # Replace with your actual URL
    phone_number = "9322365083"  # Replace with the number you want to search
    result = search_phone_number(phone_number)
    print(result)
    if result is not None:
        print('Response from Google Apps Script:', result)
    else:
        print('Failed to retrieve a valid response.')
