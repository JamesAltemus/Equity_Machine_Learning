# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 13:23:40 2020

@author: James Altemus
"""

import os
import requests

import pandas as pd
import unicodedata as utf

from time import time
from bs4 import BeautifulSoup
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class SEC_Filings:
    def __init__(self, CIK, archive, alt_name = None, form_types = 'all',
                 start_date = None, end_date = None, auto_download = 'parsed',
                 new_folder = True, auto_parse = False):
        '''
        CIK: The company's CIK number
        archive: Path to the directory containing all the SEC indicies. They can be downloaded at https://www.sec.gov/Archives/edgar/full-index/
        alt_name: An alternative name. Provides easier navigation of downlaoded folders
        
        form_types: Default 'all'. A list of filing types to scrape
        start_date: Default None. The oldest date to look at 'YYYY-MM-DD'
        end_date: Default None. The newest date to look at 'YYYY-MM-DD'
        
        auto_download: Default True (False, True, 'Parsed'). Automatically downloads the company filings into a folder instead of storing in memory. Parsed option, see auto_parse.
        new_folder: Default True. Creates a new folder for the automatic downloader
        
        auto_parse: Default False. Removes stopwords, stems words, and does other common text processing tasks
        '''
        self.CIK = self._format_cik(CIK)
        self.name = alt_name
        self.source_dir = os.getcwd()
        
        self._access_archive(archive, form_types, start_date, end_date, auto_download)
        
        if new_folder:
            self._make_directory()
            os.chdir(self.folder)
        
        self.get_filings(auto_download, auto_parse)
    
    
    def _format_cik(self, CIK):
        if len(CIK) == 10:
            while CIK.find('0') == 0:
                CIK = CIK[1:]
        return CIK
    
    
    def _make_directory(self):
        os.chdir(self.source_dir)
        if self.name:
            name = self.name + '_' + self.CIK
        else:
            name = self.CIK
        self.folder = name + '_SEC_Filings'
        try:
            os.mkdir(self.folder)
        except FileExistsError:
            pass
    
    
    def _access_archive(self, archive, form_types, start_date=None,
                        end_date=None, auto_download=False):
        os.chdir(archive)
        indicies = os.listdir()
        self.urls = []
        self.dates = []
        self.types = []
        
        print('Gathering Information...',end='')
        start = time()
        breaker = None
        chg_cik = True if form_types == 'all' else None
        for index in indicies:
            with open(index, 'r') as index:
                for line in index:
                    line = line.split('|')
                    if self.CIK == line[0]:
                        ft_test = False
                        sd_test = False
                        ed_test = False
                        f_type = line[2]
                        f_date = line[3]
                        if (form_types == 'all') or (f_type in form_types) or (f_type.lower() in form_types):
                            ft_test = True
                            if chg_cik:
                                if f_type == 'S-1':
                                    chg_cik = False
                                if f_type == 'DRS':
                                    chg_cik = False
                        if (start_date == None) or (f_date >= start_date):
                            sd_test = True
                        if (end_date == None) or (f_date <= end_date):
                            ed_test = True
                        if ft_test and sd_test and ed_test:
                            self.urls.append(line[4])
                            self.types.append(f_type)
                            self.dates.append(f_date)
                        breaker = 0
                    elif breaker == 0:
                        breaker = None
                        break
                    else:
                        pass
        end = time()
        print('\rGathering information took {0:.4f} seconds.\n'.format(end-start), end ='')
        os.chdir(self.source_dir)
        if chg_cik:
            print('\nWARNING: This company likely has an older cik number. Check their Form 8-K12B and EFFECT Forms.')
            if auto_download:
                with open('older_cik.txt', 'a+') as older:
                    older.write(self.name+','+self.CIK+'\n')
    
    
    def get_filings(self, auto_download, auto_parse):
        complete = len(self.urls)
        if self.name:
            print('\n' + self.name, 'has', complete, 'applicable filings.')
        else:
            print('\n' + self.CIK, 'has', complete, 'applicable filings.')
        
        print('\nProcessing Filing 0. Estimated time remaining: N/A:N/A...', end = '')
        def end_seq(i, complete, times):
            prediction = sum(times)/len(times) * (complete - i)
            secs = int(prediction % 60)
            mins = prediction // 60
            print('\rProcessing Filing {0}: {3} {4}. Estimated time remaining: {1:.0f}:{2:02d}...'.format(
                    i+1,mins,secs,self.types[i+1],self.dates[i+1]),end = '')
        
        
        times = []
        self.Filings = []
        for instance in range(complete):
            start = time()
            form = EDGAR_retriever(self.urls[instance], stem = False)
            if auto_download:
                if str(auto_download).lower() == 'parsed':
                    form.text = SEC_Parser(form.text).parsed
                f_type = self.types[instance]
                f_date = self.dates[instance]
                f_type = f_type.replace('/', '-')
                f_type = f_type.replace(' ', '--')
                
                save_name = self.folder + '_type_' + f_type + '_date_' + f_date
                form.download(save_name)
                self.Filings.append(save_name)
                end = time()
                times.append(end - start)
                if instance != complete-1:
                    end_seq(instance, complete, times)
            elif auto_parse:
                form.text = SEC_Parser(form.text).parsed
                self.Filings.append(form)
                end = time()
                times.append(end - start)
                if instance != complete-1:
                    end_seq(instance, complete, times)
            else:
                self.Filings.append(form)
                end = time()
                times.append(end - start)
                if instance != complete-1:
                    end_seq(instance, complete, times)
        print('All filings collected.')



class EDGAR_retriever:
    def __init__(self, url, stem = True, tables = True):
        if not stem:
            url = 'https://www.sec.gov/Archives/' + url
        self.text = requests.get(url).text.replace('<div', '<p')
        self.text = self.text.replace('</div', '</p')
        self.text = BeautifulSoup(self.text, 'lxml')
        self.text = self.text.find_all('document')[0]
        
        if tables:
            # separate fianncial tables
            raw_tables = self._extractor(self.text.findAll('table'))
            self.text = self._tabler(str(self.text), raw_tables)
            self.text = BeautifulSoup(self.text, 'lxml')
        
        self.text = self.text.get_text(separator = '\n')
        self.text = utf.normalize('NFKC', self.text)
    
    
    def download(self, file_name, download_selector = 'all',
                 text_ext = '.txt', table_ext = '.csv'):
        '''
        Saves the filing's text and tables given their extentions.
        
        file_name: the root name for the download
        download_selector: default 'all'. Accepts 'all','text', or 'table' and only downloads the selected type
        text_ext: default '.txt'. the extention to use for text download
        table_est: Currently tables can only be in .csv
        '''
        if download_selector.lower() == 'all' or download_selector.lower() == 'text':
            with open(file_name+text_ext, 'w+', encoding = 'utf-8') as file:
                file.write(self.text)
        if download_selector.lower() == 'all' or download_selector.lower() == 'table':
            table_ext = '.csv'
            for i in range(len(self.tables)):
                self.tables[i].to_csv(file_name+'_table'+str(i)+table_ext)
    
    
    def _tabler(self, doc, raw_tables):
        for i in range(len(raw_tables)):
            raw = str(raw_tables[i])
            doc = doc.replace(raw,'table'+str(i))
        return doc
    
    
    def _extractor(self, tables):
        raw = []
        self.tables = []
        def remove_lead_acct(text):
            text = str(text)
            pairs = [('(0', '-0'),('(1', '-1'),('(2', '-2'),('(3', '-3'),('(4', '-4'),
                     ('(5', '-5'),('(6', '-6'),('(7', '-7'),('(8', '-8'),('(9', '-9')]
            for pair in pairs:
                text = text.replace(pair[0],pair[1])
            return text
        
        def df_formatter(df, dtype = float, nan_threshold = 0.75):
            financial = False
            numeric = False
            # Due to SEC formatting, closing parenthesis in a separate column are common in financial tables.
            # These should be removed to ensure data quality
            df = df[0].replace(')',None)
            df = df.dropna(axis = 0, how = 'all')
            df = df.dropna(axis = 1, how = 'all')
            # Replace the none dash with 0
            df = df.replace('—',0)
            
            drop = []
            df = df.astype(str, errors='ignore')
            for col in df.columns:
                if df[col].str.find('$').dropna().product() == 0:
                    # Due to SEC formatting, financial tables end up having duplicate columns next to eachother 
                    # with some sign changes. This can be used to pick out only the fianncial tables due to this reduction.
                    financial = True
                    drop.append(col)
                for ele in df.index:
                    try:
                        # Additionally, financial tables should contain at least 1 number
                        df[col][ele] = dtype(df[col][ele])
                        numeric = True
                    except ValueError:
                        pass
            df = df.drop(drop, axis = 1)
            # Remove any remaining columns that are mostly empty
            df = df.dropna(axis = 1, thresh = int(len(df)*nan_threshold))
            return df, financial & numeric
        
        for tmp_table in tables:
            # It is easier to remove the leading accounting format now and the trailing later
            table = remove_lead_acct(str(tmp_table))
            try:
                table = pd.read_html(table)
                if table != []:
                    table, valid = df_formatter(table)
                    if valid:
                        # Since SEC formatting is relatively consistent, this should allow extraction of
                        # only tables with financial data per the notes in the df_formatter function
                        table = table.fillna('null')
                        table.index = table[table.columns[0]]
                        table = table.drop(table.columns[0], axis = 1)
                        first = table.loc[table.index[0]].astype(str, errors='ignore')
                        table.columns = first.sum() if len(first.shape) > 1 else first
                        table = table.drop(table.index[0])
                        self.tables.append(table)
                        raw.append(tmp_table)
            except ValueError:
                pass
        return raw



class SEC_Parser:
    def __init__(self, corpus, case = True, language = 'english',
                 rm_stopwords = True, rm_special = True, stem = True,
                 keep_paragraphs = True, keep_sentences = True):
        '''
        case: changes to lowercase
        rm_punctuation: removes all punctuation, and certain special characters
        
        language: used for stemming and stopwords
        rm_stopwords: removes all stopwords
        stem: stems words
        
        keep_paragraphs: keeps \n's in the corpus
        keep_sentences: keeps ". " in the corpus
        '''
        if case:
            corpus = corpus.lower()
        if rm_stopwords:
            stop_words = set(stopwords.words(language))
        if stem:
            snowball = SnowballStemmer(language)
        
        if rm_stopwords or rm_special:
            self._check_token()
            if keep_paragraphs:
                corpus = corpus.split('\n')
                new_corpus = []
                for para in corpus:
                    new_para = []
                    para = word_tokenize(para)
                    if keep_sentences:
                        while '.' in para:
                            i = para.index('.')
                            new_sent = []
                            for w in para[:i]:
                                if rm_stopwords and rm_special:
                                    if (w not in stop_words) and (w.replace('.','').isalnum()):
                                        if stem:
                                            new_sent.append(snowball.stem(w))
                                        else:
                                            new_sent.append(w)
                                elif rm_stopwords:
                                    if w not in stop_words:
                                        if stem:
                                            new_sent.append(snowball.stem(w))
                                        else:
                                            new_sent.append(w)
                                elif rm_special:
                                    if w.replace('.','').isalnum():
                                        if stem:
                                            new_sent.append(snowball.stem(w))
                                        else:
                                            new_sent.append(w)
                            new_para.append(' '.join(new_sent))
                            para = para[i+1:]
                    else:
                        if rm_stopwords and rm_special:
                            if (w not in stop_words) and (w.replace('.','').isalnum()):
                                if stem:
                                    new_para.append(snowball.stem(w))
                                else:
                                    new_para.append(w)
                        elif rm_stopwords:
                            if w not in stop_words:
                                if stem:
                                    new_para.append(snowball.stem(w))
                                else:
                                    new_para.append(w)
                        elif rm_special:
                            if w.replace('. ','').isalnum():
                                if stem:
                                    new_para.append(snowball.stem(w))
                                else:
                                    new_para.append(w)
                    
                    new_corpus.append('. '.join(new_para))
            elif keep_sentences:
                while '.' in corpus:
                    i = corpus.index('.')
                    new_sent = []
                    for w in corpus[:i]:
                        if rm_stopwords and rm_special:
                            if (w not in stop_words) and (w.replace('.','').isalnum()):
                                if stem:
                                    new_sent.append(snowball.stem(w))
                                else:
                                    new_sent.append(w)
                        elif rm_stopwords:
                            if w not in stop_words:
                                if stem:
                                    new_sent.append(snowball.stem(w))
                                else:
                                    new_sent.append(w)
                        elif rm_special:
                            if w.replace('.','').isalnum():
                                if stem:
                                    new_sent.append(snowball.stem(w))
                                else:
                                    new_sent.append(w)
                    new_corpus.append(' '.join(new_sent))
                    corpus = corpus[i+1:]
            else:
                if rm_stopwords and rm_special:
                    if (w not in stop_words) and (w.replace('.','').isalnum()):
                        if stem:
                            new_corpus.append(snowball.stem(w))
                        else:
                            new_corpus.append(w)
                elif rm_stopwords:
                    if w not in stop_words:
                        if stem:
                            new_corpus.append(snowball.stem(w))
                        else:
                            new_corpus.append(w)
                elif rm_special:
                    if w.replace('.','').isalnum():
                        if stem:
                            new_corpus.append(snowball.stem(w))
                        else:
                            new_corpus.append(w)
        new_corpus = [p for p in new_corpus if p]
        self.parsed = '\n'.join(new_corpus)
    
    
    def _check_token(self):
        try:
            word_tokenize('Hello. This sentence is for testing purposes.')
        except LookupError as e:
            print(e)
            print('This is required to continue. Would you like to download this now? y/n')
            ans = input()
            if ans.lower() == 'yes' or ans.lower() == 'y':
                import nltk
                nltk.download('punkt')
            else:
                raise LookupError(e)
