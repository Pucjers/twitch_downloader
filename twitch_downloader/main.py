import fake_useragent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import requests
import json

import os

from error import ChannelNameInputError, HTMLParsingError

class Downloader:
    counter = 0

    def __init__(self, user_agent :str = None) -> None:
        
        if user_agent == None:
            self.user_agent = fake_useragent.FakeUserAgent().random
        else:
            self.user_agent = user_agent

    def download(self, channel_name: str = None, range: str = '7d', path = os.getcwd()) -> None:
        if channel_name == None:
            raise ChannelNameInputError('Channel name must not be empty')
        
        url = f'https://www.twitch.tv/{channel_name}/clips?filter=clips&range={range}'

        html_content = self.get_html(url=url)
        urls = self.get_urls_from_json(self.extract_json(html_content=html_content))
        
        for i in urls:
            self.download_clip(url=i, path=path)

    def get_html(self, url: str = None, clp:bool=False):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            if clp:
                time.sleep(1)
                video_element = driver.find_element(By.TAG_NAME, 'video')
                return video_element.get_attribute('src')
            html_content = driver.page_source
            
            driver.quit()
            return html_content
        except Exception as e:
            print("Unexpected error:", e)
            return None

    def extract_json(self, html_content:str):
        soup = BeautifulSoup(html_content, 'html.parser')
        json_data = None

        script_tags = soup.find_all('script')
        for script_tag in script_tags:
            if 'itemListElement' in script_tag.text:
                json_data = json.loads(script_tag.text)
                break
        
        if json_data == None:
            raise HTMLParsingError('Something wrong with html content, please try again')
        
        return json_data
    
    def get_urls_from_json(self, json_data):
        urls = []
        for item in json_data[1]['itemListElement']:
            if 'url' in item:
                urls.append(item['url'])
        return urls
    
    def download_clip(self, url: str, path: str):
        src = self.get_html(url=url,clp=True)
        try:
            response = requests.get(src, stream=True)
            if response.status_code == 200:
                with open(f'{path}/{self.counter}.mp4', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                Downloader.counter +=1
            else:
                print("Video upload error. Status code:", response.status_code)
        except Exception as e:
            print("Unexpected:", e)

d = Downloader()

d.download(channel_name='cs2_maincast')