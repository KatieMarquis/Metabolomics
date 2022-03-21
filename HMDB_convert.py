#!/usr/bin/env python
# coding: utf-8

import unicodecsv as csv
from io import BytesIO
from lxml import etree as ET
from functools import reduce

with open('/Users/danielsg/hmdb_metabolites.xml', 'r') as xml:
    tree = ET.parse(xml)
root = tree.getroot()
context = tree.iter(tag='{http://www.hmdb.ca}metabolite')
    
#open a file for writing
csvfile = open('hmdb_metabolites.csv', 'wb')
fieldnames = ['accession', 'name', 'iupac_name', 'traditional_iupac', 'smiles', 'inchi', 'inchikey', 'kegg_id', 'pubchem_id', 'vmh_id', 'synonyms', 'pathway_name' ,'smpdb_ID', 'kegg_map_id'] #create column names for csv file
    
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
        elif child.tag == "{http://www.hmdb.ca}iupac_name":
            iupac_name = child.text
        elif child.tag == "{http://www.hmdb.ca}traditional_iupac":
            traditional_iupac = child.text
        elif child.tag == "{http://www.hmdb.ca}smiles":
            smiles = child.text
        elif child.tag == "{http://www.hmdb.ca}inchi":
            inchi = child.text
        elif child.tag == "{http://www.hmdb.ca}inchikey":
            inchikey = child.text
        elif child.tag == "{http://www.hmdb.ca}kegg_id":
            kegg_id = child.text
        elif child.tag == "{http://www.hmdb.ca}pubchem_compound_id":
            pubchem_id = child.text
        elif child.tag == "{http://www.hmdb.ca}vmh_id":
            vmh_id = child.text
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
    writer.writerow({'accession':accession, 'name':name, 'iupac_name':iupac_name, 'traditional_iupac':traditional_iupac, 'smiles':smiles, 'inchi':inchi, 'inchikey':inchikey,'kegg_id':kegg_id, 'pubchem_id':pubchem_id, 'vmh_id':vmh_id, 'synonyms':all_synonyms, 'pathway_name':pathway_name ,'smpdb_ID':smpdb_id, 'kegg_map_id':kegg_map_id})
    elem.clear()

db_metabolites = dt.fread('hmdb_metabolites.csv').to_pandas()
print("Metabolite database length: ", len(db_metabolites))
