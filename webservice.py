# -*- coding: utf-8 -*-
from suds.client import Client
from suds.xsd.doctor import *
import urllib


class WebService:
    __lang = "es"
    # creates a webserver with wsdl url
    __wsdl_url = 'http://ws04.iula.upf.edu/soaplab2-axis/services/' \
    'morphosintactic_tagging.freeling_tagging?wsdl'
    __FL_ws = Client(__wsdl_url)
    # create ws
    __ws_datatype = __FL_ws.factory.create('ns3:Map')

    def __init__(self):
        pass

    def lematization_freeling_ws(self, comment, stopwords):
        self.__ws_datatype.item = {'key': 'input_direct_data',
            'value': comment}, {'key': 'language', 'value': self.__lang}
        # invocate ws
        result = self.__FL_ws.service.runAndWaitFor(self.__ws_datatype)
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
                        #lema = parse(lema)
                        lema = unicode(lema, "UTF-8")
                        ret.append(lema)
        file.close
        return ret
