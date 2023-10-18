import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# Set the URL of the Amazon product listing
url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

# Initialize a headless Selenium WebDriver (you'll need to have ChromeDriver installed)
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# Create a list to store product data
product_data = []

# Function to scrape product details
def scrape_product_details(page_url):
    driver.get(page_url)
    time.sleep(3)  # Wait for the page to load (you can adjust this time)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    for product in products:
        product_url = f"https://www.amazon.in{product.find('a', {'class': 'a-link-normal s-no-outline'})['href']}"
        product_name = product.find("span", {"class": "a-text-normal"}).text
        product_price = product.find("span", {"class": "a-price-whole"}).text
        rating = product.find("span", {"class": "a-icon-alt"})
        num_reviews = product.find("span", {"class": "a-size-base"})

        if rating:
            rating = rating.text
        else:
            rating = "N/A"

        if num_reviews:
            num_reviews = num_reviews.text
        else:
            num_reviews = "N/A"

        # Scrape additional product details from the product URL
        product_page = requests.get(product_url)
        product_soup = BeautifulSoup(product_page.content, "html.parser")
        
        product_description = product_soup.find("div", {"id": "productDescription"}).get_text(strip=True) if product_soup.find("div", {"id": "productDescription"}) else "N/A"
        asin = product_soup.find("th", text="ASIN").find_next("td").text if product_soup.find("th", text="ASIN") else "N/A"
        manufacturer = product_soup.find("th", text="Manufacturer").find_next("td").text if product_soup.find("th", text="Manufacturer") else "N/A"

        # Store the data in a dictionary
        product_data.append({
            "Product URL": product_url,
            "Product Name": product_name,
            "Product Price": product_price,
            "Rating": rating,
            "Number of Reviews": num_reviews,
            "Description": product_description,
            "ASIN": asin,
            "Manufacturer": manufacturer,
        })

# Scrape multiple pages (20 pages in this example)
for page_number in range(1, 21):
    page_url = f"{url}&page={page_number}"
    print(f"Scraping page {page_number}...\n")
    scrape_product_details(page_url)

# Close the WebDriver
driver.quit()

# Create a DataFrame and export to CSV
df = pd.DataFrame(product_data)
df.to_csv("amazon_product_data.csv", index=False)
