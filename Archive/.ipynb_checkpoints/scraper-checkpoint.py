# WHO EML Scraper

import bs4
import urllib.request
import pandas as pd
import operator

# current path for your computer, which each person needs to change
PATH = "C:\\Users\\Laura\\Documents\\RP\\EMLs_WHO"

# Number of countries had to be manually determined by scrolling down to the last country on the list (currently Zimbabwe) 
# and finding its index from the end of the url (currently 137). Could not figure out how to automate this process, as the original url
# (https://global.essentialmeds.org/dashboard/countries/) does not have an html file that contains countries' indices past Bhutan and
# clicking on "Z" did not produce a unique url whose html file would containing all country indexes where the country name started with "Z". 
# Worth double-checking to see if NUM_COUNTRIES is still 137 each time this is refreshed.
NUM_COUNTRIES = 137

# try this with True and if you get an empty dataframe, it's because the HMTL file thinks your browser is out of date. 
# if this happens, you have to manually download all 137 country html files (click on each country, then on "Differences with the list") 
# and name them "EML_i.html", where i = 1, ..., 137.
can_download = False

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






