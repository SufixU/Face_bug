import requests
import re
import json
import time
import os

def extract_token(patterns, text, token_name):
    if isinstance(patterns, str):
        patterns = [patterns]
    for pattern in patterns:
        try:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1)
        except re.error:
            continue 
    return None

def load_cookies_from_file(filename='cookies.json'):
    cookies = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
            
            if isinstance(cookies_data, list):
                for cookie in cookies_data:
                    key = cookie.get('name') or cookie.get('key')
                    value = cookie.get('value')
                    
                    if key and value:
                        cookies[key] = value
            
            elif isinstance(cookies_data, dict):
                cookies = cookies_data
            
            return cookies if cookies else None

    except FileNotFoundError:
        print("[-] Błąd: Nie znaleziono pliku cookies.json")
        return None
    except json.JSONDecodeError:
        print("[-] Błąd: Niepoprawny format pliku cookies.json")
        return None
    except Exception as e:
        print(f"[-] Błąd: {str(e)}")
        return None

def save_error_log(error_type, details):
    error_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "error_type": error_type,
        "details": details
    }
    try:
        with open('fb_error_log.json', 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=4)
    except Exception as e:
        print(f"[-] Nie można zapisać logu błędu: {str(e)}")

def analyze_response(response, cookies):
    results = {
        'id_in_cookies': bool(cookies.get('c_user')),
        'no_login_form': 'login_form' not in response.text.lower(),
        'has_navigation': 'navigation' in response.text.lower(),
        'has_xs': bool(cookies.get('xs')),
    }
    return results

def print_analysis(response, cookies):
    print("\n[] Łączenie z Facebookiem...")
    print(f"[+] Status HTTP: {response.status_code}")
    print(f"[+] URL końcowy: {response.url}")
    if response.status_code == 200:
        print("[+] Połączenie udane!")

    results = analyze_response(response, cookies)
    
    print("\n[] Analiza odpowiedzi:")
    print(f"  {'[OK]' if results['id_in_cookies'] else '[FAIL]'} ID użytkownika w cookies: {results['id_in_cookies']}")
    print(f"  {'[OK]' if results['no_login_form'] else '[FAIL]'} Brak formularza logowania: {results['no_login_form']}")
    print(f"  {'[OK]' if results['has_navigation'] else '[FAIL]'} Obecność nawigacji: {results['has_navigation']}")
    print(f"  {'[OK]' if results['has_xs'] else '[FAIL]'} Cookie xs obecne: {results['has_xs']}")

def print_token_results(tokens_found):
    print("\n" + "="*60)
    print("[] WYCIĄGANIE TOKENÓW:")
    print("="*60)

    token_checks = [
        ('dtsg_token', 'DTSGToken'),
        ('dtsg_init', 'DTSGInitialData'),
        ('lsd_token', 'LSD Token'),
        ('jazoest', 'JAZOEST'),
        ('spin_r', 'Spin Token'),
        ('rev_token', 'Rev Token'),
        ('server_rev', 'Server Revision'),
        ('client_rev', 'Client Revision'),
        ('hsi', 'HSI'),
        ('connection_class', 'Connection Class')
    ]

    found_any = False
    for key, display_name in token_checks:
        value = tokens_found.get(key)
        if value:
            found_any = True
            print(f"[+] {display_name}: {value}")
    
    if not found_any:
        print("[-] Nie znaleziono żadnych tokenów")
        print("\n[!] UWAGA: Nie można znaleźć tokenów")
        print("[!] Prawdopodobnie problem z dostępem")
    
    print("="*60)
    print("[] Sprawdzanie zakończone")

def main():
    cookies = load_cookies_from_file('cookies.json')
    if cookies is None:
        save_error_log("COOKIE_ERROR", {
            "reason": "Nie można wczytać cookies",
            "file": "cookies.json"
        })
        print("\n" + "="*60)
        print("[!] BŁĄD KRYTYCZNY: Nie można kontynuować bez cookies!")
        print("[!] Upewnij się, że:")
        print("    - Plik cookies.json istnieje")
        print("    - Format pliku jest poprawny")
        print("    - Masz uprawnienia do odczytu pliku")
        print("="*60 + "\n")
        return

    if not cookies.get('c_user') or not cookies.get('xs'):
        save_error_log("INVALID_COOKIES", {
            "missing_cookies": {
                "c_user": not bool(cookies.get('c_user')),
                "xs": not bool(cookies.get('xs'))
            }
        })
        print("\n" + "="*60)
        print("[!] BŁĄD: Brak wymaganych cookies (c_user lub xs)!")
        print("="*60 + "\n")
        return

    print("\n" + "="*60)
    print("[*] DIAGNOSTYKA POŁĄCZENIA")
    print("="*60)
    print(f"[+] Znaleziono c_user: {cookies.get('c_user', 'BRAK!')}") 
    print(f"[+] Znaleziono xs: {'TAK' if cookies.get('xs') else 'NIE'}")
    print("="*60 + "\n")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl-PL,pl;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'DNT': '1',
    }

    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(headers)

    try:
        print("[*] Inicjalizacja połączenia z Facebookiem...")
        response = session.get(
            'https://www.facebook.com/',
            timeout=15,
            allow_redirects=True
        )

        print_analysis(response, cookies)

        if '/login' in response.url:
            save_error_log("LOGIN_REDIRECT", {
                "url": response.url,
                "cookies_expired": True
            })
            print("\n" + "="*60)
            print("[!] BŁĄD LOGOWANIA: Przekierowanie do strony logowania")
            print("[!] Prawdopodobne przyczyny:")
            print("    - Cookies wygasły")
            print("    - Cookies są nieprawidłowe")
            print("    - Sesja została zakończona przez Facebook")
            print("[>] Zalecenie: Zaloguj się ponownie i wyeksportuj świeże cookies")
            print("="*60 + "\n")
            return

        if '/checkpoint' in response.url:
            save_error_log("CHECKPOINT", {
                "url": response.url,
                "checkpoint_type": "security_check",
                "user_id": cookies.get('c_user')
            })
            print("\n" + "="*60)
            print("[!] CHECKPOINT WYKRYTY!")
            print("[!] Facebook wymaga weryfikacji bezpieczeństwa")
            print("[!] Możliwe przyczyny:")
            print("    - Nietypowa aktywność")
            print("    - Logowanie z nowej lokalizacji")
            print("    - Wymagana weryfikacja dwuetapowa")
            print("[>] Zalecenie: Zaloguj się przez przeglądarkę i przejdź proces weryfikacji")
            print("="*60 + "\n")
            return

        if response.status_code != 200:
            print("\n" + "="*60)
            print(f"[!] BŁĄD HTTP {response.status_code}")
            if response.status_code == 400:
                print("[!] Kod 400 sugeruje problem z żądaniem")
                print("[>] Sprawdź poprawność cookies i nagłówków")
            elif response.status_code == 403:
                print("[!] Kod 403 oznacza brak dostępu")
                print("[>] Możliwe tymczasowe blokowanie przez Facebook")
            elif response.status_code >= 500:
                print("[!] Błąd serwera Facebooka")
                print("[>] Spróbuj ponownie później")
            print("="*60 + "\n")
            return

        print("[*] Ekstrakcja tokenów w toku...")
        
        response_text = response.text
        
        token_patterns = {
            'dtsg_token': [
                r'"DTSGToken":"([^"]+)"',
                r'dtsg":\{"token":"([^"]+)"'
            ],
            'dtsg_init': [
                r'"DTSGInitialData",\[\],\{"token":"([^"]+)"',
                r'DTSGInitData",\[\],\{"token":"([^"]+)"'
            ],
            'lsd_token': [
                r'"LSD",\[\],\{"token":"([^"]+)"',
                r'"LSD":\[],{"token":"([^"]+)"'
            ],
            'jazoest': [
                r'name="jazoest" value="([^"]+)"',
                r'"jazoest":"([^"]+)"'
            ],
            'spin_r': [
                r'"__spin_r":(\d+)',
                r'"spin_r":(\d+)'
            ],
            'rev_token': [
                r'"__rev":(\d+)',
                r'"server_revision":(\d+)'
            ],
            'server_rev': [r'"server_revision":"([^"]+)"'],
            'client_rev': [r'"client_revision":"([^"]+)"'],
            'hsi': [r'"hsi":"([^"]+)"'],
            'connection_class': [r'"connection_class":"([^"]+)"']
        }

        tokens_found = {}
        for name, patterns in token_patterns.items():
            value = extract_token(patterns, response_text, name)
            tokens_found[name] = value

        print_token_results(tokens_found)

        if any(tokens_found.values()):
            with open('dump_Facebook_token.json', 'w', encoding='utf-8') as f:
                json.dump(tokens_found, f, indent=4)

    except requests.exceptions.Timeout:
        print("\n" + "="*60)
        print("[!] TIMEOUT: Przekroczono czas oczekiwania")
        print("[>] Sprawdź połączenie internetowe")
        print("[>] Facebook może być niedostępny")
        print("="*60 + "\n")
    except requests.exceptions.ConnectionError:
        print("\n" + "="*60)
        print("[!] BŁĄD POŁĄCZENIA")
        print("[>] Sprawdź:")
        print("    - Połączenie internetowe")
        print("    - Ustawienia proxy (jeśli używane)")
        print("    - Blokady firewalla")
        print("="*60 + "\n")
    except Exception as e:
        save_error_log("RUNTIME_ERROR", {
            "error_type": type(e).__name__,
            "error_message": str(e)
        })
        print("\n" + "="*60)
        print("[!] NIEOCZEKIWANY BŁĄD")
        print(f"[!] Typ błędu: {type(e).__name__}")
        print(f"[!] Szczegóły: {str(e)}")
        print("[>] Zgłoś ten błąd wraz z powyższymi szczegółami")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
