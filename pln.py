#! /usr/bin/python
# -*- coding: UTF-8 -*-

###########################################################
# example_call_FreeLing_WS.py
#   call FreeLing ws to annotate sentences given in stdin
#
# usage:
#  ./example_call_FreeLing_WS.py language < sentences
#
# WARNING: requieres Suds 0.4. Does not work with previous versions!!
#  suds website: https://fedorahosted.org/suds/
###########################################################

import urllib

 #soap client
from suds.client import Client
from suds.xsd.doctor import *


# import logging
# from optparse import OptionParser

# set stdout to utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# main
if __name__ == "__main__":

    # setting language
    lang = "es"

    # creates a webserver with wsdl url
    wsdl_url = 'http://ws04.iula.upf.edu/soaplab2-axis/services/morphosintactic_tagging.freeling_tagging?wsdl'
    FL_ws = Client(wsdl_url)

    print "Service loaded..."

    # to know the specifications of the webservice:
    #print FL_ws.service.getInputSpec()

    # create input map
    input = FL_ws.factory.create('ns3:Map')

    # input contains the sentences to annotate (stdin) and the language
    input.item = {'key':'input_direct_data','value':sys.stdin.read()}, {'key':'language','value':lang}
    print input

    ## analyse sentences
    result=FL_ws.service.runAndWaitFor(input)

    ## print obtained analysis
    print "--Resultados ----"

    # reading reference_data (read output from url):
    # select output_url tag and store in tmp_file
    for item in result.item:
        if item.key == "output_url":
            rfile = item.value
            urllib.urlretrieve(rfile, "tmp_file")

    # print lines in file
    with open("tmp_file") as file:
        for line in file:
            if line.rstrip():
                print line

    file.close

    # creates hash with key=word, indexing lema and tag
    dic = {}
    with open("tmp_file") as file:
        for line in file:
            if line.rstrip():
                (word, lema, tag, _, _, _) = line.split()  # unification
                dic[word] = (lema, tag)

    #print dic
    file.close

    # print items in dic
    for a, b in dic.iteritems():
        print b[0]
        print b[1]
