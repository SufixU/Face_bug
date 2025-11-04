import json
import requests

def load_cookies():
    with open('cookies.json', 'r') as f:
        return json.load(f)

def load_tokens():
    with open('dump_Facebook_token.json', 'r') as f:
        return json.load(f)

def create_fanpage(name, cookies, tokens):
    headers = {
        'authority': 'www.facebook.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': '; '.join([f"{cookie['key']}={cookie['value']}" for cookie in cookies]),
        'origin': 'https://www.facebook.com',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-fb-friendly-name': 'AdditionalProfilePlusCreationMutation',
        'x-fb-lsd': tokens['lsd_token']
    }

    data = {
        'fb_api_req_friendly_name': 'AdditionalProfilePlusCreationMutation',
        'variables': json.dumps({
            "input": {
                "bio": "",
                "categories": ["1350536325044173"],
                "creation_source": "comet",
                "name": name,
                "off_platform_creator_reachout_id": None,
                "page_referrer": "null",
                "actor_id": next(cookie['value'] for cookie in cookies if cookie['key'] == 'c_user'),
                "client_mutation_id": "1"
            }
        }),
        'server_timestamps': True,
        'doc_id': '23863457623296585',
        'fb_dtsg': tokens['dtsg_token'],
        'lsd': tokens['lsd_token'],
        'jazoest': tokens['jazoest'],
        '__spin_r': tokens['spin_r'],
        '__spin_b': 'trunk',
        '__spin_t': tokens['rev_token']
    }

    response = requests.post(
        'https://www.facebook.com/api/graphql/',
        headers=headers,
        data=data
    )
    response_json = response.json()
    
    if 'data' in response_json and 'additional_profile_plus_create' in response_json['data']:
        result = response_json['data']['additional_profile_plus_create']
        if result['name_error']:
            print(f"Błąd: Fanpage o nazwie '{name}' już istnieje. Proszę wybrać inną nazwę.")
            return False
    return response_json

cookies = load_cookies()
tokens = load_tokens()
result = create_fanpage("TestNaMeFanPagE!", cookies, tokens)
if result:
    print("Sukces!" if result['data']['additional_profile_plus_create']['page'] else "Wystąpił błąd podczas tworzenia fanpage.")
