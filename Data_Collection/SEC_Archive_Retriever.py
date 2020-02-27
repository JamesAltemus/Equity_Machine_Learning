# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 19:39:55 2020

@author: juliu
"""

from os import chdir, mkdir
from urllib.request import urlopen
from datetime.datetime import today

def build_archive():
    months = ['January','February','March','April','May','June','July',
              'August','September','October','Novemeber','December']
    if not os.path.exists('SEC_Archive'):
        mkdir('SEC_Archive')
    chdir('SEC_Archive')
    base = 'https://www.sec.gov/Archives/edgar/full-index/'
    for year in range(-7, today().year-1999):
        for quarter in range(1, 5):
            with urlopen(base+str(year+2000)+'/QTR'+str(quarter)+'/company.idx') as archive:
                namer = []
                i = 0
                for line in archive:
                    namer.append(line)
                    if i == 1:
                        date = str(line).lstrip("b'Last Data Received:").rstrip("\\n'")
                        mon = str(months.index(date[:date.find(' ')])+1)
                        day = date[date.find(' ')+1:date.find(',')]
                        year = date[date.find(', ')+2:]
                        quarter = '-'.join([year,mon,day])
                        break
                    i+=1
                with open('index_'+quarter+'.idx', 'a+', encoding = 'utf-8') as file:
                    for line in namer:
                        file.write(str(line).lstrip("b'").rstrip("\\n'")+'\n')
                with open('index_'+quarter+'.idx', 'a+', encoding = 'utf-8') as file:
                    for line in archive:
                        file.write(str(line).lstrip("b'").rstrip("\\n'")+'\n')
    chdir('../')