import csv
import time
from datetime import datetime
import selenium
from selenium import webdriver
import pymysql
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def grabAndSave(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(options=chrome_options)

    try:
        browser.get(url)
        time.sleep(3)

        # Find all buttons corresponding to the routes
        route_buttons = browser.find_elements(By.XPATH, "//*[@id='contentContainer']/div[2]/div/div[4]/div/div[1]/div[2]/button")

        # Iterate over each route button
        for i, button in enumerate(route_buttons, start=1):
            # Click on the button
            button.click()

            # Wait for the route information to load (if needed)
            time.sleep(2)  # Adjust the wait time as necessary

            # Scrape the information after clicking
            route_info_element = browser.find_element(By.XPATH, "//*[@id='contentContainer']/div[2]/div/div[4]/div/div[2]")
            route_info = route_info_element.text

            # Extract time data
            time_element = browser.find_element(By.XPATH, "//*[@id='contentContainer']/div[2]/div/div[4]/div/div[3]/strong/span[2]")
            time_data = time_element.text

            # Extract distance data
            distance_element = browser.find_element(By.XPATH, "//*[@id='contentContainer']/div[2]/div/div[4]/div/div[3]/strong/span[3]")
            distance_data = distance_element.text

            # Print the scraped information
            print(f"Route {i}: {route_info} | Time: {time_data} | Distance: {distance_data}")

            # Insert data into the database
            insert_data_into_database(i, route_info, time_data, distance_data)

    finally:
        browser.quit()

def insert_data_into_database(route_num, route_info, time_data, distance_data):
    db = pymysql.connect(host="imc.kean.edu", user="parekhad", passwd="*******", db="test")
    cursor = db.cursor()

    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO `MapQuest` (`routenum`, `distance`, `route`, `time`, `current_time`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (route_num, distance_data, route_info, time_data, current_time))
        db.commit()
        print(f"Route {route_num} data uploaded to database")
    except Exception as e:
        print(f"Error uploading Route {route_num} data to database: {e}")
    finally:
        cursor.close()
        db.close()

# Main function
if __name__ == "__main__":
    url = "https://www.mapquest.com/directions/from/us/nj/edison/08820-4414/2403-deerfield-dr-40.58689,-74.36194/to/us/nj/union/07083-7133/1000-morris-ave-40.67848,-74.2343"
    
    try:
        while True:
            grabAndSave(url)
            time.sleep(900)  # 15 minutes till it fetches information again
                
    except KeyboardInterrupt:
        print("\n\nStopped by Keyboard Interruption\n\n")
