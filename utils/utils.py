from bs4 import BeautifulSoup
import requests as r
import re
import json
import asyncio
from httpx import AsyncClient
import pandas as pd
#import lxml
#import cchardet

succesful_pages = 0
number_of_pages = 10
errors = 0
log = "\n"
go_up = '\033[1A'
clean_line = '\x1b[2K'
print("\n")

def progress():
    """Prints the current status of the scrape process"""
    print(go_up*2,end=clean_line)
    print("Succesfull pages: ", succesful_pages,
      f"({round(succesful_pages/(2*number_of_pages*0.3),1)}%)",
      " errors: ", errors,f" ({round(errors/succesful_pages,3)}%)", end="\n\n")

def get_locality(wp_soup):
    """Receives a soup object from a immoweb listing and
    return the  locality of the listing"""
    data = get_classified_data_layer(wp_soup)
    try:
        result = data["property"]["location"]["locality"]
    except:
        result = None
    return result

def get_postalcode(wp_soup):
    """Receives a soup object from a immoweb listing and
    return the postal code of the listing"""
    data = get_data_layer(wp_soup)
    try:
        result = data["classified"]["zip"]
    except:
        result = 0
    return result

def get_subtype_of_propert(wp_soup):
    """Receives a soup object from a immoweb listing and
    return the subtype of the listing"""
    data = get_data_layer(wp_soup)
    try:
        x=data["classified"]["subtype"]
    except:
        x=None
    return x

def get_type_of_property(wp_soup):
    """Receives a soup object from a immoweb listing and
    return the type of the listing"""
    data = get_data_layer(wp_soup)
    try:
        x=data["classified"]["type"]
    except:
        x=None
    return x

def get_price(wp_soup):
    """Receives a soup object from a immoweb listing and
    return the listing price"""
    data = get_data_layer(wp_soup)
    try:
        x=data["classified"]["price"]
    except:
        x=None
    return x

def get_kitchen(wp_soup):
    """Receives a soup object from a immoweb listing and
    return the type of kitchen it has"""
    data = get_data_layer(wp_soup)
    try:
        x= data["classified"]["kitchen"]["type"]
    except:
        x = None
    return x

def get_num_of_bedrooms(wp_soup):
    """Receives a soup object from a immoweb listing and
    return the number of bedrooms it has"""
    data = get_data_layer(wp_soup)
    try:
        x=data["classified"]["bedroom"]["count"]
    except:
        x=None
    return x

def get_swimming_pool(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns whether the listing has a swimming pool"""
    data = get_data_layer(wp_soup)
    try:
        x = data["classified"]["wellnessEquipment"]["hasSwimmingPool"]
        if x =="true":
            answer = True
        else:
            answer = False
    except:
        answer = False
    return answer

def get_garden(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns whether the listing has a garden"""
    data = get_classified_data_layer(wp_soup)
    try:
        x=data["property"]["hasGarden"]
    except:
        x= False
    return x

def get_garden_area(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns the surface of the garden. Returns None if it has
    no garden"""
    data = get_data_layer(wp_soup)
    try:
        x = data["classified"]["outdoor"]["garden"]["surface"]
    except:
        x = None
    return x

def get_terrace(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns whether the listing has a terrace"""
    data = get_data_layer(wp_soup)
    try:
        terrace= data["classified"]["outdoor"]["terrace"]["exists"]
        x =True
    except:
        x = False
    return x

def get_surface_of_land(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns the surface of the land"""
    data = get_data_layer(wp_soup)
    try:
        x = data["classified"]["land"]["surface"]
    except:
        x = None
    return x

def get_listing_id(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns the immoweb unique id"""
    data = get_classified_data_layer(wp_soup)
    try:
        x= data["id"]
    except:
        x= None
    return x

def get_listing_address(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns the address of the listing"""
    data = get_classified_data_layer(wp_soup)
    try:
        x= f"{data['property']['location']['street']} {data['property']['location']['number']}"
    except:
        x= None
    return x

def get_living_area(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns the living area of the listing"""
    data = get_classified_data_layer(wp_soup)
    try:
        x=data["property"]["netHabitableSurface"]
    except:
        x= None
    return x

def get_open_fire(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns whether the listing contains a fire place"""
    data = get_classified_data_layer(wp_soup)
    try:
        x=data["property"]["fireplaceExists"]
    except:
        x= False
    return x

def get_furnished(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns whether the listing is furnished"""
    data = get_classified_data_layer(wp_soup)
    try:
        x=data["transaction"]["sale"]["isFurnished"]
    except:
        x= False
    return x


def get_facade_count(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns the number of facades"""
    data = get_classified_data_layer(wp_soup)
    try:
        x=data["property"]["building"]["facadeCount"]
    except:
        x= None
    return x

def get_state_of_the_building(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns the condition of the building"""
    data = get_classified_data_layer(wp_soup)
    try:
        x=data["property"]["building"]["condition"]
    except:
        x= None
    return x

def get_data_layer(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns a dictionary containing data from the javascript
    windows.data_layer object"""
    tags = wp_soup.find_all("script")
    script=['']
    for tag in tags:
        if "window.dataLayer = " in tag.text:
            script=json.loads(tag.text.split("window.dataLayer = ")[1][:-2])
    return script[0]

def get_classified_data_layer(wp_soup):
    """Receives a soup object from a immoweb listing and
    returns a dictionary containing data from the javascript
    windows.data_classified_layer object"""
    tags = wp_soup.find_all("script")
    script={}
    for tag in tags:
        if "window.classified = " in tag.text:
            script=json.loads(re.search(r"\{.*\}(?:;)", tag.text).group(0)[:-1])
    return script

async def get_soup(url, session=None):
    """Receives a url and returns a beautifulsoup object from that
    url. If session is passed uses that session otherwise uses a
    default requests session"""
    if session:
        page = await session.get(url)
    else:
        page = r.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

async def url_dictionary(url, session):
    """For a given immoweb url, returns a dictionary containing
    information about that url.Keeps track of succesful and unsuccesful
    attempts. If an exception occurs when retrieving the data, add to
    the log and raise it."""
    global errors
    global succesful_pages
    global log
    url_dic = {}
    try:
        soup = await get_soup(url, session)
        url_dic["URL"] = url
        url_dic["Listing_ID"] = get_listing_id(soup)
        url_dic["Type"] = get_type_of_property(soup)
        url_dic["Subtype"] = get_subtype_of_propert(soup)
        url_dic["Price"] = get_price(soup)
        url_dic["Bedroom"] = get_num_of_bedrooms(soup)
        url_dic["Living_area"] =get_living_area(soup)
        url_dic["Listing_address"] = get_listing_address(soup)
        url_dic["Postal_code"] = get_postalcode(soup)
        url_dic["Locality"] = get_locality(soup)
        url_dic["Swimming_pool"] = get_swimming_pool(soup)
        url_dic["Garden"] = get_garden(soup)
        url_dic["Garden_area"] = get_garden_area(soup)
        url_dic["Surface_of_land"] = get_surface_of_land(soup)
        url_dic["Terrace"] = get_terrace(soup)
        url_dic["Kitchen"] = get_kitchen(soup)
        url_dic["Facade"] = get_facade_count(soup)
        url_dic["Open Fire"] = get_open_fire(soup)
        url_dic["Furnished"] = get_furnished(soup)
        url_dic["State of the building"] = get_state_of_the_building(soup)
        succesful_pages+=1
        progress()
        return url_dic
    except Exception as e:
        print(go_up,end=clean_line)
        print("Error on single page: ",e)
        errors += 1
        log += e.__str__() + "\n"
        progress()
        raise e


async def get_data_per_page(url, session=None):
    """Returns a list containing data (dicts) from each immoweb
    listings on url.
    If session is passed uses it, otherwise uses request.Sessions"""
    must_close = False
    if not session:
        must_close = True
        session = AsyncClient()
    soup = await get_soup(url, session)
    if soup:
        results = []
        tasks = []
        links = soup.find_all("a", attrs={'class' : 'card__title-link'})
        for link in links:
            if ("immoweb.be/en/classified" in link["href"]
                and link.parent.name != "h2"):
                tasks.append(
                    asyncio.create_task(url_dictionary(link["href"], session)))
        results = await asyncio.gather(*tasks,return_exceptions=True)
        results[:] = [x for x in results if not isinstance(x, Exception)]
    else:
        print(go_up,end=clean_line)
        print("Error on page, could not get links")
        results = []
    if must_close:
        await session.aclose()
    return results

async def request_links_pages(type_property):
    """For a given 'type_propety', loop through the pages containing
    groups of listings (30 per page) asynchronously using asyncio.
    Returns a list containing the results for each individual link
    inside each individual page"""
    global log
    tasks = []
    consolidated_results=[]
    async with AsyncClient(timeout=20) as session:
        for x in range(1, number_of_pages+1):
            url = ("https://www.immoweb.be/en/search/"
                   + type_property
                   + "/for-sale?countries=BE&&isALifeAnnuitySale=false"
                   + "&page=" + str(x) + "&orderBy=relevance")
            tasks.append(
                asyncio.create_task(get_data_per_page(url, session)))
        results = await asyncio.gather(*tasks,return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print("Error in the page request: " + result.__str__())
            else:
                consolidated_results.extend(result)
    return consolidated_results

def consolidate_data():
    """Returns a list of all property data from both 'house' and
    'apartment' types."""
    results = asyncio.run(request_links_pages("house"))
    results.extend(asyncio.run(request_links_pages("apartment")))
    return results

def create_dataframe():
    """Create a DataFrame object from data received from consolidate_data
    and returns it."""
    treasure_chest = consolidate_data()
    with open("error_logs.log","w") as log_file:
        log_file.write(log)
    if not treasure_chest:
        return pd.DataFrame()
    print("Creating Data Frame...")
    main_df = pd.DataFrame.from_records(treasure_chest)
    print("Done!")
    print(main_df)
    return main_df

def create_csv():
    """Create a csv from the Dataframe returned by create_dataframe()
    and writes it to file 'final-csv.csv'"""
    main_df = create_dataframe()
    main_df.to_csv("final-csv.csv", index=False)
    return main_df
