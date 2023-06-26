from bs4 import BeautifulSoup
import requests as r

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
    soup = BeautifulSoup(page.text, "html.parser")
    return soup

