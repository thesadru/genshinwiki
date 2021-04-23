from bs4 import BeautifulSoup

def extract_table(soup: BeautifulSoup, path: tuple[str]=('tr','td')) -> list:
    """Extracts data-parts and tables from them"""
    if not path:
        return soup
    return [extract_table(i,path[1:]) for i in soup.find_all(path[0])]

def extract_image(soup: BeautifulSoup) -> tuple[str,str]:
    raise NotImplementedError