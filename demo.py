from bs4 import BeautifulSoup
import requests
import string
import re


def process(soup: BeautifulSoup, container: list) -> list:
    '''Put word into the words container'''

    def remove_whitespace(text: str) -> str:
        '''Clean the text from whitespace'''

        text = "".join([s for s in text if s not in string.punctuation])
        text = re.sub("\s+"," ",text).strip()
        return text

    # iterate string from html text
    for word in soup.strings:
        text = remove_whitespace(word)
        if text != "":
            text = text.split(" ")
            container.extend(text)
            
            # if exceed 10000, stop the iteration process
            if len(container) >= 10000:
                return container[:10000]
    
    # return words container variable
    return container

def collect_links(soup: BeautifulSoup, reffer: str) -> list:
    '''Collect website URLs'''

    links = []
    for a in soup.find_all("a"):
        if "href" in a.attrs:
            link = a['href']
            if "http" not in link: 
                link = reffer + link
            links.append(link)
    return list(dict.fromkeys(links))

def parser(url: str) -> BeautifulSoup:
    '''Make a GET requests and return it as BeautifulSoup object'''

    h = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}
    res = requests.get(url, headers=h)
    return BeautifulSoup(res.text,"html.parser")


url = "https://en.wikipedia.org/wiki/Philosophy"
allowed = re.search("(?<=/)[a-zA-Z. ]+(?=/)",url).group()
ref = "https://"+allowed
soup = parser(url)
links = collect_links(soup,ref)

container = []
container = process(soup,container)
while len(container) < 10000:
    for link in links:
        new_soup = parser(link)
        container = process(new_soup,container)
        if len(container >= 10000):
            break

output_file = allowed + ".txt"
with open(output_file,"w") as f:
    f.write(" ".join(container))