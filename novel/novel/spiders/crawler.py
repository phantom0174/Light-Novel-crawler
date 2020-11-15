import scrapy
from opencc import OpenCC
import os

all = [[]]
del(all[0])

class ncrawler(scrapy.Spider):
    name = 'n'

    #Things of web links
    start_urls = [input('Input the url of the book :')]
    domain = str()
    domain_set = bool(0)

    #Crawler mode set
    parse_mode = int(1)
    next_chapter = int(0)

    #Index of txt inputing
    cur_book_chapter_count = int(0)
    cur_book = int(0)

    #Temp
    book_text = []

    #Book basic info
    book_name_tw = str()
    book_ccount = []
    title_order_tw = []
    chapter_name_tw = []
    chapter_links = []

    def parse(self, response):
        if(ncrawler.domain_set == bool(0) and ncrawler.start_urls[0][-1] == 'm'):
            ncrawler.domain = ncrawler.start_urls[0].split('i')[0]

        if (ncrawler.parse_mode == 1):
            book_name_link = response.xpath('//*[@id="title"]/text()')
            order_links = response.xpath('//td[contains(@class,"css")]')

            book_name = book_name_link.get()

            #Partial basic info
            class_order = []
            title_order = []
            chapter_name = []
            chapter_partial_links = []

            for i in order_links:
                spec_class = i.xpath('@class').get()
                if (spec_class == 'ccss' and i.xpath('string()').get() != '\xa0'):
                    class_order.append(spec_class)
                    chapter_name.append(i.xpath('a/text()').extract())
                    chapter_partial_links.append(i.css('a::attr(href)').extract())
                elif (spec_class == 'vcss'):
                    class_order.append(spec_class)
                    title_order.append(i.xpath('text()').get())

            class_order.append('vcss')

            # find the chapter count of each book
            chapter_count = int(0)
            for i in class_order:
                if (i != 'vcss'):
                    chapter_count += 1
                else:
                    ncrawler.book_ccount.append(chapter_count)
                    chapter_count = 0

            ncrawler.book_ccount.remove(0)
            class_order.clear()

            # translate
            cc = OpenCC('s2tw')
            ncrawler.book_name_tw = cc.convert(book_name)
            #

            for i in title_order:
                ncrawler.title_order_tw.append(cc.convert(i))

            for i in range(len(chapter_name)):
                ncrawler.chapter_name_tw.append(cc.convert(str(chapter_name[i])))

            title_order.clear()
            chapter_name.clear()

            #Specific character removal
            ncrawler.book_name_tw = ncrawler.book_name_tw.replace('\\','_').replace('/','_').replace(':','：').replace('*','＊').replace('?','？').replace('"','_').replace('<','＜').replace('>','＞').replace('|','｜')
            for i in range(len(ncrawler.title_order_tw)):
                ncrawler.title_order_tw[i] = ncrawler.title_order_tw[i].replace('\\','_').replace('/','_').replace(':','：').replace('*','＊').replace('?','？').replace('"','_').replace('<','＜').replace('>','＞').replace('|','｜')
            #

            for i in chapter_partial_links:
                ncrawler.chapter_links.append(ncrawler.domain + i[0])

            ncrawler.parse_mode = 2
        elif(ncrawler.parse_mode == 2):
            cc = OpenCC('s2tw')
            chapter_title = cc.convert(response.xpath('//*[@id="title"]/text()').get())

            if(chapter_title[-3:-1] != '插圖'):
                text_links = response.xpath('//*[@id="content"]/text()')
                inner_string = str()

                for i in text_links:
                    inner_string = inner_string + i.get()

                ncrawler.book_text.append(inner_string)
            ncrawler.cur_book_chapter_count += 1

            if(ncrawler.cur_book_chapter_count == ncrawler.book_ccount[ncrawler.cur_book]):
                temp = []

                for i in ncrawler.book_text:
                    temp.append(i)

                all.append(temp)
                ncrawler.book_text.clear()
                ncrawler.cur_book += 1
                ncrawler.cur_book_chapter_count = 0
            ncrawler.next_chapter += 1

            if(ncrawler.next_chapter > (len(ncrawler.chapter_links) - 1)):
                chapter_title_count = int(0)

                for i in range(len(ncrawler.title_order_tw)):
                    folder = 'D:\\' + ncrawler.book_name_tw
                    if not os.path.isdir(folder):
                        os.mkdir(folder)

                    path = str(folder + '\\' + str(i + 1) + ncrawler.title_order_tw[i] + '.txt')
                    f = open(path, 'w', encoding='UTF-8')
                    for j in range(len(all[i])):
                        if (ncrawler.chapter_name_tw[chapter_title_count][2:-2] != '插圖'):
                            chapter_head = str('//' + ncrawler.chapter_name_tw[chapter_title_count][2:-2])
                            f.write(chapter_head)
                            cc = OpenCC('s2tw')
                            for k in all[i][j]:
                                f.write(cc.convert(k))

                        chapter_title_count += 1
                    f.close()
                    
        if(ncrawler.parse_mode == 2 and ncrawler.next_chapter <= len(ncrawler.chapter_links) - 1):
            yield scrapy.Request(url=ncrawler.chapter_links[ncrawler.next_chapter], callback=self.parse)