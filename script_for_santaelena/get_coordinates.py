import requests
from tqdm import tqdm
from typing import List, Dict, Optional, Tuple

def get_coordinates(address_list: List[str]) -> List[Optional[Tuple[float, float]]]:
    coordinates_list: List[Optional[Tuple[float, float]]] = []
    with tqdm(total=len(address_list), desc="Optimizing route") as pbar:
        for address in address_list:
            delimiters: List[str] = ["–", ",", ";", " Frente", " - "]
            for delimiter in delimiters:
                address = address.split(delimiter)[0].strip()

            url: str = "https://nominatim.openstreetmap.org/search"
            params: Dict[str, str] = {"q": address, "format": "json"}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    coordinates_list.append((lat, lon))
                else:
                    print("Coordinates not found for address:", address)
                    coordinates_list.append(None)
            else:
                print("Error executing request:", response.status_code)
            pbar.update(1)
    return coordinates_list
