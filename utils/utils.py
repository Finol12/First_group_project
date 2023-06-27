from bs4 import BeautifulSoup
import requests as r
import re
import json
#import lxml
#import cchardet

def get_locality(wp_soup):
    data = get_data_layer(wp_soup)
    return data["classified"]["zip"]

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

def get_url(url):
    page = r.get(url)
#    soup = BeautifulSoup(page.content, "lxml")
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

def url_dictionary(url):
    soup = get_url(url)
    url_dic = {}
    url_dic["URL"] = url
    url_dic["Type"] = get_type_of_property(soup) 
    url_dic["Subtype"] = get_subtype_of_propert(soup)
    url_dic["Price"] = get_price(soup)
    url_dic["Bedroom"] = get_num_of_bedrooms(soup)
    url_dic["Living_area"] =get_living_area(soup)
    url_dic["Locality"] = get_locality(soup)
    return url_dic