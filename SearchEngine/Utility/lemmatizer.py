# -*- coding: utf-8 -*-
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import unicodedata


class Lemmatiser(object):
    def __init__(self):
        self.lemmatiser = WordNetLemmatizer()
        self.stopwords = set(stopwords.words("english"))

    def eliminate_stop_words(self, word_list):
        filtered_word_list = [word for word in word_list if word not in self.stopwords]
        return filtered_word_list


    def eliminate_punctuators(self, text):
        text=text.replace('’','')
        text= text.replace('‘','')
        text = text.replace('"', '')
        text = text.replace('“', '')
        #text=text.replace("'",'')
        text = text.replace('”', '')
        text = text.replace(':', '')
        #text = text.replace('-', '')
        return text

    def generate_token_stream(self, text):
        tokenizer=RegexpTokenizer(r'\w+')

        words = tokenizer.tokenize(text)
        return words

    def lemmatize_word(self, word_list, mode):
        """
        Lemmatizes the list of words
        :param word_list: List of all the words
        :return: the lemmatized version of the words
        """
        lemmatized_list = []
        for item in word_list:
            _item=unicodedata.normalize('NFKD',unicode(item))
            only_ascii= "".join([c for c in _item if not unicodedata.combining(c)])
            lemmatized_list.append(self.lemmatiser.lemmatize(only_ascii, mode))
        return lemmatized_list


def main():
    le = Lemmatiser()
    text = 'Bike enthusiasts the world over have been calling out for more cycle lines to be created'
    text = le.eliminate_punctuators(text)
    text = le.generate_token_stream(text)
    print text
    text=le.lemmatize_word(text,'v')
    print text
    #crawl.crawl_query('Nadal')
    #query = 'Rafael'
    #print query
    #query=query.replace(" ", "%20")
    #print query

if __name__ == '__main__':
    main()
