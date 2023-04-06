# WHO EML Scraper

import bs4
import urllib.request
import pandas as pd
import operator

# current path for your computer, which each person needs to change
PATH = "/Users/james-y-hu/Desktop/Work/RP WHO EML"

# Step 0: Get all HTMLs (Laura only has differences with WHO list; additionally need consistencies with WHO list)

# Step 1: Get list of all meds by looking at HTML (maybe start out as a set from the get go, or maybe convert to set at the very end)

# Step 2: Verify that no WHO EML medicines are missing from this list (i.e., there are no WHO EML medicines that are not also on at least one national EML)

# Step 3: Figure out pandas stuff

medicines = []


# Step 2: 


# Notes:
# Wasn't able to scrape/crawl WHO website, so had to download HTML files individually.
# All the functions work but probably need to completely redesign since I'm doing a different thing.
# Then need a function to write to a CSV
# Laura's rethinking her strategy: since sets aren't ordered it'll be a little bit odd, so should make into list
# Suggested data structure: one big dict with 137 items, each item is key (country): value (big list of binaries which correspond to LIST). LIST is list of medicines which is converted to list from set.


# Laura only downloaded differences with WHO.


# Number of countries had to be manually determined by scrolling down to the last country on the list (currently Zimbabwe) 
# and finding its index from the end of the url (currently 137). Could not figure out how to automate this process, as the original url
# (https://global.essentialmeds.org/dashboard/countries/) does not have an html file that contains countries' indices past Bhutan and
# clicking on "Z" did not produce a unique url whose html file would containing all country indexes where the country name started with "Z". 
# Worth double-checking to see if NUM_COUNTRIES is still 137 each time this is refreshed.
NUM_COUNTRIES = 137

# try this with True and if you get an empty dataframe, it's because the HMTL file thinks your browser is out of date. 
# if this happens, you have to manually download all 137 country html files (click on each country, then on "Differences with the list") 
# and name them "EML_i.html", where i = 1, ..., 137.
can_download = False # BECAUSE WHO SITE WON'T ALLOW

# to_print True if you want the program to print the dataframe instead of just creating a csv file
to_print = True

def scrape_one_country(country_idx, can_download):
    if can_download:
        url = 'https://global.essentialmeds.org/dashboard/countries/' + str(country_idx)
        req = urllib.request.urlopen(url).read()
        soup = bs4.BeautifulSoup(req, 'html.parser')
    else:
        html = open('{}\\EMLs_{}.html'.format(PATH, country_idx), encoding='utf8').read()
        soup = bs4.BeautifulSoup(html, 'html.parser')

    country_med_tags = soup.find_all("span", class_ = "css-t9ct1g")
    return country_med_tags


# This one counts up frequencies at the moment
# Want: collective list
# Want: cycle through EML HTMLs, then create a set of all of the medicines that are in the database [SET X] → never mind, actually should make list, ordered tuples
# Want: and then go through each of the countries (come up with a nested dictionary, where the first key is Afghanistan and its value would be a dict that contains SET X as keys and 0 or 1 as value)
def update_medicines_dictionary(med_dict, country_med_tags):
    for tag in country_med_tags:
        medicine = str(tag.text)
        if medicine not in med_dict:
            med_dict[medicine] = 1
        else:
            med_dict[medicine] += 1
    return med_dict

def get_all_frequencies():
    med_dict = {}
    for i in range(1, NUM_COUNTRIES+1):
        country_med_tags = scrape_one_country(i, can_download)
        med_dict = update_medicines_dictionary(med_dict, country_med_tags)

    med_dict = dict(sorted(med_dict.items(), key=operator.itemgetter(1), reverse=True))
    return med_dict

def make_ranked_df(med_dict):
    med_names = med_dict.keys()
    med_freqs = med_dict.values()

    idx = [i for i in range(1, len(med_names)+1)]

    med_df = pd.DataFrame(list(zip(med_names, med_freqs)), columns = ["Medicine", "Freq. on Country EML"], index=idx)

    return(med_df)

def main():
    med_dict = get_all_frequencies()
    eml_df = make_ranked_df(med_dict)
    top_20_df = eml_df[:20]
    eml_csv = eml_df.to_csv('EMLs_not_on_WHO_List_Descending_Frequency.csv')
    top_20_csv = top_20_df.to_csv('Top 20 Country EMLs Not on WHO List.csv')
    return eml_df, top_20_df

eml_df, top_20_df = main()
if to_print:
    print("Top 20 Country EMLs Not on WHO List:")
    print(top_20_df)






