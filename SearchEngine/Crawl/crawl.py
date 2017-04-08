import datetime, dateutil.parser
import json
import os
import re
import requests
import urllib2
from BeautifulSoup import BeautifulSoup
from SearchEngine.Main import indexing
from SearchEngine.Utility.lemmatizer import Lemmatiser
from SearchEngine.Utility.sql import MySQL
from string import punctuation

# TODO ---- Sort out encoding issue


class Crawl:
    api_key = "44fe4958-51a9-48b2-acdd-7b8277b2ca83"
    api_test = 'test'
    base_url = 'http://content.guardianapis.com/search'
    page_size = 10
    crawled_information = {}
    sections = ('sport', 'football')
    lemmatiser = Lemmatiser()
    my_sql = MySQL(host='104.199.252.211', database='INFORETRIEVAL', user='root', password='cz4034')

    def __init__(self):
        print "Crawling initialised."

    def get_section_arg(self, section):
        if section in self.sections:
            return '?section=' + section
        else:
            return '?section=' + 'sport'

    def get_page_id_arg(self, page_id):
        return '&page=' + str(page_id)

    def get_api_key_arg(self):
        return "&api-key=" + self.api_test

    def get_query_arg(self, query):
        return "&q=" + query

    def extract_article_paragraphs(self, web_url):
        print "extract_article_paragraphs()"
        print "url:", web_url
        try:
            urlf = urllib2.urlopen(web_url)
            article_html = urlf.read()
            paragraph_start = int(article_html.find('<p>'))
            paragraph_end = int(article_html.rfind('</p>'))
            soup = BeautifulSoup(article_html[paragraph_start:paragraph_end + 4])
            invalid_tags = ['a', 'span', 'em', 'strong', 'strike']
            ignore_tags = ['br', 'time']
            # Replace tags with the text within them
            for tag in invalid_tags:
                for match in soup.findAll(tag):
                    match.replaceWithChildren()

            # Replace tags with ""
            for tag in ignore_tags:
                for match in soup.findAll(tag):
                    match.replaceWith("")

            soup = soup.findAll('p')
            count = 0
            word_count = 0
            paragraph_list = []
            for paragraph in soup:
                paragraph = str(paragraph)
                if '<p>' in paragraph:
                    text = paragraph.strip('<p>').strip('</p>')
                    # Do not add again if it already exists
                    if text not in paragraph_list:
                        count += 1
                        text = self.lemmatiser.eliminate_punctuators(text)
                        r = re.compile(r'[{}]'.format(punctuation))
                        new_text = r.sub(' ', text)
                        word_count += len(new_text.split())
                        paragraph_list.append(text)
                        # print count, len(text), text
            # print " "
            # print "Word-count:", word_count
            return (paragraph_list, word_count)
        except urllib2.URLError:
            print "URLError encountered."

    def extract_article_images(self, web_url):
        print "extract_article_images()"
        try:
            urlf = urllib2.urlopen(web_url)
            article_html = urlf.read()
            image_start = int(article_html.find('<picture>'))
            image_end = int(article_html.rfind('</picture>'))
            soup = BeautifulSoup(article_html[image_start:image_end + 4])
            invalid_tags = ['a', 'span', 'em', 'strong', 'strike', 'class']
            ignore_tags = ['br', 'time', 'class']
            # Replace tags with the text within them
            for tag in invalid_tags:
                for match in soup.findAll(tag):
                    match.replaceWithChildren()

            # Replace tags with ""
            for tag in ignore_tags:
                for match in soup.findAll(tag):
                    match.replaceWith("")

            soup = soup.findAll('img')
            count = 0
            word_count = 0
            image_list = []
            for image in soup:
                # print image, type(image), "\n"
                image = str(image)
                if '<img' in image:
                    # print image
                    image = image.replace('amp;', '')
                    caption_start = int(image.find('alt'))
                    caption = image[caption_start+5:]
                    caption_end = int(caption.find('"'))
                    caption = caption[:caption_end]
                    image_url_start = int(image.find('src'))
                    image_url = image[image_url_start+5:]
                    image_url_end = int(image_url.find('"'))
                    image_url = image_url[:image_url_end]
                    # print caption, image_url
                    if len(image_url) > 1 and len(caption) > 1:
                        image_list.append({'caption': caption, 'url': image_url})
            return image_list, len(image_list)
        except urllib2.URLError:
            print "URLError encountered."

    def crawl_page(self, crawl_url, section, page_id):
        print "\ncrawl_page()"
        # print "Page id:", page_id
        self.crawled_information.update()
        crawl_url += self.get_page_id_arg(page_id)
        # print "Url: ", crawl_url
        response = requests.get(crawl_url)
        dictionary = {}
        # print dictionary
        dictionary.update(response.json())
        # print crawl_url, dictionary
        articles = dictionary['response']['results']
        # print "Number of articles:", len(articles)
        article_count = 0
        # TODO ---- This part needs to be modified to dump data for every crawled page
        dir_path = os.path.join(os.getcwd(), 'json_files')
        file_name = "crawl_info_" + section + "_" + str(page_id) + ".json"
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'w') as json_file:
            for article in articles:
                print "\npage:", page_id, "article:", article_count+1, "article:", article
                article_id = article['id']
                article_web_url = article['webUrl']
                # print article_count, article['apiUrl'], article_id
                (paragraphs, word_count) = self.extract_article_paragraphs(article_web_url)
                (images, img_count) = self.extract_article_images(article_web_url)
                print "Images:", img_count, images
                # print "Words in paragraph:", word_count
                # print "Paragraphs for article:", len(paragraphs), ":", paragraphs
                if len(paragraphs) < 1:
                    paragraphs.append("")
                if len(paragraphs) < 2:
                    paragraphs.append("")

                # print dictionary['response']['results'][article_count]['webTitle']
                dictionary['response']['results'][article_count].update(
                    {'firPara': paragraphs[0], 'secPara': paragraphs[1], "wordCnt": word_count, 'images': images,
                     'img_count': img_count})
                article_count += 1
                publication_date = article['webPublicationDate']
                parsed_date = dateutil.parser.parse(publication_date)
                sql_query = "INSERT INTO INFORETRIEVAL.Crawl (apiUrl, firPara, secPara, id, isHosted, sectionId, sectionName, articleType, webPublicationDate, webTitle, webUrl, wordCnt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (article['apiUrl'], paragraphs[0], paragraphs[1], article['id'], 'True', article['sectionId'], article['sectionName'], article['type'], parsed_date, article['webTitle'], article['webUrl'], word_count)
                # Dump crawled data into DB
                # self.my_sql.insert_query(sql_query, values)
                # print "Updated dictionary:", dictionary
            json.dump(dictionary, json_file, sort_keys=True)
        # indexing.get_file_to_index(file_path)
        return article_count

    def crawl_by_section(self, section, page_id, query=None):
        print "crawl_by_section(), Query:", query
        print "Crawling section:", section
        crawl_url = self.base_url + self.get_section_arg(section) + self.get_api_key_arg()
        if query is not None:
            crawl_url += self.get_query_arg(query)
        print crawl_url
        response = requests.get(crawl_url)
        dictionary = {}
        dictionary.update(response.json())
        total_articles = int(dictionary['response']['total'])
        number_of_pages = int(dictionary['response']['pages'])
        crawled_pages = 0
        # print dictionary
        print "Total number of articles:", total_articles
        print "Total number of pages:", number_of_pages
        for page in range(page_id, page_id+1):
            print "Crawling page:", page
            crawled_pages += 1
            crawled_articles = self.crawl_page(crawl_url, section, page)
        crawled_articles = (crawled_pages * 10 - 1) + (crawled_articles % 10) + (crawled_articles / 10)
        dictionary['response'].update({'total': crawled_articles, 'pages': crawled_pages})
        dir_path = os.path.join(os.getcwd(), 'json_files')
        file_name = "info_" + section + ".json"
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'w') as json_file:
            json.dump(dictionary, json_file, sort_keys=True)
        return crawled_articles

    def crawl_all_sections(self, page_id, query=None):
        '''
        Case for the selection of crawling all sections or crawling by query
        :param query:
        :param page_id: 
        :return: None
        '''
        # Crawls both 'Football' and 'Sport' sections
        crawled_articles = 0
        if query is not None:
            for section in self.sections:
                crawled_articles += self.crawl_by_section(section, page_id, query)
        # Crawls query in both 'Football' and 'Sport' sections
        else:
            for section in self.sections:
                crawled_articles += self.crawl_by_section(section, page_id)
        return crawled_articles

    def crawl_dynamic(self, section_list=['sport', 'football'], query=None, page_id=2):
        print "crawl_dynamic()"
        if query is not None:
            crawled_articles = self.crawl_all_sections(page_id, query=query)
        elif len(section_list) == 1:
            crawled_articles = self.crawl_by_section(section_list[0], page_id)
        else:
            crawled_articles = self.crawl_all_sections(page_id)
        return crawled_articles


def main():
    crawl = Crawl()
    articles = crawl.crawl_dynamic()
    print "Articles crawled", articles
    # crawl.crawl_query('Nadal')
    # query = 'Rafael'
    # print query
    # query=query.replace(" ", "%20")
    # print query
    # strs = "Johnny.Appleseed!is:a*good&farmer"

if __name__ == '__main__':
    main()