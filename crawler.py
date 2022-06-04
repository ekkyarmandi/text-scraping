from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import string
import time
import json
import re
import os

class WordsCrawler:

    def __init__(self, url: str, cookies_path: str, output_path: str, headless: bool = False):
        self.url=url
        self.cookies_path=cookies_path
        self.output_path=output_path
        self.headless=headless

        # define allowed domain
        self.allowed = re.search("(?<=/)[a-zA-Z. ]+(?=/)",url).group()
        self.ref = "https://"+self.allowed

    def run(self):
        '''Run the words crawler'''

        # open the chromedriver
        options = Options()
        options.add_argument("--level-log=3")
        if self.headless:
            options.add_argument("--headless")
        self.browser = Chrome(options=options)
        self.browser.get(self.ref)

        # adding cookies
        if self.cookies_path != None and len(self.cookies_path) != 0:
            self.add_cookies()
        else:
            self.browser.get(self.url)
            time.sleep(2)

        # scrape browser html
        links = self.collect_links()

        # scrape 10K words
        container = []
        container = self.process(container)
        while len(container) < 10000:
            for link in links:
                print("Next URL:",link)
                self.browser.get(link)
                container = self.process(container)
                if len(container) >= 10000:
                    break

        # check output folder
        if not os.path.exists("output"):
            os.mkdir("output")

        # decide the output filename
        if self.output_path != None:
            file_name = os.path.join("output",self.output_path+".txt")
        else:
            file_name = os.path.join("output",self.ref.split("/")[-1]+".txt")
        
        # writeout the 10K words 
        with open(file_name,"w",encoding="utf-8") as f:
            f.write(" ".join(container))

        # printout message
        print(f"done! {len(container):,d} has been collected")

    def add_cookies(self):
        '''Adding cookies to the driver'''

        raw_data = json.load(open(self.cookies_path))
        self.browser.delete_all_cookies()
        for cookie in raw_data['cookies']:
            self.browser.add_cookie(dict(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain']
            ))
        self.browser.get(self.url)
        time.sleep(2)

    def process(self, container: list) -> list:
        '''Put word into the words container'''

        def remove_whitespace(text: str) -> str:
            '''Clean the text from whitespace and punctuation'''

            text = "".join([s for s in text if s not in string.punctuation])
            text = re.sub("\s+"," ",text).strip()
            return text

        # iterate string from html text
        soup = BeautifulSoup(self.browser.page_source,"html.parser")
        for word in soup.strings:
            text = remove_whitespace(word)
            if text != "":
                text = text.split(" ")
                container.extend(text)
                
                # if exceed 10000, stop the iteration
                if len(container) >= 10000:
                    return container[:10000]
        
        # return words container variable
        print("Words:",len(container))
        return container

    def collect_links(self) -> list:
        '''Collect URLs from the visited website'''

        links = []
        soup = BeautifulSoup(self.browser.page_source,"html.parser")
        for a in soup.find_all("a"):
            if "href" in a.attrs:
                link = a['href']
                if "http" not in link: 
                    link = self.ref + link
                if self.allowed in link:
                    links.append(link)
        return list(dict.fromkeys(links))