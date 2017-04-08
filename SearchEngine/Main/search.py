import dateutil.parser
import pysolr
import json
import urllib
import urllib2
from SearchEngine.Utility.lemmatizer import Lemmatiser
from SearchEngine.Utility.sql import MySQL

# Setup a Solr instance. The timeout is optional.

solr = pysolr.Solr('http://localhost:8983/solr/newtest/', timeout=10)
mysql = MySQL(host='104.199.252.211', database='INFORETRIEVAL', user='root', password='cz4034')
lemmatiser = Lemmatiser()


def smart_search(query):
    query_list = lemmatiser.generate_token_stream(query)
    lemma_list = lemmatiser.lemmatize_word(query_list, 'n')
    lemma_list = lemmatiser.lemmatize_word(lemma_list, 'a')
    lemma_list = lemmatiser.lemmatize_word(lemma_list, 'v')
    lemmatised_query = " ".join(str(word) for word in lemma_list)
    query_params = {'q': '"' + lemmatised_query + '"', 'wt': 'json'}
    url = 'http://localhost:8983/solr/cz4034_indexing/select?'
    url = url + urllib.urlencode(query_params)
    print url
    results = json.loads(urllib2.urlopen(url).read())
    # results = solr.search("'"+query+"'")
    print results
    result_id = []
    for i in range(0, len(results['response']['docs'])):
        article_id = results['response']['docs'][i]['id']
        # print "ID", article_id
        result_id.append(article_id)
        get_article_info(str(article_id))

    # TODO - Use database to extract article's first paragraph, second paragraph and title based on article ID
    number = results['response']['numFound']
    # if (number == 0): #do spellcheck
    #     collations = results['spellcheck']['collations']
    #     collationqueries = []
    #     for c in collations:
    #         if(c!='collation'):
    #             print c['collationQuery']
    #             collationqueries.append(c['collationQuery'])
    #     print (collationqueries)
    #     if(len(collationqueries)==0):
    #         print "entered ~1"
    #         query_params = {'q': query+'~1', 'wt': 'json'}
    #         url = 'http://localhost:8983/solr/newtest/select?'
    #         url = url + urllib.urlencode(query_params)
    #         results = json.loads(urllib2.urlopen(url).read())
    #         number = results['response']['numFound']
    # print results
    # print number
    #  for doc in results['response']['docs']:
    #      print doc['webTitle']
    #      doc['webTitle'][0] = doc['webTitle'][0].encode("utf-8")
    #      print type(doc['webTitle'][0])
    #      print type(doc['webTitle'][0])
    # encoded_str = results.encode("utf8")
    return number, results['response']['docs']


def quick_search(query):
    query_params = {'q': query, 'wt': 'json'}
    url = 'http://localhost:8983/solr/newtest/select?'
    url = url + urllib.urlencode(query_params)
    results = json.loads(urllib2.urlopen(url).read())
    result_id = []
    for i in range(0, len(results['response']['docs'])):
        result_id.append(results['response']['docs'][i]['id'])
    print results
    number = results['response']['numFound']
    print number
    return results


def get_article_info(article_id):
    print article_id
    # sql_query = "SELECT webTitle, firPara, secPara, webPublicationDate, wordCnt from crawlData WHERE id='{}'".format(article_id)
    sql_query = "SELECT webTitle, firPara, secPara, webPublicationDate, wordCnt from crawlData LIMIT 15"
    results = mysql.execute_query(sql_query)
    return results


def filter_by_year(results, year1, year2):
    filtered_result = []
    for webTitle, firPara, secPara, webPublicationDate, wordCnt in results:
        parsed_date = dateutil.parser.parse(str(webPublicationDate).upper())
        if year1 <= parsed_date.year <= year2:
            filtered_result.append((webTitle, firPara, secPara, wordCnt, parsed_date))
    return filtered_result
#
# quick_search('with weeks')
# smart_search('eight weeks')
# url = 'football/2017/apr/06/arsenal-mesut-ozil-theo-walcott'
# result = get_article_info(url)
# print len(result), result
# filtered_result = filter_by_year(result, 2016, 2016)
# print len(filtered_result), filtered_result
