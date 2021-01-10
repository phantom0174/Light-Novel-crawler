import time
import os
import os.path
from os import path
from selenium import webdriver
from opencc import OpenCC

options=webdriver.ChromeOptions()
prefs={
     'profile.default_content_setting_values': {
        'images': 2,
        'javascript':2
    }
}
options.add_experimental_option('prefs',prefs)

#translate lang model
cc = OpenCC('s2tw')

def illSynRemover(string):
    return string.replace('\\','_').replace('/','_').replace(':','：').replace('*','＊').replace('?','？').replace('"','_').replace('<','＜').replace('>','＞').replace('|','｜')

url = input('Input the url of the book :')

book_url_mode = bool(True)
book_index = str()
if (url[-1] == 'm'):
    book_url_mode = False
    book_index = url.split('/')[-2]
else:
    book_index = url.split('=')[-1]

driver = webdriver.Chrome(chrome_options=options)
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
    if (spec_class == 'ccss'):
        if (class_link[i].get_attribute('innerHTML') != '&nbsp;'):
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

#Specific character removal

book_name_tw = illSynRemover(book_name_tw)
for i in range(len(title_order_tw)):
    title_order_tw[i] = illSynRemover(title_order_tw[i])
#

loc_link = int(0)
first_links = []
for i in ccount_book:
    if (book_url_mode == False):
        first_links.append(title_link[loc_link].split('/')[-1].split('.')[0])
    else:
        first_links.append(title_link[loc_link].split('=')[-1])
    loc_link += i

title_link.clear()

cmd1 = 'explorer "http://dl.wenku8.com/packtxt.php?aid=' + str(book_index) + '&vid='
cmd2 = '&charset=big5'

folder = 'D:\\' + str(book_name_tw)
if not os.path.isdir(folder):
    os.mkdir(folder)


download_link = 'C:\\Users\\lenovo\\Downloads\\'
for i in range(len(first_links)):
    os.system(cmd1 + first_links[i] + cmd2)
    while (path.exists(download_link + first_links[i] + ' big5.txt') == False):
        time.sleep(0.1)
    old_file = open(download_link + first_links[i] + ' big5.txt', 'r', encoding ='utf-8', errors = 'replace')
    txtInnerText = old_file.read()
    old_file.close()
    new_file = open(folder + '\\' + str(i + 1) + title_order_tw[i] + '.txt', 'w', encoding ='utf-8')
    new_file.write(txtInnerText)
    new_file.close()
    os.remove(download_link + first_links[i] + ' big5.txt')

os.system('taskkill /f /im msedge.exe')
print('Book Set Complete!')
