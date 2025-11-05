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

def extract_friend_info(friend_data):
    try:
        action_data = friend_data.get('actions_renderer', {}).get('action', {})
        client_handler = action_data.get('client_handler', {})
        profile_action = client_handler.get('profile_action', {})
        profile_owner = profile_action.get('restrictable_profile_owner', {})
        
        if not profile_owner:
            profile_owner = (action_data.get('profile_owner') or 
                           friend_data.get('node') or 
                           friend_data)
        
        status = profile_owner.get('friendship_status', 'Unknown')
        if status == 'ARE_FRIENDS':
            status = 'Znajomi'
        
        return {
            'name': profile_owner.get('name', friend_data.get('title', {}).get('text', 'Unknown')),
            'id': profile_owner.get('id', 'Unknown'),
            'friendship_status': status,
            'gender': 'Kobieta' if profile_owner.get('gender') == 'FEMALE' else 'Mężczyzna' if profile_owner.get('gender') == 'MALE' else 'Nieznane'
        }
    except Exception as e:
        print(f"Error in extract_friend_info: {str(e)}")
        return None

def get_friends():
    cookies = load_json_file('cookies.json')
    tokens = load_json_file('dump_Facebook_token.json')
    
    actor_id = get_actor_id(cookies)
    if not actor_id:
        raise Exception("Nie można znaleźć ID użytkownika w cookies")
    
    cookies_dict = {cookie['key']: cookie['value'] for cookie in cookies}
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
    
    friends_list = []
    cursor = None
    page = 1
    
    while True:
        variables = {
            "count": 500,
            "cursor": cursor,
            "scale": 1,
            "search": None,
            "id": "YXBwX2NvbGxlY3Rpb246cGZiaWQwMkJ4VXpCYkRNUml0ajJ6YnpzOWVpZXIzNE1uVW5NRDNQM3V3YW01dFdZQnBWcEh6dHdLVG1KRHdmUHlCRGRjWG9lQUdRQnBMamtROW9TZXJFR1RLd2ZCWEhuSmw=",
            "__relay_internal__pv__FBProfile_enable_perf_improv_gkrelayprovider": True
        }
        
        data = {
            'fb_api_req_friendly_name': 'ProfileCometAppCollectionSelfFriendsListRendererPaginationQuery',
            'variables': json.dumps(variables),
            'doc_id': '24590503720622379',
            'fb_dtsg': tokens['dtsg_token'],
            'lsd': tokens['lsd_token'],
            '__spin_r': tokens['spin_r'],
            '__spin_b': 'trunk',
            '__spin_t': tokens['rev_token'],
            'server_timestamps': True
        }
        
        response = requests.post(
            'https://www.facebook.com/api/graphql/',
            headers=headers,
            cookies=cookies_dict,
            data=data
        )
        
        data = response.json()
        
        try:
            edges = (data.get('data', {}).get('node', {}).get('pageItems', {}).get('edges', []) or
                    data.get('data', {}).get('node', {}).get('all_friends', {}).get('edges', []) or
                    data.get('data', {}).get('viewer', {}).get('friends', {}).get('edges', []) or
                    data.get('data', {}).get('friends', {}).get('edges', []) or
                    [])
            
            if not edges:
                print("\nNie znaleziono więcej znajomych")
                break
                
            for edge in edges:
                friend_info = extract_friend_info(edge.get('node', {}))
                if friend_info:
                    friends_list.append(friend_info)
            
            print(f"Strona {page}: Pobrano {len(edges)} znajomych (łącznie: {len(friends_list)})")
            
            last_edge = edges[-1] if edges else None
            if last_edge and 'cursor' in last_edge:
                cursor = last_edge['cursor']
                page += 1
            else:
                print("\nOsiągnięto koniec listy znajomych")
                break
                
        except Exception as e:
            print(f"Błąd podczas pobierania strony {page}: {str(e)}")
            break
    
    print(f"\nZakończono pobieranie. Łącznie pobrano {len(friends_list)} znajomych")
    return friends_list

if __name__ == "__main__":
    try:
        print("\n=== Facebook Friends List Fetcher ===")
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pobieranie listy znajomych...")
        
        friends_data = get_friends()
        
        if isinstance(friends_data, list):
            print("\nZnalezieni znajomi:")
            for friend in friends_data:
                print(f"\nImię: {friend['name']}")
                print(f"ID: {friend['id']}")
                print(f"Status: {friend['friendship_status']}")
                print(f"Płeć: {friend['gender']}")
        else:
            print("\nWystąpił błąd podczas pobierania danych:")
            print(json.dumps(friends_data, indent=2))
            
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Wystąpił błąd: {str(e)}")
