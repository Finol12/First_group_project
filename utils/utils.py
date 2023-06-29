from bs4 import BeautifulSoup
import requests as r
import re
import json
import asyncio
from httpx import AsyncClient
import pandas as pd
import lxml
import cchardet

succesful_pages = 0
number_of_pages = 200
errors = 0
log = "\n"

def get_locality(wp_soup):
    """Function receives a soup object from a immoweb listing and
    return the zip code of the listing"""
    data = get_data_layer(wp_soup)
    try:
        result = data["classified"]["zip"]
    except:
        result = 0
    return result

def get_subtype_of_propert(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x=data["classified"]["subtype"]
    except:
        x=None
    return x

def get_type_of_property(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x=data["classified"]["type"]
    except:
        x=None
    return x

def get_price(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x=data["classified"]["price"]
    except:
        x=None
    return x

def get_kitchen(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x= data["classified"]["kitchen"]["type"]
    except:
        x = None
    return x

def get_num_of_bedrooms(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x=data["classified"]["bedroom"]["count"]
    except:
        x=None
    return x

def get_swimming_pool(wp_soup):
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

def get_garden_area(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x = data["classified"]["outdoor"]["garden"]["surface"]
    except:
        x = None
    return x

def get_terrace(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        terrace= data["classified"]["outdoor"]["terrace"]["exists"]
        x =True

    except:
        x = False
    return x

def get_surface_of_land(wp_soup):
    data = get_data_layer(wp_soup)
    try:
        x = data["classified"]["land"]["surface"]
    except:
        x = None
    return x

def get_data_layer(wp_soup):
    tags = wp_soup.find_all("script")
    script=['']
    for tag in tags:
        if "window.dataLayer = " in tag.text:
            script=json.loads(tag.text.split("window.dataLayer = ")[1][:-2])
    return script[0]

def get_classified_data_layer(wp_soup):
    tags = wp_soup.find_all("script")
    script={}
    for tag in tags:
        if "window.classified = " in tag.text:
            script=json.loads(re.search(r"\{.*\}(?:;)", tag.text).group(0)[:-1])
    return script

def get_living_area(wp_soup):
    data = get_classified_data_layer(wp_soup)
    try:
        x=data["property"]["netHabitableSurface"]
    except:
        x= None
    return x

async def get_soup(url, session=None):
    if session:
        page = await session.get(url)
    else:
        page = r.get(url)
    soup = BeautifulSoup(page.content, "lxml")
#    soup = BeautifulSoup(page.content, "html.parser")
    return soup

async def url_dictionary(url, session):
    global errors
    url_dic = {}
    try:
        soup = await get_soup(url, session)
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
        url_dic["Terrace"] = get_terrace(soup)
        url_dic["Kitchen"] = get_kitchen(soup)
        return url_dic
    except Exception as e:
        print("\nError on single page: ",e, end=
             "\033[1A\r")
        errors += 1
        raise e

def progress(task):
    global succesful_pages
    succesful_pages+=1
    print(" Succesfull pages: ", succesful_pages,
          f"({round(succesful_pages/(number_of_pages*0.3),1)}%)",
          " errors: ", errors,f" ({round(errors/succesful_pages,3)}%)",
          end="                                                        \r")

async def get_data_per_page(page_number, session=None):
    """Receives a 'page_number', then returns a dictionary containing
    data from each immoweb real estate advertisement on that page"""
    url = ("https://www.immoweb.be/en/search/house/for-sale?countries=BE&page="
           + str(page_number) + "&orderBy=postal_code")
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
        for task in tasks:
            task.add_done_callback(progress)
        try:
            results = await asyncio.gather(*tasks)
        except Exception as e:
            raise e
        #for index, result in enumerate(results):
        #    if isinstance(result, Exception):
        #        print("\n\n Deleting error after page is done \033[1A\033[1A\r ")
        #        results.pop(index)
    else:
        print("\n Error on page, could not get links \033[1A")
        results = []
    if must_close:
        await session.aclose()
    return results

async def consolidate_data():
    consolidated_results = []
    tasks = []
    async with AsyncClient(timeout=None) as session:
        for x in range(1, number_of_pages+1):
            tasks.append(
                asyncio.create_task(get_data_per_page(x, session)))
        try:
            results = await asyncio.gather(*tasks)
        except Exception as e:
            log +=e + "\n"
        for result in results:
            consolidated_results.extend(result)
        #    try:
        #        result
        #        consolidated_results.extend(result)
        #    except Exception as e:
        #        print("\nError in the page request: ", e)
        #        print("\n", result)
    return consolidated_results

def create_dataframe():
    treasure_chest = asyncio.run(consolidate_data())
    print("Writing log")
    with open("error_logs.log","w") as log_file:
        log_file.write(log)
    if not treasure_chest:
        return pd.DataFrame()
    print("\nCreating Data Frame...")
    main_df = pd.DataFrame.from_records(treasure_chest)
    print("Done!")
    print(main_df)
    return main_df

def create_csv():
    main_df = create_dataframe()
    main_df.to_csv("final-csv.csv", index=False)
    return main_df
