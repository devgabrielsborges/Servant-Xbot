import pickle
import re
import os
from random import randint

import undetected_chromedriver as uc
from time import sleep
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located, presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

# First execution to log in and save cookies
driver = uc.Chrome()

# refreshing the page to avoid bot detection
driver.get("https://www.amazon.com.br/gp/bestsellers/?ref_=nav_cs_bestsellers")
driver.implicitly_wait(randint(1, 3))
driver.get("https://www.amazon.com.br/gp/bestsellers/?ref_=nav_cs_bestsellers")


wait = WebDriverWait(driver, 20)

wait.until(presence_of_element_located((By.ID, "nav-link-accountList")))
login_button = driver.find_element(By.ID, "nav-link-accountList")
login_button.click()

wait.until(presence_of_element_located((By.ID, "ap_email")))
email_input = driver.find_element(By.ID, "ap_email")
email_input.send_keys(f'{os.getenv("amazon_email")}\n')

wait.until(presence_of_element_located((By.ID, "ap_password")))
password_input = driver.find_element(By.ID, "ap_password")
password_input.send_keys(f'{os.getenv("amazon_password")}')

# Clicks the login button
driver.find_element(By.ID, "signInSubmit").click()

# Waits for the page to fully load and login to be completed
wait.until(presence_of_element_located((By.ID, "nav-link-accountList")))

# Saves the cookies to a file
with open("cookies.pkl", "wb") as file:
    pickle.dump(driver.get_cookies(), file)


# Loads the homepage of the same domain before adding cookies
driver.get("https://www.amazon.com.br/")


# Loads the cookies from the file
with open("cookies.pkl", 'rb') as cookiesfile:
    cookies = pickle.load(cookiesfile)
    for cookie in cookies:
        driver.add_cookie(cookie)

with open("best_sellers_topics.txt", 'r') as f:
    topics = f.readlines()

    for topic in topics:
        # opens the page with the desired topic
        driver.get(str(topic))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        driver.implicitly_wait(25)
        driver.execute_script("window.scrollTo(0, 800);")

        wait.until(presence_of_all_elements_located((By.CLASS_NAME, "_cDEzb_p13n-sc-css-line-clamp-3_g3dy1")))
        wait.until(presence_of_all_elements_located((By.CLASS_NAME, "_cDEzb_p13n-sc-price_3mJ9Z")))

        products = [product.text for product in
                    driver.find_elements(By.CLASS_NAME, "_cDEzb_p13n-sc-css-line-clamp-3_g3dy1")]
        prices = [
            float(
                re.search(r"R\$\s*([\d,.]+)", price.text).group(1).replace(".", "").replace(",", ".")
            ) for price in driver.find_elements(By.CLASS_NAME, "_cDEzb_p13n-sc-price_3mJ9Z")
        ]

        links = [link.get_attribute("href") for link in driver.find_elements(By.XPATH,
            "//a[@class='a-link-normal' and @role='link']/span/div[@class='_cDEzb_p13n-sc-css-line-clamp-3_g3dy1']/ancestor::a")]

        with open("brute_links.txt", "w") as file:
            for link in links:
                file.write(f"{link}\n")

        afiliate_links = []
        with open("brute_links.txt", "r") as file:
            for link in file.readlines():
                driver.get(link)

                wait.until(presence_of_element_located((By.ID, "amzn-ss-get-link-button")))
                driver.find_element(By.ID, "amzn-ss-get-link-button").click()

                wait.until(presence_of_element_located((By.ID, "amzn-ss-text-shortlink-textarea")))
                sleep(0.5)
                afiliate_link = driver.find_element(By.ID, "amzn-ss-text-shortlink-textarea").text

                afiliate_links.append(afiliate_link)

        with open("afiliate_links.txt", "a") as file:
            for link in afiliate_links:
                file.write(f"{link}\n")
