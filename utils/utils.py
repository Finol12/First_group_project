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

def get_living_area(wp_soup):
    result = 0
    tag = wp_soup.find("path", {'d':"M4 .22L.1 3.75l.46.5.44-.4v3.48c0 .19.15.34.33.34h2v-2h1.34v2h2A.33.33 0 007 7.33V3.85l.44.4.45-.5L4 .22zm.67 4.11H3.33V3h1.34v1.33z"})
    result = int((tag.parent.parent.span.contents[0].strip()))
    return result

def get_n_bedrooms(wp_soup):
    result = 0
    tag = wp_soup.find("path", {'d':"M7 2.05H1V.7c0-.2.13-.33.33-.33h5.34c.2 0 .33.13.33.33v1.34zm.9 2.66H.1l.87-2h6.06l.87 2zM0 7.38v-2h8v2c0 .2-.13.33-.33.33s-.34-.13-.34-.33v-.67H.67v.67c0 .2-.14.33-.34.33S0 7.58 0 7.38z"})
    numbers = tag.parent.parent.span.contents[0].strip()
    result = int(''.join(c for c in numbers if c.isdigit()))
    return result

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
    types_of_appartments=["appartments","duplex" ,"apps"]
    for word in types_of_appartments :
        if word in type_of_building.lower():
            answer= "Apartment"
            break
    return answer
