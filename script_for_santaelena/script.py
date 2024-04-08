import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Any, Optional
from get_coordinates import get_coordinates


def getting_information_about_restaurants(urls: List[str]) -> List[Dict[str, Any]]:

    # Пустой список для хранения данных всех ресторанов
    all_restaurant_info: List[Dict[str, Any]] = []

    for url in urls:
        # Отправляем GET запрос к URL
        response = requests.get(url)

        if response.status_code == 200:
            # Создаем объект BeautifulSoup для парсинга HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Находим все блоки с информацией о ресторанах
            restaurant_blocks = soup.find_all("div", class_="elementor-column-wrap")
            restaurant_info_list = []
            addresses = []

            # Извлекаем город из ссылки
            link_part = soup.find("a", class_="elementor-sub-item elementor-item-active").get_text(strip=True)
            last_word_link_part = link_part.split()[-1]

            for block in restaurant_blocks:
                # Извлекаем название ресторана, если блок существует
                name_block = block.find("div", class_="elementor-widget-container")
                if name_block:
                    name_element = name_block.find("h3")
                    if name_element:
                        name: str = name_element.get_text(strip=True)
                    else:
                        name = ""
                else:
                    name = ""

                text = block.get_text()

                # Проверяем, содержит ли текст ключевые фразы для информации о ресторане
                if "Dirección" in text:
                    
                    # Извлекаем адрес
                    address_start_index = text.find("Dirección") + len("Dirección")
                    address_end_index = text.find("Teléfono") if "Teléfono" in text else text.find("Horario de atención")

                    address: str = text[address_start_index:address_end_index].strip().replace('\xa0', ' ')
                    address = address.replace("\n", "").strip()
                    address = last_word_link_part + " " + address

                    # Извлекаем телефон
                    if "Teléfono" not in text:
                        phone: Optional[str] = None
                    else:
                        phone_start_index = text.find("Teléfono") + len("Teléfono")
                        phone_end_index = text.find("Horario de atención")
                        phone = text[phone_start_index:phone_end_index].strip()
                        
                        # Удаляем лишние двоеточия из номера телефона
                        phone = phone.replace(":", "").strip()

                    # Извлекаем часы работы
                    hours_start_index = text.find("Horario de atención:") + len("Horario de atención:")
                    hours_text = text[hours_start_index:].strip().replace("Cómo llegar", "")
                    # Разделяем текст по символу новой строки, исключая пустые строки и первую строку с названием
                    hours = [line.strip() for line in hours_text.split('\n') if line.strip() and line.strip() != "Horario de atención"]
                    # Удаляем пустые элементы из списка часов работы
                    hours = list(filter(lambda x: x != ":", hours))

                    # Формируем объект для данного ресторана
                    restaurant_info: Dict[str, Any] = {
                        "name": name,
                        "address": address,
                        "phone": phone,
                        "working_hours": hours
                    }
                    restaurant_info_list.append(restaurant_info)
                    addresses.append(address)

            # Получаем координаты для адресов
            coordinates_list = get_coordinates(address_list=addresses)

            # Добавляем координаты к информации о ресторанах
            for i in range(min(len(restaurant_info_list), len(coordinates_list))):
                restaurant_info_list[i]["coordinates"] = coordinates_list[i]
            all_restaurant_info.extend(restaurant_info_list)
        else:
            print("Error executing request:", response.status_code)
    return all_restaurant_info

urls: List[str] = [
    "https://www.santaelena.com.co/tiendas-pasteleria/tienda-medellin/",
    "https://www.santaelena.com.co/tiendas-pasteleria/tienda-bogota/",
    "https://www.santaelena.com.co/tiendas-pasteleria/tienda-monteria/",
    "https://www.santaelena.com.co/tiendas-pasteleria/tiendas-pastelerias-pereira/",
    "https://www.santaelena.com.co/tiendas-pasteleria/nuestra-pasteleria-en-barranquilla-santa-elena/"
]

# Вызываем функцию и получаем информацию
restaurant_info: List[Dict[str, Any]] = getting_information_about_restaurants(urls)

# Записываем данные в JSON файл
with open("restaurant_info.json", 'w', encoding='utf-8') as f:
    json.dump(restaurant_info, f, ensure_ascii=False, indent=4)

if restaurant_info:
    print("Information about Restaurant has been successfully saved to the file sushi_addresses.json")
    print("Restaurant information: ")
    for info in restaurant_info:
        print(info)
