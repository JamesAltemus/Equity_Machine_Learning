# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 16:25:42 2020

@author: James Altemus
"""

import os

from time import time, sleep
from gensim.models import Word2Vec
from SEC_Analyzer_Backend import filing_loader, progress, predict_time

save_dir = 'Directory to store the saved model in'
sec_dir = 'directory where SEC filings are'
saver = 'SEC_w2v.model'

# Create sample for testing
os.chdir(sec_dir)
companies = os.listdir()
encoding_sample_size = len(companies)
os.chdir(save_dir)

times = []
done = 0
stopper = 0
for company in companies:
    bg = time()
    os.chdir(os.path.join(sec_dir, company))
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
    os.chdir(save_dir)
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
