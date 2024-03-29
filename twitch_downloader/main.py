
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import logging
import re
import requests
import json

import os

from error import ChannelNameInputError, HTMLParsingError

class Downloader:
    counter = 0

    def __init__(self, log_level=logging.FATAL) -> None:
        logging.basicConfig(level=log_level)
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('--log-level=3')

    def download(self, channel_name: str = None, range: str = '7d', path = os.getcwd()) -> None:
        if channel_name == None:
            raise ChannelNameInputError('Channel name must not be empty')
        
        url = f'https://www.twitch.tv/{channel_name}/clips?filter=clips&range={range}'

        html_content = self.get_html(url=url)
        urls = self.get_urls_from_json(self.extract_json(html_content=html_content))
        src = self.get_clips_src(urls)

        for source in src:
            self.download_clip(source, path=path)

    def get_clips_src(self, urls):
        driver = webdriver.Chrome(options=self.chrome_options)

        src = []
        for url in urls:
            try:
                driver.get(url)
                time.sleep(1)
                video_element = driver.find_element(By.TAG_NAME, 'video')
                src.append(video_element.get_attribute('src'))
            except Exception as e:
                logging.error(f'Unexpected error on {url}: {e}')
        
        return src

    def get_html(self, url: str = None):
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            time.sleep(1)
            html_content = driver.page_source
            
            driver.quit()
            return html_content
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
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
    
    def download_clip(self, src: str, path: str):
        try:
            response = requests.get(src, stream=True)
            if response.status_code == 200:
                with open(f'{path}/{self.counter}.mp4', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                Downloader.counter +=1
            else:
                logging.error("Video download error. Status code: %d", response.status_code)
        except Exception as e:
            logging.error("Unexpected: %s", e)

downloader = Downloader(log_level=logging.ERROR) 

downloader.download(channel_name='cs2_maincast')