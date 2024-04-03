import csv
import time
from datetime import datetime
import selenium
import pymysql
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

db = pymysql.connect(host="imc.kean.edu",
                     user = "parekhad",
                     passwd="******",
                     db="test")

cursor = db.cursor()

url = "https://www.bing.com/maps/directions?cp=40.693655%7E-74.135056&lvl=11.0"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')

browser = webdriver.Chrome(options=chrome_options)

def grabAndSave(url):
    browser.get(url)
    time.sleep(3)

    start_input = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@title='From']")))
    start_input.send_keys("2403 Deerfield Dr, Edison, NJ 08820")
    start_input.send_keys(Keys.ENTER)

    end_input = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@title='To']")))
    end_input.send_keys("1000 Morris Ave, Union, NJ 07083")
    end_input.send_keys(Keys.ENTER)

    # Wait for the route to be calculated (you may need to adjust the wait time)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='directionsPanelRoot']/div[2]/div[2]/ul/li[1]/div/a/table/tr")))

    # Find and scrape the route information
    nav1 = browser.find_element(By.XPATH, "//*[@id='directionsPanelRoot']/div[2]/div[2]/ul/li[1]/div/a/table/tr/td[2]/div/table[1]/tr/td/div[3]/div[1]/span[1]")
    data1 = (nav1.text).splitlines()

    time1 = browser.find_element(By.XPATH, "//*[@id='directionsPanelRoot']/div[2]/div[2]/ul/li[1]/div/a/table/tr/td[3]/div/table/tr/td[3]/div[1]")
    timedata1 = (time1.text).splitlines()

    distance1 = browser.find_element(By.XPATH, "//*[@id='directionsPanelRoot']/div[2]/div[2]/ul/li[1]/div/a/table/tr/td[2]/div/table[1]/tr/td/div[1]/div")
    distancedata1 = (distance1.text).splitlines()

    print("Route: " + data1[0] +" | Time: " + timedata1[0] + " min | Distance: " + distancedata1[0])

    check1 = False

    try:
        check1 = browser.find_element(By.XPATH, "//*[@id='directionsPanelRoot']/div[2]/div[2]/ul/li[2]/div/a")
    except:
        print("There is no route 2!")

    if (check1):
        nav2 = browser.find_element(By.XPATH, "//*[@id='directionsPanelRoot']/div[2]/div[2]/ul/li[2]/div/a/table/tr/td[2]/div/table[1]/tr/td/div[3]/div[1]/span[1]")
        data2 = (nav2.text).splitlines()

        #print(data2[0])

        time2 = browser.find_element(By.XPATH, "//*[@id='directionsPanelRoot']/div[2]/div[2]/ul/li[2]/div/a/table/tr/td[3]/div/table/tr/td[3]/div[1]")
        timedata2 = (time2.text).splitlines()

        #print(timedata2[0])

        distance2 = browser.find_element(By.XPATH, "//*[@id='directionsPanelRoot']/div[2]/div[2]/ul/li[2]/div/a/table/tr/td[2]/div/table[1]/tr/td/div[1]/div")
        distancedata2 = (distance2.text).splitlines()

        if data2 and timedata2 and distancedata2:
            print("Route: " + data2[0] +" | Time: " + timedata2[0] + " min | Distance: " + distancedata2[0])
        else:
            print("Route 2 data not found or incomplete")
    
    routenum1 = 1
    eta1 = timedata1[0]
    routedistance1 = distancedata1[0]
    routeinfo1 = data1[0]
    
    if (check1):
        routenum2 = 2
        eta2 = timedata2[0]
        routedistance2 = distancedata2[0]
        routeinfo2 = data2[0]
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sql = "INSERT INTO `BingMaps` (`routenum`, `distance`, `route`, `time`, `current_time`) VALUES (%s, %s, %s, %s, %s)"

    try:
        with db.cursor() as cursor:
            cursor.execute(sql, (routenum1, routedistance1, routeinfo1, eta1, current_time)) #(routenum1, routedistance1, routeinfo1, eta1)
            db.commit()

            print("Route 1 data uploaded to database")

            if(check1):
                cursor.execute(sql, (routenum2, routedistance2, routeinfo2, eta2, current_time))
                db.commit()

                print("Route 2 uploaded to database")
        
    except Exception as e:
        print(e)

with open('BingMapsData.csv', 'a', newline='') as csvfile:
    fieldnames = ['Route number', 'Distance', 'Route', 'Time']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
    if csvfile.tell() == 0:
        writer.writeheader()
        

    try:
        while True:
            grabAndSave(url)
            time.sleep(900) #10 secs till it fetches information again -- change to 900
                
    except KeyboardInterrupt:
        print("\n\nStopped by Keyboard Interruption\n\n")
        pass

browser.close()