import requests
import time
import random
import requests
from utils.agent import random_user_agent
from typing import Optional



def laborum_fetch(url: str, headers: dict, body: dict) -> dict | None:
    headers['User-Agent'] = random_user_agent()
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error in fetching data from Laborum:", url)
        print("Status code:", response.status_code if 'response' in locals() else 'unknown')
        return None






def trabajando_fetch(url: str, headers: dict, timeout: int = 10, retries: int = 2) -> dict | None:
    headers = headers or {}
    headers['User-Agent'] = random_user_agent()
    headers.setdefault('Accept', 'application/json')
    last_err = None

    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            last_err = e
            time.sleep(1 + attempt * 0.5)
            continue
        except Exception as e:
            print("Error in fetching data from Trabajando:", url)
            return None

    print("Timeout/connection error from Trabajando:", url, "-", last_err)
    return None


def trabajo_con_sentido_fetch(url: str, headers: dict) -> dict | None:
    agent = random_user_agent()
    headers['User-Agent'] = agent

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error in fetching data from TrabajoConSentido:", url)
        return None

def linkedin_fetch(url: str, retries: int = 3, timeout: int = 20) -> Optional[str]:
    """
    GET simple para endpoints públicos de LinkedIn (jobs-guest y páginas de detalle).
    Rota User-Agent y hace pequeños backoffs para reducir bloqueos.
    """
    for attempt in range(1, retries + 1):
        try:
            headers = {
                "User-Agent": random_user_agent(),
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200 and resp.text:
                return resp.text
            # 429 / 403 -> backoff aleatorio
            if resp.status_code in (429, 403):
                time.sleep(1.5 + random.random() * 2.5)
            else:
                time.sleep(0.5 + random.random())
        except requests.RequestException:
            time.sleep(0.7 + random.random())
    return None