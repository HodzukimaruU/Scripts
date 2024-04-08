import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional


def getting_information_about_sushi_bars(urls: List[str]) -> List[Dict[str, Any]]:
    # Пустой список для хранения данных всех суши-баров
    sushi_bars_info: List[Dict[str, Any]] = []
    
    for url in urls:
        # Отправляем GET запрос к URL
        response = requests.get(url)
    
        if response.status_code == 200:
            # Создаем объект BeautifulSoup для парсинга HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find("script", string=lambda text: "window.initialState" in str(text))
        
            if script_tag:
                # Получаем содержимое скрипта
                script_content: Optional[str] = script_tag.string
            
                # Находим индекс начала и конца JSON-блока
                start_index: int = script_content.find('{', script_content.find("window.initialState"))
                end_index: int = script_content.rfind('}') + 1
            
                # Извлекаем JSON-блок
                json_data: Dict[str, Any] = json.loads(script_content[start_index:end_index])
            
                # Получаем информацию о магазинах
                shops: List[Dict[str, Any]] = json_data.get("shops", [])

                # Извлекаем город из ссылки
                city: str = soup.find("a", class_="city-select__current link link--underline").get_text(strip=True)
                
                for shop in shops:
                    name: str = shop.get('geoPoint')
                    address: str = shop.get('address')
                    address: str = city + ", " + address
                    latitude: float = shop.get('coord', {}).get('latitude')
                    longitude: float = shop.get('coord', {}).get('longitude')
                    schedule: List[Dict[str, str]] = shop.get('schedule', [])

                    # Извлекаем номер телефона
                    phone_element = soup.find("div", class_="contacts__phone")
                    phone_number: Optional[str] = None
                    if phone_element:
                        phone_number = phone_element.find("a").text.strip()
                
                    # Формируем объект для данного суши-бара
                    sushi_bar: Dict[str, Any] = {
                        "name": name,
                        "address": address,
                        "coordinates": [latitude, longitude],
                        "phone_number": phone_number,
                        "working_hours": [f"{entry['openTime']} - {entry['closeTime']}" for entry in schedule]
                    }
                
                    sushi_bars_info.append(sushi_bar)
                
            else:
                print("Script with window.initialState not found.")
                
        else:
            print("Error executing request:", response.status_code)
    
    return sushi_bars_info

urls: List[str] = [
        "https://omsk.yapdomik.ru/",
        "https://achinsk.yapdomik.ru/",
        "https://berdsk.yapdomik.ru",
        "https://krsk.yapdomik.ru",
        "https://nsk.yapdomik.ru",
        "https://tomsk.yapdomik.ru"
            ]

## Вызываем функцию и получаем информацию
sushi_addresses: List[Dict[str, Any]] = getting_information_about_sushi_bars(urls)

# Записываем информацию в JSON файл
with open('sushi_info.json', 'w', encoding='utf-8') as f:
    json.dump(sushi_addresses, f, ensure_ascii=False, indent=4)

if sushi_addresses:
    print("Information about sushi-bars has been successfully saved to the file sushi_addresses.json")
    print("Information about sushi-bars:")
    for address in sushi_addresses:
        print(address)
