#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from gmail_client import GmailMyself
import collections
import urllib
import re
import os
import datetime
import os.path

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
    remove_non_alpha = lambda s: re.sub('\W', '', s)
    

    soup = BeautifulSoup(bolsa_page, 'html.parser')
    article = soup.find('article')

    table_head = map(remove_non_alpha,\
                    map(tag_to_str,\
                        article.find('thead').find_all('th')))

    Table = collections.namedtuple('Table', table_head)

    scholarships = []
    for row in article.find('tbody').find_all("tr"):
        items = map(tag_to_str, row.find_all('td'))
        scholarships.append(Table(*items))

    return scholarships

if __name__ == '__main__':

    telecom_ss = lambda s : "telecomunicações" in s.reaProjeto.lower()

    user = "pbraz.93@gmail.com"
    title = "[Bolsa Checker] Found a scholarship for you!!"


    my_mail = GmailMyself(user)
    scholarships = bolsa_checker()
    telecom_scholarships = filter(telecom_ss, scholarships) if scholarships else None


    if telecom_scholarships:
        body = "\n".join(["{} -> {}".format(ss.Tipodebolsa, ss.reaProjeto)\
                                        for ss in telecom_scholarships])
        my_mail.send(title, body)

