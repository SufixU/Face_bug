import json
import requests
import random
import time
from datetime import datetime

class FacebookFriendAdder:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.facebook.com/api/graphql/"
        self.cookies = self._load_cookies()
        self.tokens = self._load_tokens()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.facebook.com",
            "Referer": "https://www.facebook.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }

    def _load_cookies(self) -> dict:
        try:
            with open('cookies.json', 'r') as f:
                cookie_list = json.load(f)
                cookie_dict = {}
                for cookie in cookie_list:
                    if cookie['domain'] == 'facebook.com':
                        cookie_dict[cookie['key']] = cookie['value']
                        self.session.cookies.set(cookie['key'], cookie['value'])
                return cookie_dict
        except Exception as e:
            raise Exception(f"Error loading cookies: {str(e)}")

    def _load_tokens(self) -> dict:
        try:
            with open('dump_Facebook_token.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading tokens: {str(e)}")

    def send_friend_request(self, user_id):
        data = {
            'fb_api_req_friendly_name': 'FriendingCometFriendRequestSendMutation',
            'variables': json.dumps({
                "input": {
                    "friend_requestee_ids": [str(user_id)],
                    "friending_channel": "PROFILE_BUTTON",
                    "warn_ack_for_ids": [],
                    "actor_id": self.cookies.get('c_user'),
                    "client_mutation_id": str(random.randint(1, 9999999))
                },
                "scale": 1
            }),
            'doc_id': '24974393785534352',
            'fb_api_caller_class': 'RelayModern',
            'server_timestamps': 'true',
            '__rev': self.tokens['rev_token'],
            '__hsi': self.tokens['hsi'],
            'fb_dtsg': self.tokens['dtsg_token'],
            '__spin_r': self.tokens['spin_r'],
            '__spin_b': 'trunk',
            '__spin_t': self.tokens['spin_r']
        }

        response = self.session.post(
            self.base_url,
            headers=self.headers,
            cookies=self.cookies,
            data=data
        )

        if response.status_code == 200:
            try:
                result = response.json()
                success = 'errors' not in result
                return {'success': success}
            except json.JSONDecodeError as e:
                raise Exception(f"Błąd przetwarzania odpowiedzi: {str(e)}")
        else:
            raise Exception(f"Błąd połączenia, status: {response.status_code}")

    def add_multiple_friends(self, user_ids):
        for user_id in user_ids:
            try:
                result = self.send_friend_request(user_id)
                if result['success']:
                    print(f"Wysłano zaproszenie dla UID: {user_id}")
                    return
                else:
                    print(f"Nie udało się wysłać zaproszenia dla UID: {user_id}")
            except Exception as e:
                print(f"Błąd: {str(e)}")
            break

if __name__ == "__main__":
    try:
        fb_adder = FacebookFriendAdder()
        user_ids = ["61564810780807"]
        fb_adder.add_multiple_friends(user_ids)
    except Exception as e:
        print(f"Błąd krytyczny: {str(e)}")
