import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict


def scrape_dentalia_info(url: str) -> List[Dict[str, str]]:
    # Список для хранения информации о клиниках
    dentalia_info: List[Dict[str, str]] = []
    # Отправляем GET запрос к URL
    response = requests.get(url)

    # Проверяем успешность запроса
    if response.status_code == 200:
        # Создаем объект BeautifulSoup для парсинга XML
        soup = BeautifulSoup(response.text, "xml")
        # Находим элемент <channel>
        channel = soup.find("channel")
        if channel:
            # Находим все элементы item внутри блока channel
            items = channel.find_all("item")

            for item in items:
                # Находим ссылку на страницу клиники
                link_tag = item.find("link")

                if link_tag:
                    link = link_tag.text
                    response = requests.get(link)

                    if response.status_code == 200:
                        # Создаем объект BeautifulSoup для парсинга HTML
                        inner_soup = BeautifulSoup(response.text, 'html.parser')

                        # Извлекаем название клиник
                        name = inner_soup.find("h1", class_="elementor-heading-title elementor-size-default").get_text(strip=True).replace('\xa0', ' ')

                        # Извлекаем адрес клиники
                        address_tag = inner_soup.find("div", class_="jet-listing-dynamic-field__content")
                        address = re.sub(r'[^\x00-\x7F]+', ' ', address_tag.get_text(strip=True)) if address_tag else "Address not found"
                        address = address.replace('\r\n', ', ')

                        # Извлекаем номера телефонов
                        phone_tag = inner_soup.find("div", class_="jet-listing-dynamic-field__content", text=lambda text: "Teléfono(s):" in text)
                        phone_number = phone_tag.get_text(strip=True).replace("Teléfono(s):", "").replace('\r\n', ', ') if phone_tag else "Phone number not found"
                        phone_number = phone_number.strip()

                        # Извлекаем часы работы клиники
                        hours_tag = inner_soup.find("div", class_="jet-listing-dynamic-field__content", text=lambda text: "Horario:" in text)
                        hours = hours_tag.get_text(strip=True).replace("Horario:", "").replace('\r\n', ', ') if hours_tag else "Hours not found"
                        hours = hours.strip()
                        
                        coordinates = None

                        # Создаем объект
                        clinics = {
                            "name": name,
                            "address": address,
                            "coordinates": coordinates,
                            "phone_number": phone_number,
                            "hours": hours
                        }

                        # Добавляем информацию о клинике в список
                        dentalia_info.append(clinics)
                    else:
                        print("Failed to parse link:")
        else:
            print("Failed to find channel in XML")
    else:
        print("Error executing request:", response.status_code)

    return dentalia_info

url = "https://dentalia.com/clinica/feed"

# Вызываем функцию для парсинга информации и получаем список с данными о клиниках
all_dentalia_info: List[Dict[str, str]] = scrape_dentalia_info(url)

# Записываем данные в JSON файл
with open("dentalia_info.json", "w", encoding='utf-8') as f:
    json.dump(all_dentalia_info, f, indent=4, ensure_ascii=False)

if all_dentalia_info:
    print("The information was successfully saved to the file: dentalia_info.json")
    print("Information about clinics: ")
    for address_info in all_dentalia_info:
        print(address_info)
