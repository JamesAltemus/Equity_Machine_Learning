# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 14:18:20 2020

@author: James Altemus
"""

import os
import csv
import SEC_Downloader_Classes as sec

from time import sleep


store_in = ''
index_archive = ''
num_parallel = 6

def download(tiks, ciks, p, indicies, types):
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
            sec.SEC_Filings(cik, alt_nm=tik, archive = indicies, types)
            os.chdir(d)
            with open('sucess.txt', 'a+') as failed:
                failed.write(tik+','+cik+'\n')
        except Exception as e:
            os.chdir(d)
            print(e)
            with open('failed.txt', 'a+') as failed:
                failed.write(tik+','+cik+','+str(e)+'\n')
            print('Error infomration saved to failed.txt.\n')
        sleep(2)
        download(tiks, ciks, p-1, indicies, types)
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

os.chdir(store_in)
download(tiks, ciks, len(tiks)/num_parallel, index_archive, form_types = ['10-K','10-Q','8-K','S-1','DRS'])
