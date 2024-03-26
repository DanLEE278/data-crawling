# PYTHON BASE
import argparse
import io
import os
import requests

# EXTERNAL
from tqdm import tqdm
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from multiprocessing import Pool
from itertools import repeat


def get_parser()-> tuple[str,str,int]:
    parser = argparse.ArgumentParser(
                    prog='CivitAI Website Data crawler',
                    description='Provides Auto Crawling images/videos'
                    )
    parser.add_argument('-dt', '--datatype', type=str, required=True) # datatype
    parser.add_argument('-sp', '--savepath', type=str, default="result") # file save path
    parser.add_argument('-w', '--workers', type=int, default=1) # multiprocessing workers
    args = parser.parse_args()
    return args.datatype, args.savepath, args.workers

# scroll method to
def crawl_dataset(url:str)-> None:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(20)
    content = driver.page_source
    soup = BeautifulSoup(content,"html.parser")
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/main/div[1]/div[1]/div/div[2]/button/div/span[1]').click()
    
    elem = driver.find_element(By.TAG_NAME, "html")
    elem.send_keys(Keys.END)
    max_scrolls = 5000
    scroll_count = 0

    while scroll_count < max_scrolls:
        elem = driver.find_element(By.TAG_NAME, "html")
        elem.send_keys(Keys.END)
        driver.implicitly_wait(5)
        scroll_count += 1
        print(scroll_count)

        if max_scrolls%100 == 0:
            with open("civitai.html", "w") as file:
                file.write(str(soup))
            file.close()

    content = driver.page_source
    soup = BeautifulSoup(content,"html.parser")
    
    for item in tqdm(soup.find_all("div", {"class": "mantine-16xlp3a"})[0].find_all("a")):
        try:
            url = "https://civitai.com" + item.attrs['href'] # 본 이미지 url
            fpath = os.path.join("image", item.attrs['href'].split("/")[-1] + ".png")
            if os.path.isfile(fpath):
                continue
            html_content = requests.get(url).text
            soup2 = BeautifulSoup(html_content, "html.parser")
            url = soup2.find_all("img", {"class": "mantine-it6rft"})[0].get("src") # 다운로드 이미지 url
            image_content = requests.get(url).content
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert("RGB")
            image.save(fpath, "PNG", quality=100)
        except:
            pass

def crawl_image(url:str,savedir:str)-> str:
    
    fpath = os.path.join(savedir, url.split("/")[-1] + ".png")
    if os.path.isfile(fpath): # skip exisiting image
        pass
    else:
        html_content = requests.get(url).text
        soup2 = BeautifulSoup(html_content, "html.parser")
        if len(soup2.find_all("img", {"class": "mantine-it6rft"})) != 0:
            url = soup2.find_all("img", {"class": "mantine-it6rft"})[0].get("src") # 다운로드 이미지 url
            image_content = requests.get(url).content
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert("RGB")
            image.save(fpath, "PNG", quality=100)
            return print(f"{fpath} success")

def crawl_video(url:str,savedir:str)-> str:
    
    fpath = os.path.join(savedir, url.split("/")[-1] + ".mp4")
    if os.path.isfile(fpath): # skip exisiting video
        pass
    else:
        html_content = requests.get(url).text
        soup2 = BeautifulSoup(html_content, "html.parser")
        if len(soup2.find_all("source")) != 0:
            url = soup2.find_all("source")[1].get("src")
            content = requests.get(url, stream = True)
            with open(fpath, 'wb') as f:
                for chunk in content.iter_content(chunk_size = 1024*1024):
                    if chunk:
                        f.write(chunk)
            return print(f"{fpath} success")

if __name__ == "__main__":
    datatype, savepath, workers = get_parser()
    os.makedirs(savepath,exist_ok=True)
    inputs = [f"https://civitai.com/images/{str(x)}" for x in range(8000000, 9000000, 1)] # input lists
    
    with Pool(processes=workers) as pool:
        if datatype == "video":
            results = pool.starmap(crawl_video, zip(inputs, repeat(savepath)))
        elif datatype == "image":
            results = pool.starmap(crawl_image, zip(inputs, repeat(savepath)))

