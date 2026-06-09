url = "https://tbox.mllhild.com/forum/register.php"
data = {"login": "Hild", "password": "Hild"}

import requests
try:
    response = requests.post(url, json=data, verify=False)  # disable SSL verification  because Im going via cloudflare tunnel
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)