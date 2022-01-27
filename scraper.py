import logging
import math

from PIL import ImageChops, Image

from selenium import webdriver
from selenium.webdriver.common.by import By

import os

# good start at 1048576

SETTING_PATH = "settings.txt"
IMG_PATH = "E:\Stuff\lightshot-scraper-images"
TEMP_PATH = "./temp"
WEB_PATH = "https://prnt.sc/"
# LIMIT = 500000

# some starting binary data of the removed screenshot image
REMOVED_IMG = None
count = 0
valid_chars = {}

def saveCount():
    settings_file = open(SETTING_PATH, "w")
    # print("Saving count: " + str(count))
    settings_file.write(str(count))


def loadCount():
    count = 0
    try:
        settings_file = open(SETTING_PATH, "r")
        count = int(settings_file.readline())
    finally:
        return count


def saveImage(path, img):
    file = open(path, "wb")
    file.write(img)
    file.close()


def init(driver):
    if not os.path.exists(IMG_PATH):
        os.makedirs(IMG_PATH)

    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH)

    # Accept cookie banner
    driver.get("https://prnt.sc")
    try:
        cookie_accept = driver.find_element(By.CLASS_NAME, "css-47sehv")
        cookie_accept.click()
    except:
        logging.exception("Stupid cookie banner")

    # Find removed screenshot img
    driver.get("https://prnt.sc/0")
    try:
        global REMOVED_IMG
        delete_name = "delete_tmp.png"
        saveImage(TEMP_PATH + "/" + delete_name,
                  driver.find_element(By.XPATH, "/html/body/div[4]/div/div/img").screenshot_as_png)
        REMOVED_IMG = Image.open(TEMP_PATH + "/" + delete_name)
    except:
        logging.exception("Screenshot removed image wasn't found")


def asHex(number):
    return hex(number).replace('0x', '')


def rmsdiff(im1, im2):
    """ Calculate the root-mean-square difference between two images

    Source: https://stackoverflow.com/a/40176818 """
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares / float(im1.size[0] * im1.size[1]))
    return rms


def main():
    global count, REMOVED_IMG
    count = loadCount()
    print("Starting count: " + str(count))
    driver = webdriver.Firefox()

    init(driver)

    # max len of string to compare
    max_string_len = 1000
    while 1:
        try:
            url = WEB_PATH + asHex(count)
            print(url)
            driver.get(url)

            path = IMG_PATH + "/" + "img_" + str(count) + ".png"
            saveImage(path, driver.find_element(By.XPATH, "/html/body/div[4]/div/div/img").screenshot_as_png)
            tmp = Image.open(path)
            saveCount()
            # compares first n characters, n chosen arbitrarily above
            if rmsdiff(tmp, REMOVED_IMG) <= 0:
                print(rmsdiff(tmp, REMOVED_IMG))
                tmp.close()
                os.remove(path)

        except:
            logging.exception("Error on website open?")

        count = count + 1

    driver.close()


if __name__ == "__main__":
    main()
