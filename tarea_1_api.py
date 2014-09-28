#! /usr/bin/python
# -*- coding: utf-8 -*-

#imports
import sys
import os
import operator
import re
import numpy as np
import matplotlib.pyplot as plt
import getopt
#excel api
from openpyxl import load_workbook
from webservice import WebService
reload(sys)


class Utils:

    # CONFIG ARGS
    __host = "localhost"
    __port = "50005"
    __infile = "temp_file"
    __outfile = "data_file"
    __dir_images = 'figures/'

    # files to load
    __comment_file = 'Comentarios_Peliculas.xlsx'
    __xls_range = 'G3:H875'
    __stopwords_file = 'stopwords.txt'
    __listaElem_file = 'listasElementosSubjetivos.pl'

    def __init__(self):
        pass

    def parse(self, word):
        word = re.sub("á", u"á", word)
        word = re.sub("é", u"é", word)
        word = re.sub("í", u"í", word)
        word = re.sub("ó", u"ó", word)
        word = re.sub("ú", u"ú", word)
        word = re.sub("ñ", u"ñ", word)
        word = re.sub("Á", u"Á", word)
        word = re.sub("É", u"É", word)
        word = re.sub("Í", u"Í", word)
        word = re.sub("Ó", u"Ó", word)
        word = re.sub("Ú", u"Ú", word)
        word = re.sub("Ñ", u"Ñ", word)
        return word

    def tmpFile(self, comment):
        temp = open(self.__infile, "w")
        temp.write(comment.encode('utf-8', 'replace'))
        temp.flush
        temp.close

    def lematization_freeling_client(self, comment, stopwords):
        self.tmpFile(comment)
        command = "analyzer_client " + self.__host + ":" + self.__port \
            + "<" + self.__infile + " >" + self.__outfile
        os.system(command)

        lista = []
        with open(self.__outfile) as data:
            for words in data:
                if words.rstrip():
                    (_, lema, tag, _) = words.split()
                    if not re.match(r"^F.*", tag) and \
                    not re.match(r"^Z.*", tag) and \
                    not lema in stopwords:
                        lema = unicode(lema, "UTF-8")
                        lista.append(lema)
        return lista

    def plot(self, negativeDic, n_groups, filename):
        xvalues = [seq[0] for seq in negativeDic][:n_groups]
        values = [seq[1] for seq in negativeDic][:n_groups]
        n_groups = min(n_groups, len(xvalues))
        ysize = max(values)
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.35
        opacity = 0.4
        error_config = {'ecolor': '0.3'}
        plt.bar(index, values, bar_width, alpha=opacity, color='b',
            error_kw=error_config, label='Comentario')
        ax.set_xticklabels(xvalues, rotation=45)
        plt.xlabel('Comment')
        plt.ylabel('#Comments')
        plt.title('Top words')
        plt.xticks(index + bar_width / 2, xvalues)
        #index +bar_width
        #plt.legend()
        ax.set_ylim(0, ysize + 3)
        plt.tight_layout()
        fig.savefig(self.__dir_images + filename, dpi=90)
        #plt.show()

    def loadXLSFile(self):
        try:
            wb = load_workbook(self.__comment_file)
        except IOError:
            print ("File " + self.__comment_file + " not exists!")
            sys.exit(0)

        sheets = wb.get_sheet_names()
        sheet = wb.get_sheet_by_name(sheets[0])
        cell_range = sheet.range(self.__xls_range)
        return cell_range

    def loadStopwords(self):
        stopwords = {}
        try:
            with open(self.__stopwords_file) as stopwordsfile:
                for line in stopwordsfile:
                    if line.rstrip():
                        stopwords[line.rstrip()] = 0

            stopwordsfile.close
        except IOError:
            print("File " + self.__stopwords_file + " not exists!")
            sys.exit(0)
        return stopwords

    def loadSubjetiveElems(self):
        positiveWords = {}
        negativeWords = {}
        try:
            with open(self.__listaElem_file) as elemList:
                for line in elemList:
                    if line.rstrip():
                        m = re.match(r"elementoSubjetivo\('(.*)',(.*)\)+", line)
                        if m:
                            key = m.group(1)
                            if m.group(2) == '3':
                                positiveWords[key] = m.group(2)
                            else:
                                negativeWords[key] = m.group(2)
            elemList.close
        except IOError:
            print("File " + self.__listaElem_file + " not exists!")
            sys.exit(0)
        return (positiveWords, negativeWords)


def main():
    ws = False
    utils = Utils()
    webService = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "w", [])
    except getopt.GetoptError:
        print 'Invalid arguments'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-w':
            print 'Webservice Mode'
            ws = True
            webService = WebService()

    # used structures
    mydicneg = {}
    mydicpos = {}
    allWords = {}

    cell_range = utils.loadXLSFile()
    stopwords = utils.loadStopwords()
    (positiveWords, negativeWords) = utils.loadSubjetiveElems()

    # Iteration over cell_range
    for rows in cell_range:
        (valor, key) = rows
        if key.value < 3:
            insert = mydicneg
        else:
            insert = mydicpos
        #lematize and filter F words
        if ws:
            lista = webService.lematization_freeling_ws(valor.value, stopwords)
        else:
            lista = utils.lematization_freeling_client(valor.value, stopwords)

        list_aux = []
        for word in lista:
            if not word in allWords.keys():
                allWords[word] = 0
            if not word in insert.keys():
                insert[word] = 0
            if word not in list_aux:
                insert[word] = insert[word] + 1
                allWords[word] = allWords[word] + 1

    # ordering the dic (<)
    mydicnegSorted = sorted(mydicneg.iteritems(), key=operator.itemgetter(1),
        reverse=True)
    mydicposSorted = sorted(mydicpos.iteritems(), key=operator.itemgetter(1),
        reverse=True)
    allWordsSorted = sorted(allWords.iteritems(), key=operator.itemgetter(1),
        reverse=True)

    mydicnegList = [seq[0] for seq in mydicnegSorted][:100]
    mydicposList = [seq[0] for seq in mydicposSorted][:100]
    allWordsList = [seq[0] for seq in allWordsSorted][:100]

    # intersection
    negativeI = set(mydicnegList).intersection(negativeWords.keys())
    positiveI = set(mydicposList).intersection(positiveWords.keys())

    #for graph c
    dicPosC = {}
    dicNegC = {}

    # Transform intersection to dictionary
    for pos in positiveI:
        dicPosC[pos] = mydicpos[pos]

    for neg in negativeI:
        dicNegC[neg] = mydicneg[neg]

    dicNegC = sorted(dicNegC.iteritems(), key=operator.itemgetter(1),
        reverse=True)
    dicPosC = sorted(dicPosC.iteritems(), key=operator.itemgetter(1),
        reverse=True)


    # Print top 100 positive and negative Words
    print '\033[1m\033[31m' + 'Negative Words' + '\033[0m'
    for negative in negativeI:
        print '\t' + negative

    print '\n' + '\033[1m\033[32m' + 'Positive Words' + '\033[0m'
    for positive in positiveI:
        print '\t' + positive

    # Graphs
    # A (Dina suggest)
    utils.plot(allWordsSorted, 20, 'AllWords.png')

    # B (Dina suggest)
    utils.plot(mydicnegSorted, 20, 'NegativeWords.png')
    utils.plot(mydicposSorted, 20, 'PositiveWords.png')

    # C (Dina suggest)
    utils.plot(dicNegC[:100], 20, 'NegativeSubjetive.png')
    utils.plot(dicPosC[:100], 20, 'PositiveSubjetiveWords.png')

if __name__ == "__main__":
    main()
