import json
import requests

with open('cookies.json', 'r') as f:
    cookies_data = json.load(f)

with open('dump_Facebook_token.json', 'r') as f:
    tokens = json.load(f)

cookies = {cookie['key']: cookie['value'] for cookie in cookies_data}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'x-fb-friendly-name': 'StoriesCreateMutation',
}

def select_font():
    print("\n=== Wybierz czcionkę ===")
    print("1. Wyraźna czcionka")
    print("2. Nieformalna czcionka")
    print("3. Czcionka fantazyjna")
    print("4. Czcionka nagłówkowa")
    print("=====================")
    
    font_ids = {
        "1": "747812612080694",
        "2": "516266749248495",
        "3": "1790435664339626",
        "4": "1919119914775364"
    }
    
    while True:
        choice = input("-> Wybierz numer (1-4): ")
        if choice in font_ids:
            print(f"+ Wybrano czcionkę {choice}")
            return font_ids[choice]
        print("! Nieprawidłowy wybór. Spróbuj ponownie.")

def create_story(text, font_id):
    actor_id = next(cookie['value'] for cookie in cookies_data if cookie['key'] == 'c_user')
    
    variables = {
        "input": {
            "audiences": [
                {
                    "stories": {
                        "self": {
                            "target_id": actor_id
                        }
                    }
                }
            ],
            "audiences_is_complete": True,
            "navigation_data": {"attribution_id_v2": "StoriesCreateRoot.react,comet.stories.create,unexpected,1762321634148,642603,,,;ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,unexpected,1762321563389,811406,190055527696468,,;CometHomeRoot.react,comet.home,logo,1762321554944,791094,4748854339,,"},
            "source": "WWW",
            "message": {"ranges": [], "text": text},
            "text_format_metadata": {"inspirations_custom_font_id": font_id},
            "text_format_preset_id": "401372137331149",
            "tracking": [None],
            "actor_id": actor_id,
            "client_mutation_id": "1"
        }
    }
    
    data = {
        'fb_api_req_friendly_name': 'StoriesCreateMutation',
        'variables': json.dumps(variables),
        'server_timestamps': 'true',
        'doc_id': '24226878183562473',
        'fb_dtsg': tokens['dtsg_token'],
        '__spin_r': tokens['spin_r'],
        '__spin_b': 'trunk',
        '__spin_t': tokens['rev_token'],
    }

    response = requests.post(
        'https://www.facebook.com/api/graphql/',
        headers=headers,
        cookies=cookies,
        data=data
    )

    if response.status_code == 200:
        print("\n+ Story zostało poprawnie dodane!")
    else:
        print("\n! Błąd podczas dodawania story!")

if __name__ == "__main__":
    print("=== Facebook Story Creator ===")
    
    while True:
        text = input("\n-> Wprowadź tekst do story: ").strip()
        if text:
            print("+ Tekst zaakceptowany")
            break
        print("! Błąd: Tekst nie może być pusty!")
    
    font_id = select_font()
    print("\n-> Dodawanie story...")
    create_story(text, font_id)
