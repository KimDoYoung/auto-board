import urllib.request
import json
import urllib.error

url = "http://127.0.0.1:8000/boards/create"
payload = {
  "board": {
    "name": "Debug Board",
    "physical_table_name": "debug_table_x",
    "note": "Debugging"
  },
  "columns": {
    "fields": [
      {
        "name": "title",
        "label": "Title",
        "data_type": "string",
        "required": True
      }
    ]
  }
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(f"Body: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}")
    print(f"Body: {e.read().decode('utf-8')}")
except Exception as e:
    print(e)
