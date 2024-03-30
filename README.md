# Twitch Downloader

This script is designed to download video content from Twitch channels. It utilizes Selenium for web scraping and requests for downloading video content.

## Requirements:
- Selenium: Python library for browser automation
- requests: HTTP library for making requests
- toml: Library for parsing TOML configuration files

## Usage:
1. Ensure you have the necessary dependencies installed.
2. Create or download a TOML configuration file named 'config.toml' in the same directory as this script.
3. Configure the 'config.toml' file with appropriate values for 'main' and 'clips' paths.
4. Create an instance of the Downloader class and call the 'download' method with appropriate parameters.

## Methods:
    download: Downloads video content from the specified Twitch channel.
    get_clips_src: Retrieves the source URLs for video clips.
    get_urls: Retrieves the URLs of video clips for the specified channel.
    download_clip: Downloads a video clip from the provided source URL.

## Exceptions:
    ChannelNameInputError: Raised when the channel name is not provided.
    HTMLParsingError: Raised when there is an error parsing HTML content.
