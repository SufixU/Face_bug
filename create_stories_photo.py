import requests
import json
import time
from pathlib import Path

def load_config():
    with open('cookies.json', 'r') as f:
        cookies_data = json.load(f)
    with open('dump_Facebook_token.json', 'r') as f:
        tokens = json.load(f)
    
    cookies = {cookie['key']: cookie['value'] for cookie in cookies_data}
    user_id = next(cookie['value'] for cookie in cookies_data if cookie['key'] == 'c_user')
    
    return cookies, tokens, user_id

class FacebookStoryUploader:
    def __init__(self):
        self.cookies, self.tokens, self.user_id = load_config()
        self.session = requests.Session()
        self.session.cookies.update(self.cookies)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Origin': 'https://www.facebook.com',
            'Referer': 'https://www.facebook.com/stories/create/',
            'Sec-Fetch-Site': 'same-origin'
        })

    def upload_photo(self, image_path):
        upload_url = "https://upload.facebook.com/ajax/react_composer/attachments/photo/upload"
        upload_id = f"jsc_c_{int(time.time())}"
        
        with open(image_path, 'rb') as f:
            files = {'farr': (Path(image_path).name, f, 'image/jpeg')}
            data = {
                'source': '8',
                'profile_id': self.user_id,
                'waterfallxapp': 'comet_stories',
                'upload_id': upload_id
            }
            params = {
                '__a': '1',
                'fb_dtsg': self.tokens['dtsg_token'],
                'lsd': self.tokens['lsd_token'],
                '__user': self.user_id,
                '__comet_req': '15'
            }
            
            print(f"[1/2] Przesyłanie zdjęcia...")
            response = self.session.post(upload_url, params=params, data=data, files=files)
            
            if response.status_code != 200:
                print(f"❌ Błąd przesyłania: {response.status_code}")
                return None
                
            try:
                text = response.text.replace('for (;;);', '')
                result = json.loads(text)
                photo_id = result.get('payload', {}).get('photoID')
                
                if photo_id:
                    print("✓ Zdjęcie przesłane pomyślnie!")
                    return photo_id
                else:
                    print("❌ Błąd: Nie można uzyskać ID zdjęcia")
                    return None
                    
            except Exception as e:
                print(f"❌ Błąd: {str(e)}")
                return None

    def create_story(self, photo_id):
        url = "https://www.facebook.com/api/graphql/"
        
        composer_session_id = f"{hex(int(time.time()))[2:]}-{hex(int(time.time()*1000))[2:]}-48b6-b736-87b2a797d756"
        
        data = {
            'doc_id': '24226878183562473',
            'fb_api_req_friendly_name': 'StoriesCreateMutation',
            'variables': json.dumps({
                "input": {
                    "audiences": [{"stories": {"self": {"target_id": self.user_id}}}],
                    "audiences_is_complete": True,
                    "logging": {
                        "composer_session_id": composer_session_id
                    },
                    "navigation_data": {
                        "attribution_id_v2": "StoriesCreateRoot.react,comet.stories.create,unexpected," + \
                                          f"{int(time.time()*1000)},633895,,,;StoriesCometSuspenseRoot.react," + \
                                          f"comet.stories.viewer,via_cold_start,{int(time.time()*1000)-200000},762088,,,",
                    },
                    "source": "WWW",
                    "attachments": [{"photo": {"id": photo_id, "overlays": []}}],
                    "tracking": [None],
                    "actor_id": self.user_id,
                    "client_mutation_id": "2"
                }
            }),
            'server_timestamps': True,
            'fb_dtsg': self.tokens['dtsg_token'],
            '__a': '1',
            '__user': self.user_id,
            '__comet_req': '15'
        }
        
        print(f"[2/2] Tworzenie relacji...")
        response = self.session.post(url, data=data)
        
        if response.status_code != 200:
            print("❌ Błąd tworzenia relacji")
            return False
            
        try:
            text = response.text.replace('for (;;);', '')
            result = json.loads(text)
            
            if 'errors' not in result:
                print("✓ Relacja utworzona pomyślnie!")
                return True
            else:
                print("❌ Błąd podczas tworzenia relacji")
                return False
                
        except Exception as e:
            print(f"❌ Błąd: {str(e)}")
            return False

    def upload_story(self, image_path):
        photo_id = self.upload_photo(image_path)
        if not photo_id:
            return False
            
        time.sleep(1)
        return self.create_story(photo_id)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("""
    ███████╗██████╗     ███████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
    ██╔════╝██╔══██╗    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
    █████╗  ██████╔╝    ███████╗   ██║   ██║   ██║██████╔╝ ╚████╔╝ 
    ██╔══╝  ██╔══██╗    ╚════██║   ██║   ██║   ██║██╔══██╗  ╚██╔╝  
    ██║     ██████╔╝    ███████║   ██║   ╚██████╔╝██║  ██║   ██║   
    ╚═╝     ╚═════╝     ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
    """)
    print("="*50)
    
    script_dir = Path(__file__).parent
    
    while True:
        print("\nPodaj nazwę pliku ze zdjęciem (np. zdjecie.jpg):")
        filename = input("> ").strip()
        
        if not filename:
            print("\n❌ Błąd: Nazwa pliku nie może być pusta!")
            continue
            
        image_path = script_dir / filename
        
        if not image_path.exists():
            print(f"\n❌ Błąd: Plik {filename} nie istnieje w folderze {script_dir}")
            continue
            
        if image_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
            print("\n❌ Błąd: Plik musi być w formacie JPG lub PNG")
            continue
            
        break

    uploader = FacebookStoryUploader()
    success = uploader.upload_story(str(image_path))
    
    print("\n" + "="*50)
    print("✓ Relacja dodana pomyślnie!" if success else "❌ Wystąpił błąd podczas dodawania relacji!")
    print("="*50 + "\n")
