import json
import requests
from datetime import datetime

def load_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def get_actor_id(cookies):
    for cookie in cookies:
        if cookie['key'] == 'c_user':
            return cookie['value']
    return None

def update_facebook_bio(bio_text):
    cookies = load_json_file('cookies.json')
    tokens = load_json_file('dump_Facebook_token.json')
    
    actor_id = get_actor_id(cookies)
    if not actor_id:
        raise Exception("Nie można znaleźć ID użytkownika w cookies")
    
    cookie_dict = {cookie['key']: cookie['value'] for cookie in cookies}
    
    headers = {
        'authority': 'www.facebook.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.facebook.com',
        'referer': 'https://www.facebook.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    variables = {
        "input": {
            "attribution_id_v2": "ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,unexpected,1762239359096,829466,190055527696468,,",
            "bio": bio_text,
            "publish_bio_feed_story": True,
            "actor_id": actor_id,
            "client_mutation_id": "3"
        },
        "hasProfileTileViewID": True,
        "profileTileViewID": f"cHJvZmlsZV90aWxlX3ZpZXc6{actor_id}6aW50cm86aW50cm9fYmlvOmludHJvX2NhcmRfYmlvOnByb2ZpbGVfdGltZWxpbmU6MQ==",
        "scale": 1,
        "useDefaultActor": False
    }
    
    data = {
        'fb_api_req_friendly_name': 'ProfileCometSetBioMutation',
        'variables': json.dumps(variables),
        'doc_id': '25103750752554483',
        'fb_api_caller_class': 'RelayModern',
        'fb_api_analytics_tags': '["qpl_active_flow_ids=431626709"]',
        'server_timestamps': True,
        'fb_dtsg': tokens['dtsg_token'],
        'lsd': tokens['lsd_token'],
        '__spin_r': tokens['spin_r'],
        '__spin_b': 'trunk',
        '__spin_t': tokens['rev_token'],
    }
    
    response = requests.post(
        'https://www.facebook.com/api/graphql/',
        headers=headers,
        cookies=cookie_dict,
        data=data
    )
    
    return response.json()

if __name__ == "__main__":
    try:
        print("\n=== Facebook Bio Updater ===")
        bio_text = input("Wprowadź nowy tekst bio: ")
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Próba aktualizacji bio...")
        result = update_facebook_bio(bio_text)
        
        if 'errors' in result:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Wystąpił błąd:")
            print(result['errors'])
        else:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sukces! Bio zostało zaktualizowane na: {bio_text}")
            
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Wystąpił błąd: {str(e)}")
