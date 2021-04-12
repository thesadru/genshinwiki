from requests_cache import CachedSession
from bs4 import BeautifulSoup
from pprint import pprint

base_url = "https://bbs.mihoyo.com"
session = CachedSession()

def get_url(url: str):
    return url.split('?')[0]

def parse_info(data) -> dict:
    name = data.h1.text
    info,introduction = data.table.find_all('tbody')
    info = [i.find_all('td') for i in list(info)]
    img = info[0].pop(0).img
    img = img.get('src').split('?')[0]
    b,e,w,c = [i[1].text for i in info]
    
    return {
        'name':name,
        'belonging':b,
        'element':e,
        'weapon':w,
        'constellation':c,
        'introduction':introduction.text,
        'img': img
    }

def parse_description(data) -> dict:
    _,birthday,_,title = data.table.tbody.tr.find_all('td')
    return {
        'birthday':birthday.text,
        'title':title.text
    }

def parse_attributes(data) -> dict:
    attrs = [i.find_all('td')[1].div.span.text for i in data.table.tbody.find_all('tr')]
    return {
        'meelee': attrs[0]=="\U00008FD1\U00006218",
        'hp': int(attrs[1]),
        'atk': int(attrs[2].split('（')[0]),
        'def': int(attrs[3]),
        'em': int(attrs[4]),
        'crit_rate': float(attrs[5][:-1]),
        'crit_dmg': float(attrs[6][:-1]),
        'healing_bonus': float(attrs[7][:-1]),
        'er': float(attrs[8][:-1])
    }

def parse_ascension(data) -> list:
    ascensions = []
    stages = data.find('ul', {"class": "obc-tmpl__switch-list"})
    stages = stages.find_all('li', {"data-target": "breach.attr"})
    for stage in stages:
        materials,foo = stage.table.find_all('tbody')
        if int(stage['data-index']) < 6:
            materials = [i.div.a or i.div for i in materials.find_all('td')[1].ul.find_all('li')]
            materials = [(i.span.text.split('*'),i.img['src']) for i in materials]
        else:
            materials = []
        foo = [td for tr in foo.find_all('tr') for td in tr.find_all('td')]
        foo = [foo[i:i+2] for i in range(0,len(foo),2)]
        
        ascensions.append({
            'materials':[
                {'item':item,'amount':amount,'img':img.split('?')[0]} 
                for (item,amount),img in materials],
            'foo':[
                {'field':k.text, 'value':v.text} 
                for k,v in foo],
        })
    return ascensions

def parse_constellation(data) -> list:
    consts = [i.find_all('td') for i in data.table.tbody.find_all('tr')]
    consts = [{'name':name.span.text, 'effect':effect.text, 'img':name.img['src'].split('?')[0]} for name,_,effect in consts]
    return consts

def get_character(url: str) -> dict:
    """Fetches a character and parses all data."""
    data = {}
    
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    character = soup.find('div', {'data-type': 'character'})
    
    data['info'] = parse_info(
        character.find('div', {'data-part': 'main'})
    )
    print(data['info']['name'])
    data['info'].update(parse_description(
        character.find('div', {'data-part': 'describe'})
    ))
    data['attrs'] = parse_attributes(
        character.find('div', {'data-part': 'basicAttr'})
    )
    data['ascension'] = parse_ascension(
        character.find('div', {'data-part': 'breach'})
    )
    data['constellation'] = parse_constellation(
        character.find('div', {'data-part': 'life'})
    )
    return data
    

def get_characters() -> list:
    r = session.get("https://bbs.mihoyo.com/ys/obc/channel/map/25")
    characters = []
    soup = BeautifulSoup(r.text, 'html.parser')
    for i in soup.find_all('li', {'class': 'position-list__item'}):
        url = base_url+i.find('a')['href']
        characters.append(get_character(url))
        # break
    return characters
