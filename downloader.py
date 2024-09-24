import os
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

# Set up Selenium WebDriver (Headless Mode)
def init_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_video_url_selenium(driver, url):
    """
    Use Selenium to get the video URL from pages with dynamically loaded content.
    """
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    video_tags = soup.find_all('video')
    if video_tags:
        for video_tag in video_tags:
            if video_tag.has_attr('src'):
                return video_tag['src']
            elif video_tag.find('source'):
                return video_tag.find('source')['src']
    
    # Search for common video file extensions in the page
    video_formats = ['.mp4', '.webm', '.ogg', '.mkv', '.m3u8']
    for format in video_formats:
        match = re.search(r'http[s]?://[^\s]+{}'.format(format), driver.page_source)
        if match:
            return match.group(0)
    
    return None

def download_video(url, output_path):
    """
    Download a video from a direct URL with a progress bar.
    """
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    with open(output_path, 'wb') as file, tqdm(
        desc=output_path,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def generate_filename_from_title(driver, url):
    """
    Generate a filename based on the webpage title.
    """
    driver.get(url)
    title = driver.title.strip().replace(' ', '_').replace('/', '_')
    return f"{title}.mp4"

def main(website_url, output_dir='./downloads'):
    # Initialize the browser
    driver = init_browser()

    # Generate filename based on the page title
    filename = generate_filename_from_title(driver, website_url)
    output_path = os.path.join(output_dir, filename)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get video URL using Selenium
    video_url = get_video_url_selenium(driver, website_url)
    
    # Close the browser
    driver.quit()
    
    if video_url:
        print(f"Found video URL: {video_url}")
        download_video(video_url, output_path)
    else:
        print("No video found on the website.")

# Example Usage
if __name__ == "__main__":
    website_url = "https://www.example.com"  # Replace with the URL of the webpage containing the video
    main(website_url)
