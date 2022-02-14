#!/usr/bin/env python
# coding: utf-8

# In[2]:


import unicodecsv as csv
from io import BytesIO
from lxml import etree as ET
from functools import reduce

#The input file 'hmdb_metabolites.xml' is downloaded directly from http://www.hmdb.ca/downloads and contains data on all of the metabolites.

with open('hmdb_metabolites.xml', 'r') as xml:
    tree = ET.parse(xml)
root = tree.getroot()
context = tree.iter(tag='{http://www.hmdb.ca}metabolite')
  
#open a file for writing
csvfile = open('hmdb_metabolites.csv', 'wb')
fieldnames = ['accession', 'name', 'traditional_iupac', 'synonyms', 'smiles', 'inchi', 'inchikey', 'pathway_name' ,'smpdb_ID', 'kegg_map_id'] #create column names for csv file

#create the csv file writer object in dictionary format
writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
writer.writeheader()

#create object
for elem in context:
    for child in elem:
        if child.tag == "{http://www.hmdb.ca}accession":
            accession = child.text
        elif child.tag == "{http://www.hmdb.ca}name":
            name = child.text
        elif child.tag == "{http://www.hmdb.ca}traditional_iupac":
            traditional_iupac = child.text
        elif child.tag == "{http://www.hmdb.ca}smiles":
            smiles = child.text
        elif child.tag == "{http://www.hmdb.ca}inchi":
            inchi = child.text
        elif child.tag == "{http://www.hmdb.ca}inchikey":
            inchikey = child.text
        elif child.tag == "{http://www.hmdb.ca}synonyms":
            all_synonyms = [grandchild.text for grandchild in child]
        elif child.tag == "{http://www.hmdb.ca}biological_properties":
            pathway_name = []
            smpdb_id = []
            kegg_map_id = []
            for pathway in child.findall(".//{http://www.hmdb.ca}pathway"):
                for subchild in pathway:
                    if subchild.tag == "{http://www.hmdb.ca}name":
                        pathway_name.append(subchild.text)
                    elif subchild.tag == "{http://www.hmdb.ca}smpdb_id":
                        smpdb_id.append(subchild.text)
                    elif subchild.tag == "{http://www.hmdb.ca}kegg_map_id":
                        kegg_map_id.append(subchild.text)
    
    #write all to file
    writer.writerow({'accession': accession, 'name': name, 'traditional_iupac' : traditional_iupac, 'synonyms' : all_synonyms, 'smiles': smiles, 'inchi': inchi, 'inchikey': inchikey, 'pathway_name' : pathway_name ,'smpdb_ID' : smpdb_id, 'kegg_map_id' : kegg_map_id})
    elem.clear()


# In[15]:


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
with open('lit_metabolites_key.csv', 'wt') as f:
    writer = csv.writer(f)
    for metabolite in data['name_search']:
        for (k,v) in synonym_dict.items():
            if metabolite in v or metabolite == k:
                data = (k, metabolite)
                writer.writerow(data)
            

