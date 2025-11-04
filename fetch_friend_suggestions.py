import json
import requests
from datetime import datetime

class FacebookFriendSuggestions:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.facebook.com/api/graphql/"
        self.cookies = self._load_cookies()
        self.tokens = self._load_tokens()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.facebook.com",
            "Referer": "https://www.facebook.com/"
        }
        self.headers.update({
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-fb-friendly-name": "FriendingCometPYMKPanelPaginationQuery",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        })

    def _load_cookies(self) -> dict:
        try:
            with open('cookies.json', 'r') as f:
                cookie_list = json.load(f)
                cookie_dict = {}
                for cookie in cookie_list:
                    if cookie['domain'] == 'facebook.com':
                        cookie_dict[cookie['key']] = cookie['value']
                return cookie_dict
        except Exception as e:
            raise Exception(f"Error loading cookies: {str(e)}")

    def _load_tokens(self) -> dict:
        try:
            with open('dump_Facebook_token.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading tokens: {str(e)}")

    def get_suggestions(self, cursor=None) -> dict:
        data = {
            'fb_api_req_friendly_name': 'FriendingCometPYMKPanelPaginationQuery',
            'variables': json.dumps({
                "count": 30,
                "cursor": cursor,
                "location": "FRIENDS_HOME_MAIN",
                "scale": 1
            }),
            'doc_id': '9917809191634193',
            'fb_api_caller_class': 'RelayModern',
            'server_timestamps': 'true',
            '__a': '1',
            '__req': '1',
            '__beoa': '0',
            '__pc': 'PHASED:DEFAULT',
            'dpr': '1',
            '__ccg': 'EXCELLENT',
            '__rev': self.tokens['rev_token'],
            '__s': '',
            '__hsi': self.tokens['hsi'],
            '__comet_req': '15',
            'fb_dtsg': self.tokens['dtsg_token'],
            'jazoest': self.tokens.get('jazoest', ''),
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
                data = response.json()
                if 'errors' in data:
                    raise Exception(f"Facebook API Error: {data['errors']}")
                return data
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse JSON response: {str(e)}")
        else:
            raise Exception(f"Request failed with status code: {response.status_code}")

    def parse_suggestions(self, data):
        try:
            edges = data['data']['viewer']['people_you_may_know']['edges']
            suggestions = []
            for edge in edges:
                node = edge['node']
                suggestion = {
                    'name': node['name'],
                    'url': f"https://www.facebook.com/{node['url']}",
                    'id': node['id']
                }
                if node.get('social_context') and node['social_context'].get('text'):
                    suggestion['social_context'] = node['social_context']['text']
                suggestions.append(suggestion)
            return suggestions
        except KeyError as e:
            raise Exception(f"Failed to parse suggestions: {str(e)}")

    def get_all_suggestions(self) -> list:
        all_suggestions = []
        seen_ids = set()
        cursor = None
        
        while True:
            result = self.get_suggestions(cursor)
            data = result['data']['viewer']['people_you_may_know']
            suggestions = self.parse_suggestions(result)
            
            for suggestion in suggestions:
                if suggestion['id'] not in seen_ids:
                    seen_ids.add(suggestion['id'])
                    all_suggestions.append(suggestion)
            
            page_info = data['page_info']
            if not page_info['has_next_page']:
                break
                
            cursor = page_info['end_cursor']
            print(f"Pobrano {len(all_suggestions)} unikalnych sugestii. Pobieram kolejną stronę...")
        
        return all_suggestions

def main():
    fb = FacebookFriendSuggestions()
    try:
        print("\n=== Facebook Friend Suggestions Fetcher ===")
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pobieranie wszystkich sugestii znajomych...")
        suggestions = fb.get_all_suggestions()
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sukces! Znaleziono {len(suggestions)} unikalnych sugestii znajomych:")
        
        for i, person in enumerate(suggestions, 1):
            print(f"\nOsoba {i}:")
            print(f"Imię i nazwisko: {person['name']}")
            print(f"URL: {person['url']}")
            print(f"ID: {person['id']}")
            if 'social_context' in person:
                print(f"Obserwowani / Wspólni znajomi: {person['social_context']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Wystąpił błąd: {str(e)}")

if __name__ == "__main__":
    main()
