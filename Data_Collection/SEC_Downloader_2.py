# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 14:18:20 2020

@author: James Altemus
"""

import os
import csv

import SEC_Archive_Retriever as arc
import SEC_Downloader_Classes as sec

from time import sleep

num_parallel = 1
filings = ['10-K','10-Q','8-K','S-1','DRS','10-K/A','10-Q/A','8-K/A','S-1/A','DRS/A']

def download(tiks, ciks, p, types):
    if p == -1 or len(tiks) == 0:
        print ()
    else:
        d = os.getcwd()
        
        files = os.listdir()
        
        for f in files:
            f = f.split('_')[0]
            try:
                ind = tiks.index(f)
                tiks.pop(ind)
                ciks.pop(ind)
            except:
                pass
        
        tik = tiks[0]
        cik = ciks[0]
        if len(cik) < 10:
            x = 10 - len(cik)
            x = '0'*x
            cik = x + cik
        
        print('Ticker:', tik, ', CIK:', cik, ', Number Remaining:', p)
        
        try:
            sec.SEC_Filings(cik, alt_name=tik, form_types = types)
            with open('sucess.txt', 'a+') as failed:
                failed.write(tik+','+cik+'\n')
        except Exception as e:
            os.chdir(d)
            print('\n'+e)
            with open('failed.txt', 'a+') as failed:
                failed.write(tik+','+cik+','+str(e)+'\n')
            print('Error infomration saved to failed.txt.\n')
        sleep(2)
        download(tiks, ciks, p-1, types)
        print (tik + ":" + cik)


tiks = []
ciks = []
with open('company_info.csv', 'r') as file:
    file = csv.reader(file)
    i = 0
    for line in file:
        if i == 0:
            i+=1
            continue
        tiks.append(line[0])
        ciks.append(line[1])

if not os.path.exists('SEC_Filings'):
    os.mkdir('SEC_Filings')
os.chdir('SEC_Filings')

arc.build_archive()
download(tiks, ciks, len(tiks)/num_parallel, filings)
