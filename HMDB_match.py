#!/usr/bin/env python
# coding: utf-8

import unicodecsv as csv
import pandas as pd
import datatable as dt
import numpy as np
    
#Create dictionary containing metabolite synonyms with hmdb_name as key
reader = csv.DictReader(open('hmdb_metabolites.csv', "rb"))
syn_dict = {} #initialize empty dictionary
csv.field_size_limit(sys.maxsize)
    
for line in reader:
    if line['synonyms'] != None:
        clean_synonyms = [] #empty list to store fixed synonym names
        for xx in line['synonyms'].split("', '"):
            xx = xx.replace(" '", "")
            xx = xx.strip("'")
            xx = xx.strip("['")
            xx = xx.strip("]'")
            clean_synonyms.append(xx.lower())
        #if line['traditional_iupac'] == "":
            #print(line)
        lowercase_name = line['name'].strip('"').lower()
        clean_synonyms.append(lowercase_name)
        clean_synonyms.append(line['traditional_iupac'].strip('"').lower())
        if 'iupac_name' in line:
            clean_synonyms.append(line['iupac_name'].strip('"').lower())
        syn_dict[lowercase_name] = clean_synonyms #set hmdb_name value as key

#Reverse dictionary to have unique keys for same value
rev_syn_dict = {value: key for key in syn_dict for value in syn_dict[key]}

#Define metabolite search function
def metabolite_search(infile):
    
    #read in input data
    data = dt.fread('audrain_metabolites.csv').to_pandas()
    data_drop = data.drop_duplicates(subset=['name_search']) #get rid of duplicate names between studies for search
    
    #search for data in dictionary
    for metabolite in data_drop['name_search']:
        if metabolite in rev_syn_dict.keys():
            yield [metabolite, rev_syn_dict.get(metabolite)]
            

met_search = pd.DataFrame(list(metabolite_search('audrain_metabolites.csv')),
             columns=['name_search', 'name']) 

#Define metabolite matching function
def metabolite_match(infile, matchfile, umatchfile):
    
    #read in input data
    data = dt.fread(infile).to_pandas()
    db_metabolites = dt.fread('hmdb_metabolites.csv').to_pandas()
    
    #join input data with match data
    DF = data.merge(met_search, on = 'name_search', how = 'inner')
    
    #join match data with metabolite data
    db_match = db_metabolites.assign(name = lambda x: x.name.str.strip('"').str.lower()) #match search
    db_match = db_match.drop('synonyms', axis =1)
    
    all_match = DF.merge(db_match, on = 'name', how = 'inner')
    
    #write checkpoint information
    if len(DF) == len(all_match):
        print ("Match length checkpoint passed")
        
        #print match information
        print('Input search length:', len(data), ' Matched names found:', len(all_match), 'Unmatched:', len(data)-len(all_match))
        print('match rate:', round((len(all_match)/len(data))*100,2), '%')
        
        #write matched metabolites out to csv file
        all_match.to_csv(matchfile)
        print("Writing match data out to csv")
        
        #identify unmatched metabolites and write to csv
        unmatched_boo = ~data.name_search.isin(all_match.name_search)
        unmatched_met = pd.DataFrame(data[unmatched_boo])
        unmatched_met.to_csv(umatchfile)
        print("Writing unmatched data out to csv")
        
        #write matched vmh_id
        vmh = pd.DataFrame(all_match['vmh_id']).drop_duplicates()
        vmh.replace("", np.nan, inplace=True)
        vmh.dropna(inplace=True)
        vmh.to_csv('vmh_file.csv', index=False)
        
    else:
        print('Error: differing match length')
        
metabolite_match('audrain_metabolites.csv', 'matched_metabolites.csv', 'unmatched_metabolites.csv')

