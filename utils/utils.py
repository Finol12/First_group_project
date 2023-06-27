from bs4 import BeautifulSoup
import requests as r
import re
import json
#import lxml
#import cchardet

def get_locality(wp_soup):
    """Function receives a soup object from a immoweb listing and return the zip code of the listing"""
    data = get_data_layer(wp_soup)
    try:
        result = data["classified"]["zip"]
    except:
        result = 0
    return result

def get_subtype_of_propert(wp_soup):
    data = get_data_layer(wp_soup)
    return data["classified"]["subtype"]

def get_type_of_property(wp_soup):
    data = get_data_layer(wp_soup)
    return data["classified"]["type"]

def get_price(wp_soup):
    data = get_data_layer(wp_soup)
    return data["classified"]["price"]

def get_num_of_bedrooms(wp_soup):
    data = get_data_layer(wp_soup)
    return data["classified"]["bedroom"]["count"]

def get_swimming_pool(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x = data["classified"]["wellnessEquipment"]["hasSwimmingPool"]
        if x =="true":
            answer = "Yes"
        else:
            answer = "No"
    except:
        answer = "No"
    return answer

def get_garden_area(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x = data["classified"]["outdoor"]["garden"]["surface"]
    except:
        x = 0
    return x

def get_surface_of_land(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x = data["classified"]["land"]["surface"]
    except:
        x = 0
    return x

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

def get_soup(url):
    page = r.get(url)
#    soup = BeautifulSoup(page.content, "lxml")
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

def url_dictionary(url):
    soup = get_soup(url)
    url_dic = {}
    url_dic["URL"] = url
    url_dic["Type"] = get_type_of_property(soup)
    url_dic["Subtype"] = get_subtype_of_propert(soup)
    url_dic["Price"] = get_price(soup)
    url_dic["Bedroom"] = get_num_of_bedrooms(soup)
    url_dic["Living_area"] =get_living_area(soup)
    url_dic["Locality"] = get_locality(soup)
    url_dic["Swimming_pool"] = get_swimming_pool(soup)
    url_dic["Garden_area"] = get_garden_area(soup)
    url_dic["Surface_of_land"] = get_surface_of_land(soup)
    return url_dic

def get_urls_per_page(page_number):
    url = ("https://www.immoweb.be/en/search/house/for-sale?countries=BE&page="
           + page_number + "&orderBy=postal_code")
    print(url)
    soup = get_soup(url)
    links = soup.find_all("a", attrs={'class' : 'card__title-link'})
    #link = soup.find("article[id]")
    for link in links[1:]:
        #print(link["href"])
        info = url_dictionary(link["href"])
        print(info)
