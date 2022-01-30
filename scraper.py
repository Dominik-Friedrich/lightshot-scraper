import logging
import math
import random

from PIL import ImageChops, Image

from selenium import webdriver
from selenium.webdriver.common.by import By

import os

# good start at 1048576

SETTING_PATH = "settings.txt"
IMG_PATH = "E:\Stuff\lightshot-scraper-images"
TEMP_PATH = "./temp"
WEB_PATH = "https://prnt.sc/"


def loadValidCharacters():
    chars = ""
    try:
        settings_file = open(SETTING_PATH, "r")
        chars = settings_file.readline()
    finally:
        return chars


def generateRandUrl(characters, length):
    url = ""
    for i in range(length):
        url += random.choice(characters)
    return url


def loadFilterImages(path):
    filter_images = []
    for root, dirs, files in os.walk(path):
        for file in files:
            filter_images.append(str(root) + "/" + str(file))
    return filter_images


def deleteImage(filter_images, cmp_img_path):
    delete = False
    try:
        cmp = Image.open(cmp_img_path)
        for img_path in filter_images:
            tmp = Image.open(img_path)
            if rmsdiff(cmp, tmp) <= 0:
                delete = True
            tmp.close()
            if delete:
                break
        cmp.close()
    except:
        logging.exception("Shitty image paths")
    return delete


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
    valid_chars = loadValidCharacters()
    filter_images = loadFilterImages(TEMP_PATH)

    driver = webdriver.Firefox()

    init(driver)

    url_length = 6

    count = 0
    while 1:
        try:
            url_end = generateRandUrl(valid_chars, url_length)
            url = WEB_PATH + url_end

            driver.get(url)

            path = IMG_PATH + "/" + "img_" + url_end + ".png"
            saveImage(path, driver.find_element(By.XPATH, "/html/body/div[4]/div/div/img").screenshot_as_png)

            print(str(count) + ": " + url)

            if deleteImage(filter_images, path):
                os.remove(path)

        except:
            logging.exception("Stupid cookie banner")
            continue
        count = count + 1

    driver.close()


if __name__ == "__main__":
    main()
