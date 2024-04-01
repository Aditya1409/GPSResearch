import csv
import time
from datetime import datetime
import selenium
from selenium import webdriver
import pymysql
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

db = pymysql.connect(host="imc.kean.edu",
                     user = "parekhad",
                     passwd="*******",
                     db="test",)

cursor = db.cursor()

url = "https://www.mapquest.com/directions/from/us/nj/edison/08820-4414/2403-deerfield-dr-40.58689,-74.36194/to/us/nj/union/07083-7133/1000-morris-ave-40.67848,-74.2343"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')

#chrome_options.binary_location = r'C:\Users\parek\chromedriver.exe'
browser = webdriver.Chrome(options=chrome_options)

def grabAndSave(url):
    browser.get(url)
    time.sleep(3)

    # Selects 1st route (unique) and retrieves route info

    nav1 = browser.find_element(By.XPATH, "//*[@id='contentContainer']/div[2]/div/div[4]/div/div[2]")
    data1 = (nav1.text).splitlines()

    # Retrieve time data from 1st route
    time1 = browser.find_element(By.XPATH, "//*[@id='contentContainer']/div[2]/div/div[4]/div/div[3]/strong/span[2]")
    timedata1 = (time1.text).splitlines()

    #Retrieves distance data from Route 1
    distance1 = browser.find_element(By.XPATH, "/html/body/div[1]/div[1]/nav/div[1]/div[3]/div[2]/div/div[4]/div/div[3]/strong/span[3]")
    distancedata1 = (distance1.text).splitlines()
    
    #Prints out Route 1 results
    print("Route: " + data1[0] +" | Time: " + timedata1[0] + " | Distance: " + distancedata1[0])



    #Prepare clicker for route 2
    check1 = False

    try:
        check1 = browser.find_element(By.XPATH, "/html/body/div[1]/div[1]/nav/div[1]/div[3]/div[2]/div/div[4]/div/div[1]/div[2]/button[2]")
    except:
        print("There is no route 2!")

    if (check1):
        #Get route info for route 2
        nav2 = browser.find_element(By.XPATH, "//*[@id='contentContainer']/div[2]/div/div[4]/div/div[2]")
        data2 = (nav2.text).splitlines()

        #print(data2[0])

        time2 = browser.find_element(By.XPATH, "//*[@id='contentContainer']/div[2]/div/div[4]/div/div[3]/strong/span[2]")
        timedata2 = (time2.text).splitlines()

        #print(timedata2[0])

        distance2 = browser.find_element(By.XPATH, "/html/body/div[1]/div[1]/nav/div[1]/div[3]/div[2]/div/div[4]/div/div[3]/strong/span[3]")
        distancedata2 = (distance2.text).splitlines()

        #print(distancedata2[0])6

        # print("Route: " + data2[0] +" | Time: " + timedata2[0] + " | Distance: " + distancedata2[0])
        if data2 and timedata2 and distancedata2:
            print("Route: " + data2[0] +" | Time: " + timedata2[0] + " | Distance: " + distancedata2[0])
        else:
            print("Route 2 data not found or incomplete")


        check2 = False

        try:
            check2 = browser.find_element(By.XPATH, "//*[@id='section-directions-trip-2']")
        except: 
            print("Route 3 not found")

    if (check2):
        #Get route info for route 3
        nav3 = browser.find_element(By.XPATH, "//*[@id='section-directions-trip-title-2']")
        data3 = (nav3.text).splitlines()

        time3 = browser.find_element(By.XPATH, "//*[@id='section-directions-trip-2']/div[1]/div/div[1]/div[1]")
        timedata3 = (time3.text).splitlines()

        distance3 = browser.find_element(By.XPATH, "//html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[3]/div[1]/div/div[1]/div[2]")
        #print(distance3.text)
        distancedata3 = (distance3.text).splitlines()
        #print(distancedata3)

        if data3 and timedata3 and distancedata3:
            print("Route: " + data3[0] +" | Time: " + timedata3[0] + " | Distance: " + distancedata3[0])
        else:
            print("Route 3 data not found or incomplete")
        

    

    routenum1 = 1
    eta1 = timedata1[0]
    routedistance1 = distancedata1[0]
    routeinfo1 = data1[0]

    if (check1):
        routenum2 = 2
        eta2 = timedata2[0]
        routedistance2 = distancedata2[0]
        routeinfo2 = data2[0]

    if (check2):
        routenum3 = 3
        eta3 = timedata3[0]
        routedistance3 = distancedata3[0]
        routeinfo3 = data3[0]

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sql = "INSERT INTO `MapQuest` (`routenum`, `distance`, `route`, `time`, `current_time`) VALUES (%s, %s, %s, %s, %s)"

    try:
        with db.cursor() as cursor:
            cursor.execute(sql, (routenum1, routedistance1, routeinfo1, eta1, current_time)) #(routenum1, routedistance1, routeinfo1, eta1)
            db.commit()

            print("Route 1 data uploaded to database")

            if(check1):
                cursor.execute(sql, (routenum2, routedistance2, routeinfo2, eta2, current_time))
                db.commit()

                print("Route 2 uploaded to database")
            
            if (check2):
                cursor.execute(sql, (routenum3, routedistance3, routeinfo3, eta3, current_time))
                db.commit()

                print("Route 3 uploaded to database")
            
    except Exception as e:
        print(e) #"Exception, there was an error uploading to the database"

#grabAndSave(url3)
    
with open('mapQuestData.csv', 'a', newline='') as csvfile:
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
