#! /usr/bin/python
# -*- coding: utf-8 -*-

#imports
import sys
import operator
import urllib
import re

#excel api
from openpyxl import load_workbook

#soap client
from suds.client import Client
from suds.xsd.doctor import *
reload(sys)


def lematization(lang, coment, ws_datatype, stopwords):
    ws_datatype.item = {'key': 'input_direct_data', 'value': coment}, \
    {'key': 'language', 'value': lang}
    # invocate ws
    result = FL_ws.service.runAndWaitFor(ws_datatype)
    # select output_url tag and store in tmp_file
    # saves in temporal file, else fails
    for item in result.item:
        if item.key == "output_url":
            rfile = item.value
            urllib.urlretrieve(rfile, "tmp_file")

    ret = []
    with open("tmp_file") as tmp_file:
        for line in tmp_file:
            if line.rstrip():
                (word, lema, tag, _, _, _) = line.split()  # unification
                if not re.match(r"^F.*", tag) and \
                not re.match(r"^Z.*", tag) and \
                not lema in stopwords:
                    ret.append(lema)
    file.close
    return ret


def encoding(st):
    st = re.sub(r"·", "á", st)
    st = re.sub(r"È", "é", st)
    st = re.sub(r"Ì", "í", st)
    st = re.sub(r"Û", "ó", st)
    st = re.sub(r"˙", "ú", st)
    st = re.sub(r"Ò", "ñ", st)
    st = re.sub(r"¸", "ü", st)
    return st


if __name__ == "__main__":

    # used structures
    stopwordsdic = {}
    mydicneg = {}
    mydicpos = {}
    positiveWords = {}
    negativeWords = {}

    # used vars
    xls_range = 'G22:H22'
    lang = "es"

    # creates a webserver with wsdl url
    wsdl_url = 'http://ws04.iula.upf.edu/soaplab2-axis/services/' \
    'morphosintactic_tagging.freeling_tagging?wsdl'
    FL_ws = Client(wsdl_url)
    # create ws
    ws_datatype = FL_ws.factory.create('ns3:Map')
    _comentarios = 'Comentarios_Peliculas.xlsx'
    try:
        wb = load_workbook(_comentarios)
    except IOError:
        print "File " + _comentarios + " not exists!"
        sys.exit(0)

    sheets = wb.get_sheet_names()
    sheet = wb.get_sheet_by_name(sheets[0])
    cell_range = sheet.range(xls_range)

    #loading stop words in dictionary(faster vs list)
    _stopwfile = 'stopwords.txt'
    try:
        with open(_stopwfile) as stopwords:
            for line in stopwords:
                if line.rstrip():
                    stopwordsdic[line.rstrip()] = 0

        stopwords.close
    except IOError:
        print "File " + stopwfile + " not exists!"
        sys.exit(0)

    # loading subjetive elements list in dictionary
    _listaElemfile = 'listasElementosSubjetivos.pl'
    try:
        with open(_listaElemfile) as elemList:
            for line in elemList:
                if line.rstrip():
                    m = re.match(r"elementoSubjetivo\('(.*)',(.*)\)+", line)
                    if m:
                        key = encoding(m.group(1))
                        if m.group(2) == '3':
                            positiveWords[key] = m.group(2)
                        else:
                            negativeWords[key] = m.group(2)
        elemList.close
    except IOError:
        print "File " + _listaElemfile + " not exists!"
        sys.exit(0)

    #reading the comment file
    for rows in cell_range:
        (valor, key) = rows
        if key.value < 3:
            insert = mydicneg
        else:
            insert = mydicpos
        #lematize and filter F words
        lista = lematization(lang, valor.value, ws_datatype, stopwordsdic)
        for words in lista:
            if not words in insert.keys():
                insert[words] = 0
            insert[words] = insert[words] + 1

    # ordering the lists (<)
    mydicneg = sorted(mydicneg.iteritems(), key=operator.itemgetter(1))
    mydicpos = sorted(mydicpos.iteritems(), key=operator.itemgetter(1))

    for words in mydicneg:
        (w, i) = words
        print w

    # print the last 100 elements
    #print mydicneg[-100:]
    #print mydicpos[-100:]
    mydicneg = [seq[0] for seq in mydicneg][-100:]
    mydicpos = [seq[0] for seq in mydicpos][-100:]

    # print 100 negative words
    for word in mydicneg:
        print word
    # print 100 positive words
    for word in mydicpos:
        print word
