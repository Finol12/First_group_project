from bs4 import BeautifulSoup
import requests as r
import re
import time
def get_locality(wp_soup):
    """This function receives a 'soup' from a specific webpage
    containing an ad for a property and process it in order to
    find the location of such property"""

    #my code goes here and after it found the relevant information
    #it returns a dictionary containing the type of data I'm returning
    #and the value

    result_of_my_code = "Antwerp"
    return {"Location" : result_of_my_code}

def get_living_area(wp_soup):
    result = 0
    for tag in wp_soup.find_all("path", attrs={'d':'M4 .22L.1 3.75l.46.5.44-.4v3.48c0 .19.15.34.33.34h2v-2h1.34v2h2A.33.33 0 007 7.33V3.85l.44.4.45-.5L4 .22zm.67 4.11H3.33V3h1.34v1.33z'}):
        print(tag.parent.parent)
        for sub in tag.parent.parent:
            print(sub.text.strip().isnumeric())
            print(sub.text)
            print("done")
            if sub.name == "span" and sub.text.strip().isnumeric():
                    print(sub.text)
    return result

def get_n_bedrooms(wp_soup):
    result = 0
    for tag in wp_soup.find_all("span", attrs={'class':'overview__text'}):
        if "bedroom" in tag.text.lower():
            digits = [x for x in tag.text.split() if x.isdigit()]
            if len(digits) > 0:
                result = int(*digits)
            break
    return result

def get_url(url):
    page = r.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    return soup

def get_type_of_property(soup):
    type_of_bulding = soup.find("h1" , attrs={"class":"classified__title"}).get_text()
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
