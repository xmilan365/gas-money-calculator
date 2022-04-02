# imports
import requests
import config 
from unidecode import unidecode
from bs4 import BeautifulSoup

# constants
CONST_MATRIX_API_URL = "https://api.distancematrix.ai/maps/api/distancematrix/json?"
CONST_METRIX_API_KEY_TOKEN = config.MATRIX_API_TOKEN 
CONST_PETROL_URL = "https://www.globalpetrolprices.com/Slovakia/gasoline_prices/"
CONST_SPRITMONITOR_URL = "https://www.spritmonitor.de/en/"


# functions
def get_distance(api_key, api_site, a_location, b_location):
    parameters = {
        "origins": a_location,
        "destinations": b_location,
        "key": api_key,
        "mode": "driving"
    }
    response = requests.get(f"{api_site}", params=parameters)
    response.raise_for_status()
    data = response.json()
    lenght_km = data["rows"][0]["elements"][0]["distance"]["text"]
    lenght = float(lenght_km[:-2])
    print(f"Total distance from {a_location.title()} to {b_location.title()} is {lenght} km.")
    return lenght


def get_current_fuel_price(petrol_url):
    response = requests.get(petrol_url)
    response.raise_for_status()
    content = response.text
    soup = BeautifulSoup(content, "html.parser")
    gas_price = soup.findAll("td")[2].text
    gas_price = float(gas_price)
    print(f"Current price of gasoline is {gas_price} €/l.")
    return gas_price


def get_car_manuf_id(car, spritmonitor_url):
    response1 = requests.get(spritmonitor_url)
    response1.raise_for_status()
    content = response1.text
    soup = BeautifulSoup(content, "html.parser")
    items = soup.find("select",{"name":"manuf"}).select("option[value]")
    car_ids = [item.get('value') for item in items]
    car_manuf = [item.text for item in items]
    manuf_dict = dict(zip(car_manuf, car_ids))
    desired_car_manuf_id = manuf_dict[car]
    return desired_car_manuf_id


def get_car_model_id(model, spritmonitor_url):
    response1 = requests.get(spritmonitor_url)
    response1.raise_for_status()
    content = response1.text
    soup = BeautifulSoup(content, "html.parser")
    items = soup.find("select",{"name":"model"}).select("option[value]")
    car_model_ids = [item.get('value') for item in items]
    car_model = [item.text.title() for item in items]
    model_dict = dict(zip(car_model, car_model_ids))
    desired_car_model_id = model_dict[model]
    return desired_car_model_id


def get_car_consumption(car, model, fuel_type, spritmonitor_url):
    # first i need to check the number id by car
    car = car.title()
    car_id = get_car_manuf_id(unidecode(car), spritmonitor_url)

    # secondly, i need to check the number id of model
    model = model.title()
    car = car.replace(" ","_")
    spec_spritmonitor_url = f"{spritmonitor_url}overview/{car_id}-{unidecode(car)}/0-All_models.html?powerunit=2"
    model_id = get_car_model_id(unidecode(model), spec_spritmonitor_url)

    # finaly find consumtion based on fuel_type
    fuel_type = fuel_type.title()
    model = model.replace(" ","_")
    response = requests.get(f"{spritmonitor_url}overview/{car_id}-{unidecode(car)}/{model_id}-{unidecode(model)}.html?powerunit=2")
    response.raise_for_status()
    content = response.text
    soup = BeautifulSoup(content, "html.parser")
    tmp = soup.find("td", text=fuel_type)
    consumption_str = tmp.find_next_sibling("td", class_="consumption").text
    final_consumption_value = float(consumption_str.strip().replace(",", "."))
    print(f"\nConsumption of {car.replace('_', ' ')} {model.replace('_', ' ')} is {final_consumption_value} l/100km.")
    return final_consumption_value


def get_final_fuel_calc(consumtion, route_lenght, fuel_price):
    final_result = (((consumtion * route_lenght) // 100) * fuel_price)
    final_amount = round(final_result, 2)
    print(f"The final price of fuel for this journey is {final_amount} €.")


# inputs
origin = str(input("Origin town: "))
destination = str(input("Destination town: "))
vehicle = str(input("Vehicle manufacturer: "))
model = str(input("Model of car: "))
fuel_type = str(input("Fuel type: "))

# main functions
get_final_fuel_calc(consumtion=get_car_consumption(car=vehicle,
                                                   model=model,
                                                   fuel_type=fuel_type,
                                                   spritmonitor_url=CONST_SPRITMONITOR_URL),
                    route_lenght=get_distance(api_key=CONST_METRIX_API_KEY_TOKEN,
                                              api_site=CONST_MATRIX_API_URL,
                                              a_location=origin,
                                              b_location=destination),
                    fuel_price=get_current_fuel_price(petrol_url=CONST_PETROL_URL))
