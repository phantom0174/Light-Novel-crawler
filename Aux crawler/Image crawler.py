import os
import urllib
from urllib.request import urlopen
from selenium import webdriver
from opencc import OpenCC

options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
        'javascript': 2
    }
}
options.add_experimental_option('prefs', prefs)

# translate lang model
cc = OpenCC('s2tw')
print('Input the url of the book.')
url = input()
driver = webdriver.Chrome(chrome_options=options)
driver.implicitly_wait(30)
driver.get(url)

# find all class include "css"

uti_path = '//td[contains(@class,"css")]'
bookname_path = '//*[@id="title"]'
class_link = driver.find_elements_by_xpath(uti_path)
bookname_link = driver.find_elements_by_xpath(bookname_path)

book_name_tw = cc.convert(bookname_link[0].get_attribute('innerHTML'))

class_order = []
title_order_tw = []

for i in range(len(class_link)):
    spec_class = class_link[i].get_attribute('class')
    if (spec_class == 'ccss' and class_link[i].get_attribute('innerHTML') != '&nbsp;'):
        class_order.append(spec_class)
    if (spec_class == 'vcss'):
        class_order.append(spec_class)
        title_order_tw.append(cc.convert(class_link[i].get_attribute('innerHTML')))

class_order.append('vcss')

# find the chapter count of each book
ccount_book = []
chapter_count = int(0)
for i in range(len(class_order)):
    if (class_order[i] != 'vcss'):
        chapter_count += 1
    else:
        ccount_book.append(chapter_count)
        chapter_count = 0

ccount_book.remove(0)
class_order.clear()

# find the real chapter title (class = 'ccss')

regular_path = '//td[contains(@class,"ccss")]//a'
chapter_link = driver.find_elements_by_xpath(regular_path)

chapter_title_tw = []
title_link = []

for i in range(len(chapter_link)):
    chapter_title_tw.append(cc.convert(chapter_link[i].get_attribute('text')))
    title_link.append(chapter_link[i].get_attribute('href'))

driver.quit()

folder = 'D:\\' + book_name_tw
if not os.path.isdir(folder):
    os.mkdir(folder)

img_folder = 'D:\\' + book_name_tw + '\\@插圖'

if not os.path.isdir(img_folder):
    os.mkdir(img_folder)

volume_img_count = int(1)
for i in range(len(chapter_title_tw)):
    if (chapter_title_tw[i] == '插圖'):

        uti_img_url = title_link[i]
        img_driver = webdriver.Chrome(chrome_options=options)
        img_driver.implicitly_wait(30)
        img_driver.get(uti_img_url)

        img_find = '//img[contains(@class,"imagecontent")]'
        img_path = img_driver.find_elements_by_xpath(img_find)

        if(len(img_path) != 0):
            book_count = int(0)

            for j in range(len(ccount_book)):
                book_count += ccount_book[j]
                if (i + 1 <= book_count):
                    book_count = j
                    break

            local_path = img_folder + '\\' + str(volume_img_count) + title_order_tw[book_count]
            if not os.path.isdir(local_path):
                os.mkdir(local_path)

        for j in range(len(img_path)):
            img_url = img_path[j].get_attribute('src')
            urllib.request.urlretrieve(img_url, local_path + '\\' + str(j + 1) + '.jpg')
            print(img_url)

        img_driver.quit()

        volume_img_count += 1

print('Book Set Complete!')
