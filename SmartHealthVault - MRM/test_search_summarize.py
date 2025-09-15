import requests
import json

def test_search_summarize():
    url = "http://localhost:8000/ai/search-and-summarize/"
    
    # Test data
    payload = {
        "query": "latest treatments for diabetes",
        "max_results": 3
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    try:
        # Make the POST request
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("✅ Search and summarize successful!")
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print("Response:", response.text)
    
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    print("Testing search and summarize endpoint...\n")
    test_search_summarize()
