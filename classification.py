#! /usr/bin/python
# -*- coding: utf-8 -*-

from openpyxl import load_workbook
import sys
import re
import random


class Clasificator:

    def __init__(self):
        self.__xls_range = 'G3:H875'
        self.__resources = './resources/'
        self.__comment_file = self.__resources + 'Comentarios_Peliculas.xlsx'
        self.__train_file = './resources/train.txt'
        self.__test_file = './resources/test.txt'
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

    def generate_train_set(self, large, prop):
        (train, test) = self.get_train_test_set(large, prop)
        train = [str(i) for i in train]
        test = [str(i) for i in test]
        with open(self.__train_file, 'w') as save:
            save.write("\n".join(train))
        with open(self.__test_file, 'w') as save:
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
            if word in negSub: #elif
                features["subjetive_neg(%s)" % word] = comment.count(word)

        #custom features
        if self.generateHeuristic(pcomment):
            features["no_gusto"] = True
        #features["custom_pos"] = cant_pos
        #features["custom_neg"] = cant_neg
        #if cant_pos > 2:
        #    features["custom_pos"] = 2
        #if cant_neg > 2:
        #    features["custom_neg"] = 2

        return features

    def get_train_test_set(self, large, Prop):
        """Retorna un conjunto de comentarios(entrenamiento, test) dada la
        proporcion por parametro Prop = [0,1]"""
        elems = int(large * Prop)
        suc = [i for i in range(0, large)]
        train = random.sample(suc, elems)
        test = list(set(suc) - set(train))
        return (train, test)

    def load_train_test_set(self):
        train_list = []
        test_list = []
        with open(self.__train_file) as load:
            for line in load:
                if line.rstrip():
                    train_list.append(int(line.rstrip()))

        with open(self.__test_file) as load_test:
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

if __name__ == "__main__":
    c = Clasificator()
    #comments =  c.loadComments()
    #c.generate_train_set(len(comments), 0.7)

    com = "sd no ja gusto esa basura."
    print c.generateHeuristic(com)
