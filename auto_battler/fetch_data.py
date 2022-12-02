import requests
from typing import Dict, Any


def fetch_data() -> Dict[str, Any]:
    return requests.get("https://superauto.pet/api.json").json()
