from bs4 import BeautifulSoup
import requests as r
import re
import json
#import lxml
#import cchardet

def get_locality(wp_soup):
    data = get_data_layer(wp_soup)
    return data["classified"]["zip"]

def get_data_layer(wp_soup):
    tags = wp_soup.find_all("script")
    for tag in tags:
        if "window.dataLayer = " in tag.text:
            script = json.loads(tag.text.split("window.dataLayer = ")[1][:-2])
    return script[0]

def get_classified_data_layer(wp_soup):
    tags = wp_soup.find_all("script")
    for tag in tags:
        if "window.classified = " in tag.text:
            script = json.loads(re.search(r"\{.*\}(?:;)", tag.text).group(0)[:-1])
    return script

def get_living_area(wp_soup):
    data = get_classified_data_layer(wp_soup)
    return data["property"]["netHabitableSurface"]

def get_n_bedrooms(wp_soup):
    data = get_data_layer(wp_soup)
    return data["classified"]["bedroom"]["count"]

def get_url(url):
    page = r.get(url)
#    soup = BeautifulSoup(page.content, "lxml")
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

def find_price(immo_soup):
    in_span = []
    span_lookup = immo_soup.find_all("span")

    for things in span_lookup:
        line_lookup = things.get_text()
        in_span.append(line_lookup)
    prices = []
    for string in in_span:
        cleaned_string = string.replace("\n", "")
        match = re.search(r"(?:\b€)?(\d{1,3}(?:[.,]\d{3})*€?)\b", cleaned_string)
        if match:
            prices.append(match.group(0).replace(',', ''))
        else:
            pass
    price = 0
    for num in prices:
        if len(num) >= 7:
            price += int(num)
    return price

def get_type_of_property(soup):
    type_of_building = soup.find("h1", attrs={"class": "classified__title"}).get_text()
    types_of_houses=["house", "villa", "huis"]
    for word in types_of_houses :
        if word in type_of_building.lower():
            answer = "House"
            break
    types_of_appartments=["appartments", "apps"]
    for word in types_of_appartments :
        if word in type_of_building.lower():
            answer= "Apartment"
            break
    return answer
