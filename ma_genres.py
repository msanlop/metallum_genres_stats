import requests
import json
import time
import re

class Genre:
    """
    Represents a genre with acociated stats attributes as defined by metal-archives' data.
    """
    entries_list = [] #entries are saved to eventually rerun update_stats on
    num_bands = 0
    genres_count = {}
    status_count = {}
    country_count = {}

    def __init__(self, name, endpoint):
        self.name = name
        self.endpoint = endpoint #genre name in ma's API
        self.update_data()

    def update_data(self, start=0, end=num_bands):
        """Gets data from ma and updates the dicts.
        can pass a starting index (big genres should take no more than 5 min anyway)
        """

        #first GET to find out number of bands
        if start==0:
            j = get_json(start, self.endpoint)
            self.num_bands = end = j['iTotalRecords']
            self.entries_list.extend(j['aaData'])
            self.update_stats(j['aaData'])
            start+=500
            
        for i in range(start, end, 500):
            print(f'{i}/{self.num_bands} bands have been processed')
            time.sleep(3) # I am a civilized internet user :)
            j = get_json(start, self.endpoint)['aaData']
            self.entries_list.extend(j)
            self.update_stats(j)

    def update_stats(self, entries):
        """
        Updates the instance's dictionary counts with the 'json' array given.
        """
        for entry in entries:
            entry_country, entry_genres, entry_status =  entry[1], entry[2], entry[3]
            
            self.country_count.update({entry_country: self.country_count.get(entry_country, 0) + 1})
            self.status_count.update({entry_status: self.status_count.get(entry_status, 0) + 1})
            
            #bands with multiple genres have all of them counted
            entry_genres = re.sub(r' *\(early\)| *\(later\)', '', entry_genres)
            split_genres = re.split(r'/|; ', entry_genres)
            for g in split_genres:
                self.genres_count.update({g: self.genres_count.get(g, 0) + 1})





BASEURL = "https://www.metal-archives.com/browse/ajax-genre/g/"
URLTAIL = "/json/1"

def get_json(start, genre_endpoint, length = 500):
        return fix_json(get_url(start, genre_endpoint))


def get_url(start, genre_endpoint, length = 500):
    """
    GET to ma's genre api. Length 500 is max.
    """

    payload = {'sEcho':0, # seting sEcho is supposed to avoid getting a unvalid JSON, but not working for me...
                'iDisplayStart':start,
                'iDisplayLength':length}
    r = requests.get(BASEURL + genre_endpoint + URLTAIL, params=payload)
    return r

def fix_json(response):
    """
    Fix the json of given response by filling the empty sEcho field.
    """
    
    json_str = response.content.decode('utf-8')
    i = json_str.find(': ,')
    fixed_json_str = json_str[:i+1] + '1' + json_str[i+1:]
    return json.loads(fixed_json_str)


