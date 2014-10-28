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
import socket
import nltk
import errno
import collections
from sys import version
#excel api
from openpyxl import load_workbook
from webservice import WebService
from classification import Clasificator
reload(sys)


class Utils:

    # CONFIG ARGS
    __host = 'localhost'
    __port = '50005'
    __dir_images = 'figures/'
    __xls_range = 'G3:H875'  # 'G3:H875' #'G31:H31'
    __res = 'res/'

    # files to load
    __resources = './resources/'
    __comment_file = __resources + 'Comentarios_Peliculas.xlsx'
    __stopwords_file = __resources + 'stopwords.txt'
    __listaElem_file = __resources + 'listasElementosSubjetivos.pl'
    __Display = False

    # socket
    def __init__(self):
        if not os.path.exists(self.__dir_images):
            os.makedirs(self.__dir_images)
        if not os.path.exists(self.__res):
            os.makedirs(self.__res)
        #socket
        self.encoding = 'UTF-8'
        self.BUFSIZE = 1000240
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(None)
        try:
            self.socket.connect((self.__host, int(self.__port)))
            #self.encoding = encoding
            self.socket.sendall('RESET_STATS\0')
            r = self.socket.recv(self.BUFSIZE)

            if not r.strip('\0') == 'FL-SERVER-READY':
                raise Exception("Server not ready")
            pass
        except socket.error, v:
            errorcode = v[0]
            if errorcode == errno.ECONNREFUSED:
                print 'Error conexion servidor.'
                sys.exit()

    def setDisplay(self, Display):
        self.__Display = Display

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

    def lematization_freeling_client(self, comment, stopwords, domain):
        send = comment + '\n\0'
        self.socket.sendall(send.encode("UTF-8", 'strict'))

        done = False
        while not done:
            data = b""
            while not data:
                buffer = self.socket.recv(self.BUFSIZE)

                if buffer[-1] == '\0':
                    data += buffer[:-1]
                    done = True
                    break
                else:
                    data += buffer

        #print data
        data = data.rstrip('\x00')
        data = data.split('\n')

        #print data
        lista = []

        for words in data:
            if words.rstrip():
                args = words.split()
                if len(args) > 1:
                    lema = args[1]
                    tag = args[2]
                    if not re.match(r"^F.*", tag) and \
                    not re.match(r"^Z.*", tag) and \
                    not lema in stopwords and \
                    not lema in domain:
                        lema = unicode(lema, "UTF-8")
                        lista.append(lema)
        return lista

    def u(self, s, encoding='utf-8', errors='strict'):
        #ensure s is properly unicode.. wrapper for python 2.6/2.7,
        if version < '3':
        #ensure the object is unicode
            if isinstance(s, unicode):
                return s
            else:
                return unicode(s, encoding, errors=errors)
        else:
        #will work on byte arrays
            if isinstance(s, str):
                return s
            else:
                return str(s, encoding, errors=errors)

    def plot(self, negativeDic, n_groups, filename, totalwords):
        if negativeDic:
            xvalues = [seq[0] for seq in negativeDic][:n_groups]
            values = [seq[1] for seq in negativeDic][:n_groups]
            n_groups = min(n_groups, len(xvalues))
            ysize = max(values)
            fig, ax = plt.subplots()
            index = np.arange(n_groups)
            bar_width = 0.35
            opacity = 0.4
            error_config = {'ecolor': '0.3'}
            rect1 = plt.bar(index, values, bar_width, alpha=opacity, color='b',
                error_kw=error_config, label='Comentario')
            ax.set_xticklabels(xvalues, rotation=45)
            plt.xlabel('Comment')
            plt.ylabel('#Comments')
            plt.title('Top words')
            plt.xticks(index + bar_width / 2, xvalues)
            for rect in rect1:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., 1.02 * height,
                    '%.3f %%' % (float(height * 100) / totalwords), ha='center',
                    va='bottom', rotation=45)
            ax.set_ylim(0, ysize * 1.05)
            plt.tight_layout()
            fig.savefig(self.__dir_images + filename, dpi=90)
            if self.__Display:
                plt.show()

    def loadXLSFile(self):
        """Retorna una lista con los comentarios"""
        try:
            wb = load_workbook(self.__comment_file)
        except IOError:
            print ('File ' + self.__comment_file + ' not exists!')
            sys.exit(0)

        sheets = wb.get_sheet_names()
        sheet = wb.get_sheet_by_name(sheets[0])
        cell_range = sheet.range(self.__xls_range)
        return cell_range

    def loadStopwords(self):
        stopwords = {}
        try:
            for files in ['sw0.txt', 'sw1.txt', 'sw2.txt']:
                with open('./resources/' + files) as list1:
                    for word in list1:
                        if not word in stopwords.keys() and word.rstrip():
                            stopwords[word.rstrip()] = 0
                list1.close

        except IOError:
            print('File ' + self.__stopwords_file + ' not exists!')
            sys.exit(0)
        return stopwords

    def loadDomain(self):
        domain = {}
        try:
            with open('./resources/dominio.txt') as dominio:
                for word in dominio:
                    if word.rstrip():
                        domain[word.rstrip()] = 0
            dominio.close

        except IOError:
            print('File dominio.txt not exists!')
            sys.exit(0)
        return domain

    def loadSubjetiveElems(self):
        positiveWords = {}
        negativeWords = {}
        try:
            with open(self.__listaElem_file) as elemList:
                for line in elemList:
                    if line.rstrip():
                        m = re.match(r"elementoSubjetivo\('(.*)',(.*)\)+", line)
                        if m:
                            key = unicode(m.group(1), 'UTF-8')
                            if m.group(2) == '3':
                                positiveWords[key] = m.group(2)
                            else:
                                negativeWords[key] = m.group(2)
            elemList.close
        except IOError:
            print('File ' + self.__listaElem_file + ' not exists!')
            sys.exit(0)
        return (positiveWords, negativeWords)

    """Dado una lista de palabras, las guarda en un archivo con el nombre
    filename, el objetivo de esto es obtener datos estadisticos para realizar
    el informe"""
    def generateData(self, allWords, filename):
        saveAll = open(self.__res + filename, "w")
        save = ''
        for (lema, frec) in allWords:
            save = save + lema + ',' + '%d' % frec + '\n'
        saveAll.write(save.encode('utf-8', 'replace'))
        saveAll.close

    def generateStatisticData(self, allWords, posWords, negWords, t, n):
        data = open(self.__res + 'Data.txt', "w")
        inter = (len(posWords) + len(negWords)) - len(allWords)
        save = ''
        save = save + 'Total Lemma: %d \n' % len(allWords)
        save = save + 'Total Positive Lemma: %d\n' % len(posWords)
        save = save + 'Total Negative Lemma: %d\n' % len(negWords)
        save = save + 'Total negative & positive Lemma: %d\n' % inter
        save = save + 'Total comments: %d\n' % t
        save = save + 'Total negative comments: %d\n' % n
        save = save + 'Total positive comments: %d\n' % (t - n)
        data.write(save)
        data.close


def main():
    ws = False
    utils = Utils()
    utils.setDisplay(False)
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
    domain = utils.loadDomain()

    tokenizedComm = {}
    negComm = 0
    numComm = len(cell_range)
    it = 0
    for rows in cell_range:
        it = it + 1
        (valor, key) = rows
        if key.value != 3:
            if key.value < 3:
                insert = mydicneg
                negComm = negComm + 1
            else:
                insert = mydicpos
            #lematize and filter F words
            if ws:
                lista = webService.lematization_freeling_ws(valor.value,
                    stopwords)
            else:
                lista = utils.lematization_freeling_client(valor.value,
                    stopwords, domain)

            tokenizedComm[it - 1] = lista
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

    totalwords = len(allWords)
    # Graphs
    # A (Dina suggest)
    top = 50
    utils.plot(allWordsSorted, top, 'AllWords.png', totalwords)

    # B (Dina suggest)
    utils.plot(mydicnegSorted, top, 'NegativeWords.png', totalwords)
    utils.plot(mydicposSorted, top, 'PositiveWords.png', totalwords)

    # C (Dina suggest)
    utils.plot(dicNegC[:100], top, 'NegativeSubjetive.png', totalwords)
    utils.plot(dicPosC[:100], top, 'PositiveSubjetiveWords.png', totalwords)

    # Statistic data
    utils.generateData(mydicnegSorted, 'negativeWords.csv')
    utils.generateData(mydicposSorted, 'positiveWords.csv')
    utils.generateData(allWordsSorted, 'allWords.csv')
    utils.generateStatisticData(allWordsSorted, mydicposSorted, mydicnegSorted,
        numComm, negComm)

    print '\033[1m\033[31m' + 'Words All' + '\033[0m'
    for w in allWordsSorted[:100]:
        print w

    # Wrapping
    posWords = [word for (word, val) in mydicposSorted]
    negWords = [word for (word, val) in mydicnegSorted]

    return (posWords, negWords, list(positiveI), list(negativeI), tokenizedComm)


if __name__ == "__main__":
    (posWords, negWords, posI, negI, tokenizedComm) = main()
    classify = Clasificator()
    comments = classify.loadComments()
    (train, test) = classify.load_train_test_set()

    N = 20
    train_set = []
    for i in train:
        (com, value) = comments[i]
        if value < 3:
            splitted = tokenizedComm[i]
            train_set.append((classify.feature(N, com, splitted, posWords,
                negWords, posI, negI), "neg"))
        elif value > 3:
            splitted = tokenizedComm[i]
            train_set.append((classify.feature(N, com, splitted, posWords,
                negWords, posI, negI), "pos"))

    #print train_set
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    # Para testing se han excluido comentarios con puntuacion 3, es decir
    # se evaluan comentarios positivos y negativos.

    #for i in test:
    #    (com, value) = comments[i]
    #    if value != 3:
    #        splitted = tokenizedComm[i]
    #        print classifier.classify(classify.feature(N, splitted, posWords,
    #            negWords, posI, negI)) + "  %d" % value

    dev_set = []
    errorComments = []
    refset = collections.defaultdict(set)
    testset = collections.defaultdict(set)
    it = 0
    for i in test:
        (com, value) = comments[i]
        if value != 3:
            it = it + 1
            splitted = tokenizedComm[i]
            evaluate = classify.feature(N, com, splitted, posWords, negWords,
                posI, negI)
            if value < 3:
                dev_set.append((evaluate, "neg"))
                refset["neg"].add(it)
            else:
                dev_set.append((evaluate, "pos"))
                refset["pos"].add(it)
            res = classifier.classify(evaluate)
            testset[res].add(it)

            if res == "neg":
                if value < 3:
                    message = "OK"
                else:
                    message = "ERROR"
            else:
                if value > 3:
                    message = "OK"
                else:
                    message = "ERROR"

            if(message == "ERROR"):
                errorComments.append((com, value))
            #print  res + "  %d  " % value + message

    #for (c, v) in errorComments:
    #    if v < 3:
    #        print v, c
    #        print "\n"
    #print errorComments[0]
    classifier.show_most_informative_features(50)

    print 'Accuracy:', nltk.classify.accuracy(classifier, dev_set)
    print 'Precision Pos:', nltk.metrics.precision(refset['pos'], testset['pos'])
    print 'Recall Pos:', nltk.metrics.recall(refset['pos'], testset['pos'])
    print 'Precision Neg:', nltk.metrics.precision(refset['neg'], testset['neg'])
    print 'Recall Neg:', nltk.metrics.recall(refset['neg'], testset['neg'])