#!/usr/bin/env python
# coding: utf-8

import csv
import sys
import pandas as pd
import xlrd
import re
    
#Read in input data
data = pd.read_excel('literature_metabolites.xlsx', engine = 'openpyxl')
csv.field_size_limit(sys.maxsize)
        
#Create dictionary containing metabolite synonyms with traditional_iupac as key
reader = csv.DictReader(open('hmdb_metabolites.csv', "rt"))
synonym_dict = {} #initialize empty dictionary
    
for line in reader:
    if line['synonyms'] != None:
        clean_synonyms = [] #empty list to store fixed synonym names
        for xx in line['synonyms'].split("', '"):
            xx = xx.replace(" '", "")
            xx = xx.strip("'")
            xx = xx.strip("['")
            xx = xx.strip("]'")
            clean_synonyms.append(xx.lower())
        clean_synonyms.append(line['name'].lower())
        clean_synonyms.append(line['traditional_iupac'].lower())
        synonym_dict[line['traditional_iupac']] = clean_synonyms
    

#create object
with open('literature_metabolites_key.csv', 'wt') as f:
    writer = csv.writer(f)
    for metabolite in data['name_search']:
        for (k,v) in synonym_dict.items():
            if metabolite in v or metabolite == k:
                data = (k, metabolite)
                writer.writerow(data)
            

