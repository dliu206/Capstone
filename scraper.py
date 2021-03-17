from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, StaleElementReferenceException
from bs4 import BeautifulSoup
from credentials import username2 as username, password2 as password
from time import sleep
import pickle
import numpy

# This script serves to scrape users interests from Facebook

# Your Facebook information
payload = {
    'email': username,
    'pass': password
}

# Setting up Selenium Webdriver
options = webdriver.ChromeOptions()
options.add_argument('--disable-notifications')
cdPath = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(executable_path=cdPath, options=options)


# Login set-up
def login():
    driver.get("https://mbasic.facebook.com/login")
    sleep(2)

    email_in = driver.find_element_by_xpath('//*[@id="m_login_email"]')
    email_in.send_keys(username)

    password_in = driver.find_element_by_name("pass")
    password_in.send_keys(password)

    login_btn = driver.find_element_by_name("login")
    login_btn.click()
    sleep(2)

    notNow = driver.find_element_by_class_name("bq")
    ac = ActionChains(driver)
    ac.move_to_element(notNow).click().perform()
    sleep(2)

login()


# Scrapes user profile link address's
# Link - Facebook group link
# Example:
# scrapeGroupPage("https://www.facebook.com/groups/#/members") where # is an group id
def scrapeGroupPage(link):
    # Navigates to group page
    driver.get(link)

    # Scrolls down 500 thousand times
    for i in range(0, 500000):
        print("Index: ", i)
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except:
            pass
        # Need it to sleep so the scroll down action can take place
        sleep(.5)

    # Dump HTML using BeautifulSoup
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    # Finds the links of all the profiles in memberlist
    names = soup.find_all('a',
                          class_="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 "
                                 "p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso "
                                 "i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p")

    # Adds each unique user profile link to a set
    people = set()
    for name in names:
        line = name['href']
        people.add(line)

    people = list(people)
    # Need numpy array type for enumerated filtering
    people = numpy.array(people)
    # Change pickle file name when you need to scrape for a new group
    pickle.dump(people, open("newGroup10.p", "wb"))

# Goes through profile links to find users interests
# Parameter - people - is output of scrapeGroupPage(link)
def parseGroupPage(people):
    # Creates or loads and index to checkpoint if program has to be stopped for any reason
    try:
        index = pickle.load(open("index2.p", "rb"))
    except:
        index = 0

    # Creates or loads pickle storage of parsed user profiles
    try:
        people2 = pickle.load(open("peopleHobbies3.p", "rb"))
    except:
        people2 = dict()


    # Loops through enumerated users
    for i in range(index, len(people)):
        print("Index: " + str(i))
        sleep(5)
        driver.get(people[i])
        try:
            try:
                driver.find_element_by_xpath("//a[@aria-label='View Main Profile']").click()
            except:
                pass
            link = driver.current_url + "/likes"
            driver.get(link)
            try:
                content = driver.find_element_by_xpath("//div[contains(@class, 'j83agx80 btwxx1t3 lhclo0ds')]")
                try:
                    print(content.text)
                    if len(content.text) > 0:
                        people2[link] = content.text
                except StaleElementReferenceException as err:
                    print(err)
            except InvalidArgumentException as err:
                print(err)
                sleep(5)
        except NoSuchElementException as err:
            sleep(5)
            print(err)
        index = index + 1
        if index % 10 == 0:
            pickle.dump(index, open("index2.p", "wb"))
            pickle.dump(people2, open("peopleHobbies3.p", "wb"))

    pickle.dump(people2, open("peopleHobbies3.p", "wb"))