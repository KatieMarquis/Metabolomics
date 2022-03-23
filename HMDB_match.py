#!/usr/bin/env python3
# coding: utf-8

"""
Script to fix names using hmdb
"""

__author__ = "Scott Daniel / Katie Marquis"
__version__ = "0.1.0"
__license__ = "MIT"

from ast import If
import unicodecsv as csv
import pandas as pd
import datatable as dt
import numpy as np
import argparse
import sys

#Define metabolite search function
def metabolite_search(infile, rev_syn_dict):
    
    #read in input data
    data = dt.fread(infile).to_pandas()
    data_drop = data.drop_duplicates(subset=['name_search']) #get rid of duplicate names between studies for search
    
    #search for data in dictionary
    for metabolite in data_drop['name_search']:
        if metabolite in rev_syn_dict.keys():
            yield [metabolite, rev_syn_dict.get(metabolite)]

#Define metabolite matching function
def metabolite_match(infile, matchfile, umatchfile, met_search):
    
    #read in input data
    data = dt.fread(infile).to_pandas()
    db_metabolites = dt.fread(args.hmdb).to_pandas()
    
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
        if args.vmh:
            vmh = pd.DataFrame(all_match['vmh_id']).drop_duplicates()
            vmh.replace("", np.nan, inplace=True)
            vmh.dropna(inplace=True)
            vmh.to_csv('vmh_file.csv', index=False)
        
    else:
        print('Error: differing match length')

def main(args):
    #Create dictionary containing metabolite synonyms with hmdb_name as key
    reader = csv.DictReader(open(args.hmdb, "rb"))
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

    met_search = pd.DataFrame(list(metabolite_search(args.infile, rev_syn_dict)),
    columns=['name_search', 'name'])

    metabolite_match(args.infile, args.matched, args.unmatched, met_search)

if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Optional positional argument
    parser.add_argument("hmdb", help="HMDB database file in a csv format\
        produced by HDMB_convert.py", default='hmdb_metabolites.csv')

    # Required positional argument
    parser.add_argument("infile", help="List of metabolite names to be used as search queries\
        MUST have the column called [name_search]")

    # Optional argument flag which defaults to False
    parser.add_argument("--vmh", help="Boolean that tells the program to output a file with vmh ids",
    action="store_true", default=False)

    # Optional argument
    parser.add_argument("-m", "--matched", help="CSV file of names found in HMDB",
    action="store", default='matched_metabolites.csv')

    # Optional argument
    parser.add_argument("-u", "--unmatched", help="CSV file of names NOT found in HMDB",
    action="store", default='unmatched_metabolites.csv')

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)