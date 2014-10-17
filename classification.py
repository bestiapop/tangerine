#! /usr/bin/python
# -*- coding: utf-8 -*-

from openpyxl import load_workbook
import sys
import random

class Clasificator:

    def __init__(self):
        self.__xls_range = 'G3:H875'
        self.__resources = './resources/'
        self.__comment_file = self.__resources + 'Comentarios_Peliculas.xlsx'
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


    def feature(self, N, comment, positive, negative):
        """Lista de lemas en comment que corresponden al comentario a ser
     analizado. con las N palabras positivas y negativas, clasificamos con el
     feature positive(n):[True, False] si la palabra positiva n se encuentra en
     el comentario, analogo para negative."""
        features = {}
        for i in range(0, N - 1):
            if positive[i] in comment:
                features["positive(%d)" % i] = True
            else:
                features["positive(%d)" % i] = False
            if negative[i] in comment:
                features["negative(%d)" % i] = True
            else:
                features["negative(%d)" % i] = False
        return features


    def get_train_test_set(self, large, Prop):
        """Retorna un conjunto de comentarios(entrenamiento, test) dada la
        proporcion por parametro Prop = [0,1]"""
        elems = int(large * Prop)
        suc = [i for i in range(0, large - 1)]
        train = random.sample(suc, elems)
        test = list(set(suc) - set(train))
        return (train, test)

