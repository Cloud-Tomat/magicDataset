from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import glob
import os
import io
import requests
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures
import time
import threading
import urllib3
from tqdm import tqdm
import logger





#disable certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = 'https://yandex.com/images/'
SEARCH_BUTTON_CLASS="websearch-button.mini-suggest__button"
SEARCH_INPUT_CLASS="input__control.mini-suggest__input"
SHOW_MORE_BUTTON_CLASS=".Button2.Button2_width_max.Button2_size_l.Button2_view_action.FetchListButton-Button"
IMGS_CLASS="a.Link.ContentImage-Cover"


class imageCrawler():
    def __init__(self,debug=False):
        # Set up Chrome options
        chrome_options = Options()
        if not debug:
            chrome_options.add_argument('--log-level=3') 
            chrome_options.add_argument("--headless")  # Ensure GUI is off
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        # Set up the Chrome WebDriver with headless option
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def download_image(self, image_url, save_folder, img_name,min_megapixels):

        # Define a custom User-Agent string
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        }

        try:
            # Bypass SSL certificate verification
            response = requests.get(image_url, verify=False, headers=headers, timeout=2.0) 
            if response.status_code == 200:
                # Read the image data from the response's content
                img_data = io.BytesIO(response.content)
                
                try:
                    img = Image.open(img_data)
                    width, height = img.size
                    size_megapixels = (width * height) / 1e6

                    if min_megapixels is None or size_megapixels >= min_megapixels:
                        # Convert the image to RGB and save as PNG
                        img_rgb = img.convert('RGB')
                        base_img_name = os.path.splitext(img_name)[0]  # Strip original extension
                        path = os.path.join(save_folder, f"{base_img_name}_{int(time.time())}.jpg")
                        #img_rgb.save(path, 'PNG')
                        img_rgb.save(path, 'JPEG')
                        print(f"Saved image {img_name} with size {size_megapixels:.2f} MP")
                        return True
                    else:
                        return False           
                except:
                    print("corrupted file")
                    return False
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {image_url}: {e}")


    def extract_and_download_images(self, driver, save_folder, processed_images=None, maxImages=None, minSize=0):
        if processed_images is None:
            processed_images = set()

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        
        image_links = driver.find_elements(By.CSS_SELECTOR, IMGS_CLASS)  # Assuming IMGS_CLASS is defined elsewhere

        lock = threading.Lock()
        numImages = 0

        def process_download_task(link):
            nonlocal numImages
            with lock:
                if maxImages is not None and numImages >= maxImages:
                    return  # Skip processing this task            
            href = link.get_attribute('href')
            parsed_url = urlparse(href)
            query_params = parse_qs(parsed_url.query)
            img_url = query_params.get('img_url', [None])[0]

            if img_url and img_url not in processed_images:
                if self.download_image(img_url, save_folder, f"image_{len(processed_images) + 1}.jpg", minSize):
                    with lock:
                        numImages += 1  # Safely increment numImages
                processed_images.add(img_url)
            return img_url

        # Use ThreadPoolExecutor to download images concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            i=0
            for link in image_links:
                with lock:
                    if maxImages is not None and numImages >= maxImages:
                        break  # Cease to submit new tasks if maxImages reached
                future = executor.submit(process_download_task, link)
                futures.append(future)

            # Wait for all futures to complete and show progress
            for _ in tqdm(as_completed(futures), total=len(futures), desc="Downloading images candidate"):
                pass  # The progress update is handled by tqdm; no need to do anything in the loop

        print(f"Total images downloaded: {numImages}")
        return processed_images, numImages



    # Scroll to the bottom of the page
    def scroll_to_bottom(self,driver, wait_time=0.5):
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        retry=0

        while True:
            # Scroll down to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for page to load
            time.sleep(wait_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                retry+=1
                if retry>=3:
                    break
                else:
                    time.sleep(0.5)

            last_height = new_height


    # Function to click the "Show more" button
    def click_show_more_button(self,driver):
        try:
            # Wait for the "Show more" button to be clickable, selecting by button text
            #show_more_button = WebDriverWait(driver, 10).until(
            #    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Show more')]"))
            #)

            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SHOW_MORE_BUTTON_CLASS))
            )

            # Give focus to the "Show more" button
            show_more_button.send_keys(Keys.NULL)

            # Simulate pressing the Enter key
            show_more_button.send_keys(Keys.ENTER)

            print("Clicked the 'Show more' button.")
            return True
        except Exception as e:
            print(f"Error clicking the 'Show more' button: {e}")
            return False

    def download(self,search_text,saveFolder,minSize=0,maxNumberImages=None):

        if not os.path.exists(saveFolder):
            os.makedirs(saveFolder)

        file_path=os.path.join(saveFolder,"prompt.txt")

        with open(file_path, 'w') as file:
            file.write(search_text)

 

        # Delete cookies, seems to avoid CAPTCHA after several downloads
        self.driver.delete_all_cookies()
        wait = WebDriverWait(self.driver, 1)  # Wait for up to 10 seconds

        self.driver.get(URL)
        wait = WebDriverWait(self.driver, 1)  # Wait for up to 10 seconds

        # Locate the search input field
        search_input = self.driver.find_element(By.CLASS_NAME, SEARCH_INPUT_CLASS)

        # Clear the search field if needed
        search_input.clear()

        # Enter the search text

        search_input.send_keys(search_text)

        # Wait a moment for suggestions to load 
        time.sleep(1)

        #  locate and click the search button
        search_button = self.driver.find_element(By.CLASS_NAME, SEARCH_BUTTON_CLASS)
        search_button.click()

        time.sleep(5)

        #Some init
        success=True
        page=1
        totalImages=0
        processed_images=None
        while success and totalImages < maxNumberImages:
            logger.console(f"Processing page {page}")
            self.scroll_to_bottom(self.driver)

            processed_images, numImages = self.extract_and_download_images(self.driver, saveFolder, processed_images=processed_images, maxImages=maxNumberImages-totalImages,minSize=minSize)
            totalImages += numImages
            logger.console(f"Downloaded {numImages} images from page {page}, {totalImages} images in total")
            
            time.sleep(2)
            success = self.click_show_more_button(self.driver)
            page+=1




        return totalImages








if __name__ == "__main__":
    yandex=imageCrawler(debug=True)
    for i in range (50):
        yandex.download("a dog","testdir",0,10)

