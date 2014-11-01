#! /usr/bin/python
# -*- coding: utf-8 -*-

from openpyxl import load_workbook
import sys
import re
import random
import collections
import nltk
from nltk.metrics import ConfusionMatrix


class Clasificator:

    def __init__(self, Ver=2):
        self.__xls_range = 'G3:H875'
        self.__resources = './resources/'
        self.__comment_file = self.__resources + 'Comentarios_Peliculas.xlsx'
        self. __res = 'res/'
        self.Exc = 0
        if Ver == 2:
            self.Exc = 3
        pass

    def loadComments(self):
        try:
            wb = load_workbook(self.__comment_file)
        except IOError:
            print ('File ' + self.__comment_file + ' not exists!')
            sys.exit(0)

        sheets = wb.get_sheet_names()
        sheet = wb.get_sheet_by_name(sheets[0])
        cell_range = sheet.range(self.__xls_range)

        comments = []
        for rows in cell_range:
            (comment, valor) = rows
            comments.append((comment.value, valor.value))

        return comments

    def generate_train_set(self, large, prop, train_name, test_name):
        (train, test) = self.get_train_test_set(large, prop)
        train = [str(i) for i in train]
        test = [str(i) for i in test]
        with open(train_name, 'w') as save:
            save.write("\n".join(train))
        with open(test_name, 'w') as save:
            save.write("\n".join(test))

    def feature(self, N, pcomment, comment, positive, negative, posSub, negSub):
        """Lista de lemas en comment que corresponden al comentario a ser
     analizado. con las N palabras positivas y negativas, clasificamos con el
     feature positive(n):[True, False] si la palabra positiva n se encuentra en
     el comentario, analogo para negative."""
        features = {}
        # custom feature
        cant_pos = 0
        cant_neg = 0
        # features top N
        for i in range(0, N - 1):
            if positive[i] in comment:
                features["positive(%s)" % positive[i]] = True
                cant_pos = cant_pos + 1
            else:
                features["positive(%s)" % positive[i]] = False
            if negative[i] in comment:
                features["negative(%s)" % negative[i]] = True
                cant_neg = cant_neg + 1
            else:
                features["negative(%s)" % negative[i]] = False
        # features subjetive lists
        for word in comment:
            if word in posSub:
                features["subjetive_pos(%s)" % word] = comment.count(word)
            if word in negSub:
                features["subjetive_neg(%s)" % word] = comment.count(word)

        #custom features
        if self.generateHeuristic(pcomment):
            features["no_gusto"] = True

        return features

    def get_train_test_set(self, large, Prop):
        """Retorna un conjunto de comentarios(entrenamiento, test) dada la
        proporcion por parametro Prop = [0,1]"""
        elems = int(large * Prop)
        suc = [i for i in range(0, large)]
        train = random.sample(suc, elems)
        test = list(set(suc) - set(train))
        return (train, test)

    def load_train_test_set(self, train="./resources/train.txt",
        test="./resources/test.txt"):
        train_list = []
        test_list = []
        with open(train) as load:
            for line in load:
                if line.rstrip():
                    train_list.append(int(line.rstrip()))

        with open(test) as load_test:
            for line in load_test:
                if line.rstrip():
                    test_list.append(int(line.rstrip()))
        load.close
        load_test.close
        return (train_list, test_list)

    def generateHeuristic(self, com):
        heu = ["gusto", "gustó", "vi", "ví"]
        for elem in heu:
            reg = r".*no (\w+) %s.*" % elem
            if re.match(reg, com, re.IGNORECASE):
                return True
        return False

    def saveMetrics(self, toSave, file_name="./res/Metrics.txt"):
        saveFile = open(file_name, 'w')
        save = ''
        for k in sorted(toSave.keys()):
            save = save + k + ' : ' + str(toSave[k]) + '\n'
        saveFile.write(save)
        saveFile.close

    def process(self, posWords, negWords, posI, negI, tokenizedComm,
        train_file="./resources/train.txt", test_file="./resources/test.txt"):
        comments = self.loadComments()
        (train, test) = self.load_train_test_set(train_file, test_file)

        N = 20
        train_set = []
        for i in train:
            (com, value) = comments[i]
            if value != self.Exc:
                if value < 3:
                    splitted = tokenizedComm[i]
                    train_set.append((self.feature(N, com, splitted, posWords,
                        negWords, posI, negI), "neg"))
                else:
                    splitted = tokenizedComm[i]
                    train_set.append((self.feature(N, com, splitted, posWords,
                        negWords, posI, negI), "pos"))

        classifier = nltk.NaiveBayesClassifier.train(train_set)

        # Para testing se han excluido comentarios con puntuacion 3, es decir
        # se evaluan comentarios positivos y negativos.

        dev_set = []
        errorComments = []
        refset = collections.defaultdict(set)
        testset = collections.defaultdict(set)
        ref_list = []
        test_list = []

        it = 0
        for i in test:
            (com, value) = comments[i]
            if value != self.Exc:
                it = it + 1
                splitted = tokenizedComm[i]
                evaluate = self.feature(N, com, splitted, posWords, negWords,
                    posI, negI)
                if value < 3:
                    dev_set.append((evaluate, "neg"))
                    refset["neg"].add(it)
                    ref_list.append("neg")
                else:
                    dev_set.append((evaluate, "pos"))
                    refset["pos"].add(it)
                    ref_list.append("pos")
                res = classifier.classify(evaluate)
                testset[res].add(it)
                test_list.append(res)
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

        classifier.show_most_informative_features(20)

        # confusion matrix
        cm = ConfusionMatrix(ref_list, test_list)
        cm = '\n' + cm.pp(sort_by_count=True, show_percents=False, truncate=9)

        # data metrics
        accuracy = nltk.classify.accuracy(classifier, dev_set)
        pPos = nltk.metrics.precision(refset['pos'], testset['pos'])
        rPos = nltk.metrics.recall(refset['pos'], testset['pos'])
        pNeg = nltk.metrics.precision(refset['neg'], testset['neg'])
        rNeg = nltk.metrics.recall(refset['neg'], testset['neg'])
        Metrics = {'Accuracy': accuracy,
            'Precision Pos': pPos,
            'Recall Pos': rPos,
            'Precision Neg': pNeg,
            'Recall Neg': rNeg,
            'Confusion Matrix': cm}

        for m in sorted(Metrics.keys()):
            print m, Metrics[m]

        num = [accuracy, pPos, rPos, pNeg, rNeg]
        return (Metrics, num)
        #self.saveMetrics(Metrics)

if __name__ == "__main__":
    c = Clasificator()
    coments = c.loadComments()
    for i in range(0, 30):
        train = "./resources/statistic/train" + str(i) + ".txt"
        test = "./resources/statistic/test" + str(i) + ".txt"
        c.generate_train_set(len(coments), 0.7, train, test)