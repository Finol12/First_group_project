from bs4 import BeautifulSoup
import requests as r
import re

def get_locality(wp_soup):
    """This function receives a 'soup' from a specific webpage
    containing an ad for a property and process it in order to
    find the location of such property"""
    result = 0
    #print(wp_soup.prettify())
    pattern = r'\"locality\":.*,'
    print(re.match(pattern,wp_soup.prettify()))
#    for tag in wp_soup.find_all("span"):
#        #, attrs={'class':'classified__information'}):
#        print(tag.text)

    #result_of_my_code = "Antwerp"
    #return {"Location" : result_of_my_code}

def get_no_bedrooms(wp_soup):
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

