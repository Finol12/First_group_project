from bs4 import BeautifulSoup
import requests as r
import re
import lxml
import cchardet

def get_locality(wp_soup):
    """This function receives a 'soup' from a specific webpage
    containing an ad for a property and process it in order to
    find the location of such property"""

    #my code goes here and after it found the relevant information
    #it returns a dictionary containing the type of data I'm returning
    #and the value

    result_of_my_code = "Antwerp"
    return {"Location" : result_of_my_code}

def get_url(url):
    page = r.get(url)
    soup = BeautifulSoup(page.content, "lxml")
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

