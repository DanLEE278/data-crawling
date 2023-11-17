import io
import requests
import pandas as pd
import re

from tqdm import tqdm
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

username = "" # user name
password = "" # user password 

classes = "gallery-item"
location = "img"
source = "src"
img_name = "alt"

def crawl_dataset(page):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://eyefakes.com/gallery.php?page={page}&codename=main")
    driver.implicitly_wait(1)
    driver.find_element(By.XPATH, '//*[@id="mobile-header"]/span[2]/ul/li[1]/a').click()
    driver.implicitly_wait(1)
    driver.find_element(By.ID, 'quick_login_username').send_keys(username)
    driver.implicitly_wait(1)
    driver.find_element(By.ID, 'quick_login_password').send_keys(password)
    driver.implicitly_wait(1)
    driver.find_element(By.XPATH, '//*[@id="quick_login"]/form/table/tbody/tr[5]/td/div/input').click()

    results = []
    results2 = []
    content = driver.page_source
    soup = BeautifulSoup(content,"html.parser")

    # Picking a name that represents the function will be useful as you expand your code.
    for a in soup.findAll(attrs={'class': classes}):
        name = a.find(location)
        if name not in results:
            results.append(name.get(source))
            results2.append(name.get(img_name))

    # df = pd.DataFrame({"links": results})
    # df.to_csv("links.csv", index=False, encoding="utf-8")
    return results, results2


if __name__ == "__main__":
    error_log = open("error_main.txt", "w")
    # file_list = open("files.txt", "w")
    # counter = 2740
    # counter = 11878
    counter = 20000
    # for idx in tqdm(range(229,2222,1)):
    # for idx in tqdm(range(972,2222,1)):
    for idx in tqdm(range(1649,2222,1)):
        results, results2 = crawl_dataset(idx)
        
        # Import the requests library to send HTTP requests
        for partial_url, name in zip(results, results2):
            # Store the content from the URL to a variable
            url = "https://eyefakes.com/" + partial_url
            image_content = requests.get(url).content
            new_str = re.sub(r"[^a-zA-Z]", "", name)

            # The io library manages file-related in/out operations.
            # Create a byte object out of image_content and store it in the variable image_file
            image_file = io.BytesIO(image_content)
            
            # Use Pillow to convert the Python object to an RGB image
            image = Image.open(image_file).convert("RGB")
            fpath = f"./samples_main/{str(counter).zfill(5)}_{new_str}.png"
            print(fpath)
            
            try:
                image.save(fpath, "PNG", quality=100)
            except:
                error_log.write(f"page:{idx}\tfname:{name}\tsrc:{partial_url}\n")
            counter += 1
    error_log.close()
