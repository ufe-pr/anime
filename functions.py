import requests, re, json
import time
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options


API = 'https://animepahe.com/api'
KWIK_HEADER = {'referer': 'https://kwik.cx'}




HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0'}
s = requests.Session()

def query_api(params, recursion_count=0):

    param_string = '?'
    for i in params:
        param_string += '{}={}&'.format(i, params[i])
    
    page = s.get(API+param_string).text
    try:
        response = json.loads(page)
    except:
        options = Options()
        options.headless = True
        options.add_argument("--disable-extensions")
        browser = webdriver.Firefox(options=options)
        browser.get(API)
        browser.header_overrides = KWIK_HEADER
        browser.close()
        if recursion_count < 5:
            return query_api(params, recursion_count=recursion_count + 1)
        else:
            print('Error encountered while querying API.....')
            return
    total = response.get('total')
    data = response.get('data')
    return total, data


def search(search_term):
    # form the API query
    params = {'m': 'search', 'l': '10', 'q': search_term}
    # get the data
    return query_api(params)


def get_episodes(anime_id):
    # form the API query again
    params = {'m': 'release', 'id': str(anime_id), 'l': '-1', 'sort': 'episode_desc', 'page': '1'}
    # get the data again
    return query_api(params)


def get_embed_links(episode_link):
    page = s.get(episode_link).text
    embed_link = re.search(r'var url = "(\w+\:\/\/kwik\.cx\/e\/\w+)";', page).group(1)
    return embed_link
    

def get_token(kwik_link):
   # print('Getting token...')
    
    res = s.get(kwik_link,  headers={'Referer': kwik_link},).text
    token = re.search(r'name\|_token\|value\|(\w+)\|submit', res).group(1)
    return token


def get_down_link(embed_link):
    kwik_link = re.sub('kwik.cx/e/', 'kwik.cx/f/', embed_link)
    form_action = re.sub('kwik.cx/e/', 'kwik.cx/d/', embed_link)
    form_data = {'_token': get_token(kwik_link)}
    down_link_response = s.post(form_action, data=form_data, headers={'Origin': 'https://kwik.cx', 'Referer': kwik_link, 'Host': 'kwik.cx'}, allow_redirects=False)
    down_link = down_link_response.headers.get('location')
    print(down_link)
    return down_link
