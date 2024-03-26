import urllib.request
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
import time



def scroll_down()-> None:
    global driver
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(10)
            new_height = driver.execute_script("return document.body.scrollHeight")
            try:
                driver.find_element_by_class_name("mye4qd").click()
            except:
               if new_height == last_height:
                   break
        last_height = new_height

if __name__ == "__main__":

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.google.com/search?q=%EB%A0%88%EB%93%9C%EB%B2%A8%EB%B2%B3+%EC%95%84%EC%9D%B4%EB%A6%B0&tbm=isch&ved=2ahUKEwiX2-K-0LiCAxWXNN4KHQ1nCZ8Q2-cCegQIABAA&oq=%EB%A0%88%EB%93%9C%EB%B2%A8%EB%B2%B3+%EC%95%84%EC%9D%B4%EB%A6%B0&gs_lcp=CgNpbWcQAzIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQ6CAgAEIAEELEDOgcIABAYEIAEUI4DWO4jYIAkaA9wAHgBgAGrAYgB4BGSAQQwLjE5mAEAoAEBqgELZ3dzLXdpei1pbWfAAQE&sclient=img&ei=GbZNZdfqBpfp-AaNzqX4CQ&bih=1292&biw=1243"
    driver.get(url)
    time.sleep(1)
    scroll_down()

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img', attrs={'class':'rg_i Q4LuWd'})
        
    counter = 1
    for i in images:
        try:
            imgUrl = i["src"]
        except:
            imgUrl = i["data-src"]

        with urllib.request.urlopen(imgUrl) as f:
            with open(f"./img/{str(counter).zfill(5)}.jpg", 'wb') as h:
                img = f.read()
                h.write(img)
        counter += 1
        
    # TODO: target name parser argument
    # TODO: multiprocessing
    