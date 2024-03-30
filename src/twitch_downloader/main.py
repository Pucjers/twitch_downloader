
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import logging
import requests
import os
from error import ChannelNameInputError, HTMLParsingError
from twitch_downloader import config

class Downloader:
    counter = 0

    def __init__(self, log_level=logging.FATAL) -> None:
        """
        Initializes the Downloader class.

        Args:
            log_level (int, optional): Logging level. Defaults to logging.FATAL.
        """
        logging.basicConfig(level=log_level)
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('--log-level=3')

    def download(self, channel_name: str = None, content_type:str = 'clips', range: str = '7d', path = os.getcwd()) -> None:
        """
        Downloads video content from the specified Twitch channel.

        Args:
            channel_name (str): The name of the Twitch channel.
            content_type (str, optional): Type of content to download (e.g., 'clips'). Defaults to 'clips'.
            range (str, optional): Time range for content (e.g., '7d' for last 7 days). Defaults to '7d'.
            path (str, optional): Path to save downloaded videos. Defaults to current directory.

        Raises:
            ChannelNameInputError: Raised when the channel name is not provided.
        """
        if channel_name == None:
            raise ChannelNameInputError('Channel name must not be empty')
        
        url = f'{config['path']['main']}{channel_name}/{config['path'][content_type]}range={range}'

        urls = self.get_urls(url=url,content_type=content_type)
        src = self.get_clips_src(urls)

        for source in src:
            self.download_clip(source, path=path)

    def get_clips_src(self, urls):
        """
        Retrieves the source URLs for video clips.

        Args:
            urls (list): List of URLs for video clips.

        Returns:
            list: List of source URLs for video clips.
        """
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

    def get_urls(self, url: str = None, content_type:str = 'clips'):
        """
        Retrieves the URLs of video clips for the specified channel.

        Args:
            url (str): URL of the Twitch channel.
            content_type (str): Type of content to retrieve URLs for.

        Returns:
            list: List of URLs for video clips.
        """
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get(url)
        time.sleep(1)
        element = driver.find_element(By.CLASS_NAME, "tw-tower")
        divs = element.find_elements(By.CLASS_NAME, "tw-link")

        hrefs = []
        for div in divs:
            href = div.get_attribute('href')
            if content_type[:-1] in href:
                hrefs.append(href)
        return list(set(hrefs))
    
    def download_clip(self, src: str, path: str):
        """
        Downloads a video clip from the provided source URL.

        Args:
            src (str): Source URL of the video clip.
            path (str): Path to save the downloaded video clip.
        """
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