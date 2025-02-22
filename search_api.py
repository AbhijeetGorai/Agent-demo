import http.client
import json
from typing import Dict, Optional

class SearchAPI:
    def __init__(self, api_key: str = '425ead50d860761af310f47b839ef98e6041f54e'):
        self.api_key = api_key
        self.base_url = "google.serper.dev"

    def search(self, query: str) -> str:
        conn = http.client.HTTPSConnection(self.base_url)
        payload = json.dumps({
            "q": query,
            "gl": "in"
        })
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            conn.request("POST", "/search", payload, headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            
            if "answerBox" in json_data and "answer" in json_data["answerBox"]:
                return json_data["answerBox"]["answer"]
            elif "organic" in json_data and len(json_data["organic"]) > 0:
                return json_data["organic"][0]["snippet"]
            else:
                return "No relevant answer found"
                
        except Exception as e:
            return f"Error processing request: {str(e)}"
        finally:
            conn.close() 