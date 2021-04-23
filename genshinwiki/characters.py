from requests_cache import CachedSession
from bs4 import BeautifulSoup
from pprint import pprint

from .utils import *

session = CachedSession()


def get_character(url: str):
    r = session.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    parts = soup.find('div', {'class':"obc-tmpl obc-tmpl-character"}
        ).find_all('div',{'data-part':True})
    
    data = {}
    
    data['paintings'] = [
        {'name':n.text.strip(),'painting':p.img['src'].split('?')[0]} 
        for n,p in zip(*extract_table(parts[0],('ul','li')))
    ]
    
    info,introduction = parts[1].find_all('tbody')
    info = extract_table(info,('tr','td'))
    img = info[0].pop(0).img
    b,e,w,c = [i[1].text for i in info]
    
    _,birthday,_,title = parts[2].tr.find_all('td')
    
    data['info'] = {
        'name':parts[1].h1.text,
        'belonging':b,
        'element':e,
        'weapon':w,
        'constellation':c,
        'introduction':introduction.text,
        'birthday':birthday.text,
        'title':title.text,
        'img': img.get('src').split('?')[0]
    }
    
    data['voice_actors'] = dict(zip(
        ['cn','jp','en','ko'],
        [i.text.split('：')[1] for i in parts[3].find_all('p')[:4]]
    ))
    
    attrs = [i[1].text.strip() for i in extract_table(parts[4])]
    data['attrs'] = {
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
    
    ascensions = []
    stages = parts[5].find('ul', {"class": "obc-tmpl__switch-list"})
    stages = stages.find_all('li', {"data-target": "breach.attr"})
    for stage in stages:
        materials,asc_foo = extract_table(stage,('tbody','td'))
        asc_foo = [asc_foo[i:i+2] for i in range(0,len(asc_foo),2)]
        if stage['data-index'] == '6':
            materials = [] # last ascension doesn't have materials
        else:
            materials = [(*i.text.split('*'),i.img['src']) for i in materials[1].find_all('li')]
        ascensions.append({
            'materials': [{'name':n,'amount':a,'icon':i.split('?')[0]}
                for n,a,i in materials],
            'asc_foo':[{'name':i[0].text,'amount':i[1].text.strip()}
                for i in asc_foo]
        })
    data['ascensions'] = ascensions
    
    data['constellations'] = [
        {'name':n.text,'effect':e.text.strip(),'icon':n.img['src'].split('?')[0]}
        for n,_,e in extract_table(parts[6].tbody)]
    
    data['talents'] = None
    
    recom = soup.find('div', {'class':"obc-tmpl obc-tmpl-illustration"})
    recom = extract_table(recom.tbody)
    recom = [[i.text,i.img['src'].split('?')[0],[p.text.strip() for p in d.find_all('p')][1:]] 
             for i,d in recom]
    # here we use the fact weapons don't have effects like artifacts
    data['recommendations'] = {
        'weapons':[{'name':i[0],'icon':i[1]}
            for i in recom if not i[2]],
        'artifacts':[{'name':i[0],'effects':i[2],'icon':i[1]}
            for i in recom if i[2]]
    }
    
    return data

def get_characters() -> list:
    r = session.get("https://bbs.mihoyo.com/ys/obc/channel/map/25")
    characters = []
    soup = BeautifulSoup(r.text, 'html.parser')
    for i in soup.find_all('li', {'class': 'position-list__item'}):
        url = "https://bbs.mihoyo.com"+i.find('a')['href']
        try:
            characters.append(get_character(url))
        except Exception as e:
            print(url,e)
    return characters
    

if __name__ == '__main__':
    from pprint import pprint
    url = "https://bbs.mihoyo.com/ys/obc/content/1057/detail"
    pprint(get_character(url),sort_dicts=False)
