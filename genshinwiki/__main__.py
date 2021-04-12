import json

from . import *

data = {
    'characters': get_characters()
}
with open('data.json','w',encoding='utf-8') as file:
    json.dump(data,file,ensure_ascii=False)
