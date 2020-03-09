# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 16:25:42 2020

@author: James Altemus
"""

import os

from time import time, sleep
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from SEC_Analyzer_Backend import progress, predict_time

saver = 'SEC_w2v.model'

def filing_loader(file_name, min_length = 3):
    '''
    file_name: the name of the txt file to load
    dictionary: default None. If dictonary evaluates to true then it embeds the words in the document by the dictionary
    embed_len: default 128. The length of the 'definition' in the dictionary if the word is not found in the dictionary
    force_length: default False. Accepts false or a tuple of (sentence length, document length)
    '''
    doc = []
    word_count = 0
    with open(file_name) as text:
        for line in text:
            if len(line) < min_length:
                continue
            
            line = line.replace('\n','')
            line = word_tokenize(line)
            while '.' in line:
                ed = line.index('.')
                new = line[0:ed]
                word_count += len(new)
                doc.append(new)
                line = line[ed+1:]
            word_count += len(line)
            doc.append(line)
    sent_count = len(doc)
    return doc, word_count, sent_count


# Create sample for testing
os.chdir('SEC_Filings')
companies = os.listdir()
encoding_sample_size = len(companies)
os.chdir('../')

times = []
done = 0
stopper = 0
for company in companies:
    bg = time()
    os.chdir(os.path.join('SEC_Filings', company))
    print('Analyzing {}...'.format(company))
    filings = os.listdir()
    filings.remove('Tables')
    complete = len(filings)
    done2 = 0
    for filing in filings:
        document, word_count, sentence_count = filing_loader(filing)
        if stopper == 0:
            model = Word2Vec(document, sg = 1, iter = 2, size = 128, window = 5,
                             min_count = 6, workers = 6)
            stopper += 1
            sleep(0.1)
        else:
            model.train(document, total_examples = sentence_count,
                        total_words = word_count, epochs = 2)
        done2 += 1
        progress(done2, complete)
    
    # Save checkpoint
    os.chdir('../')
    os.chdir('../')
    model.save(saver)
    model.wv.save('vocabulary.kv')
    
    # Predict time remaining
    ed = time()
    done += 1
    elasped = (ed - bg)/60
    times.append(elasped)
    estimate = predict_time(times, encoding_sample_size, done)
    print('\r' + 'Company {2} took {0:.2f} minutes. Estimated time remaining {1:.2f} minutes'.format(
            elasped, estimate, done),'                                            ', end = '\n')
