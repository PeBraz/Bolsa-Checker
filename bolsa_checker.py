#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from gmail_client import GmailMyself
import collections
import urllib
import os
import datetime
import os.path
import sys

BOLSACHECKER_USER = "BOLSACHECKER_USER"
if  not os.environ.has_key(BOLSACHECKER_USER):
    print "Set email account first (e.g.:~ env {}=<your-email> python bolsa_checker.py)"\
            .format(BOLSACHECKER_USER)
    sys.exit()

def cache_page(func):
    BOLSAS_PAGE = "http://drh.tecnico.ulisboa.pt/bolseiros/recrutamento/"
    cache_filename = "drh_bolsas{}.html".\
                    format(datetime.date.today().isoformat())
 
    if not os.path.isfile(cache_filename):
        res = urllib.urlopen(BOLSAS_PAGE)
        page = res.read()
        with open(cache_filename, 'w') as f:
            f.write(page)
    else:
        with open(cache_filename) as f:
            page = f.read()

    #cleanup old file found
    for fname in os.listdir('.'):
        if fname != cache_filename and fname.startswith('drh_bolsas'):
            print "removing", fname
            os.unlink(fname)

    def _cache_page():
        return func(page)
    return _cache_page


@cache_page
def bolsa_checker(bolsa_page):

    tag_to_str = lambda s: (s.string or '').encode('utf-8', errors='ignore')

    header_fields = ["vagas", "tipo", "responsavel", "edital",\
                    "area", "abertura", "prazo"]
    Table = collections.namedtuple('Table', header_fields)

    soup = BeautifulSoup(bolsa_page, 'html.parser')
    article = soup.find('article')

    scholarships = []
    for row in article.find('tbody').find_all("tr"):
        items = map(tag_to_str, row.find_all('td'))
        scholarships.append(Table(*items))

    return scholarships

if __name__ == '__main__':

    targets = ["telecomunicações", "gestão", "informática"]
    #lower doesn't work with non ascii characters
    area_ss = lambda ss :  any(area in ss.area.lower() for area in targets)

    title = "[Bolsa Checker] Found a scholarship for you!!"

    my_mail = GmailMyself(os.environ[BOLSACHECKER_USER])

    scholarships = bolsa_checker()
    telecom_scholarships = filter(area_ss, scholarships) if scholarships else None


    if telecom_scholarships:
        body = "\n".join(["{} -> {}".format(ss.tipo, ss.area)\
                                        for ss in telecom_scholarships])
        my_mail.send(title, body)

