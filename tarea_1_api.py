#! /usr/bin/python
# -*- coding: utf-8 -*-

#imports
import sys
import operator
import urllib
import re
import freeling
import numpy as np
import matplotlib.pyplot as plt
import codecs

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


def lematization_freeling(comment, tk, sp, mf, tg, sen, parser, stopwords):
    l = tk.tokenize(comment)
    ls = sp.split(l, 1)

    ls = mf.analyze(ls)
    ls = tg.analyze(ls)
    ls = sen.analyze(ls)
    ls = parser.analyze(ls)
    #ls = dep.analyze(ls);

    ## output results
    lista = []
    for s in ls:
        ws = s.get_words()
        for w in ws:
            tag = w.get_tag()
            lema = w.get_lemma()
            if not re.match(r"^F.*", tag) and \
            not re.match(r"^Z.*", tag) and \
            not lema in stopwords:
                lista.append(lema)
            #print(w.get_form() + " " + w.get_lemma() + " " + w.get_tag() + " ")
            ##+w.get_senses_string());
    return lista


def plot(negativeDic, n_groups):
    xvalues = [seq[0] for seq in negativeDic][:n_groups]
    values = [seq[1] for seq in negativeDic][:n_groups]
    n_groups = min(n_groups, len(xvalues))
    ysize = max(values)
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35

    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    plt.bar(index, values, bar_width, alpha=opacity, color='b', error_kw=error_config, label='Comentario')

    plt.xlabel('Comment')
    plt.ylabel('#Comments')
    plt.title('Top words')
    plt.xticks(index + bar_width / 2, xvalues)
    #index +bar_width
    plt.legend()
    ax.set_ylim(0, ysize + 3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    # used structures
    stopwordsdic = {}
    mydicneg = {}
    mydicpos = {}
    positiveWords = {}
    negativeWords = {}
    allWords = {}

    # configure Freeling
    FREELINGDIR = "/usr/local"
    DATA = FREELINGDIR + "/share/freeling/"
    LANG = "es"
    freeling.util_init_locale("default")
    # create language analyzer
    #la=freeling.lang_ident(DATA+"common/lang_ident/ident.dat");

    # create options set for maco analyzer. Default values are Ok,
    # except for data files.
    op = freeling.maco_options(LANG)
    #()
    # user_map, false
    # affix_analysis, false
    # multiple_words_detection, true
    # Numbers detection, true
    # punctuation_detection, true
    # dates_detection, false
    # quantities_detection, true
    # dictionary_search, true
    # probability_assignament, true
    # Ner_recongition false
    op.set_active_modules(0, 0, 1, 1, 1, 0, 1, 1, 1, 0)


    op.set_data_files("",
        DATA + LANG + "/locucions.dat", DATA + LANG + "/quantities.dat",
        DATA + LANG + "/afixos.dat", DATA + LANG + "/probabilitats.dat",
        DATA + LANG + "/dicc.src", DATA + LANG + "/np.dat",
        DATA + "common/punct.dat")

    # create analyzers
    tk = freeling.tokenizer(DATA + LANG + "/tokenizer.dat")
    sp = freeling.splitter(DATA + LANG + "/splitter.dat")
    mf = freeling.maco(op)

    tg = freeling.hmm_tagger(DATA + LANG + "/tagger.dat", 1, 2)
    sen = freeling.senses(DATA + LANG + "/senses.dat")

    parser = freeling.chart_parser(DATA + LANG + "/chunker/grammar-chunk.dat")
    #dep=freeling.dep_txala(DATA+LANG+"/dep/dependences.dat", parser.get_start_symbol());

    # used vars
    #xls_range = 'G22:H22'
    #xls_range = 'G875:H875'
    xls_range = 'B2:C8'
    lang = "es"

    # creates a webserver with wsdl url
    #wsdl_url = 'http://ws04.iula.upf.edu/soaplab2-axis/services/' \
    #'morphosintactic_tagging.freeling_tagging?wsdl'
    #FL_ws = Client(wsdl_url)
    # create ws
    #ws_datatype = FL_ws.factory.create('ns3:Map')

    #_comentarios = 'Comentarios_Peliculas.xlsx'
    _comentarios = 'test.xlsx'
    try:
        wb = load_workbook(_comentarios)
    except IOError:
        print ("File " + _comentarios + " not exists!")
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
        print("File " + stopwfile + " not exists!")
        sys.exit(0)

    # loading subjetive elements list in dictionary
    _listaElemfile = 'listasElementosSubjetivos.pl'
    try:
        with open(_listaElemfile) as elemList:
            for line in elemList:
                if line.rstrip():
                    m = re.match(r"elementoSubjetivo\('(.*)',(.*)\)+", line)
                    if m:
                        key = m.group(1) #encoding(m.group(1))
                        if m.group(2) == '3':
                            positiveWords[key] = m.group(2)
                        else:
                            negativeWords[key] = m.group(2)
        elemList.close
    except IOError:
        print("File " + _listaElemfile + " not exists!")
        sys.exit(0)


    # using freeling
    #reading the comment file
    for rows in cell_range:
        (valor, key) = rows
        if key.value < 3:
            insert = mydicneg
        else:
            insert = mydicpos
        #lematize and filter F words
        #lista = lematization(lang, valor.value, ws_datatype, stopwordsdic)
        lista = lematization_freeling(valor.value, tk, sp, mf, tg, sen, parser, stopwordsdic)
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
    mydicneg = sorted(mydicneg.iteritems(), key=operator.itemgetter(1), reverse=True)
    mydicpos = sorted(mydicpos.iteritems(), key=operator.itemgetter(1), reverse=True)
    allWords = sorted(allWords.iteritems(), key=operator.itemgetter(1), reverse=True)

    mydicnegList = [seq[0] for seq in mydicneg][:100]
    mydicposList = [seq[0] for seq in mydicpos][:100]
    allWordsList = [seq[0] for seq in allWords][:100]

    # intersection
    negInter = set(mydicnegList).intersection(negativeWords.keys())
    posInter = set(mydicposList).intersection(positiveWords.keys())

    #print negInter
    for w in mydicneg:
        print w

    print "positive Words"
    for w in mydicpos:
        print w
    # A (Dina suggest)
    plot(allWords, 10)

    # B (Dina suggest)
    #plot(mydicneg, 14)
    #plot(mydicpos, 14)


    #for word in negInter:
    #    print(word)
