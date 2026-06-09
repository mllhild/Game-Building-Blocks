import requests
import json

# The JWT you got from your login
jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NTczMjc3MDEsImV4cCI6MTc1NzMzMTMwMSwidWlkIjo4LCJ1c2VybmFtZSI6IkhpbGQifQ.xfzofF3nmjNeBxnzMcdo2SoTW4ISErwk8nRdoe3W91Q"

# The API endpoint you want to send the POST to
url = "https://tbox.mllhild.com/api/submitpost.php"

# POST data
data = {
    "title": "Hello World",
    "text": "This is the content of my post"
}

# Headers including the JWT for authentication
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, headers=headers, json=data, verify=False)  # verify=False if using a self-signed SSL
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
