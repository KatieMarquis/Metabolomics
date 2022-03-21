#!/usr/bin/env python
# coding: utf-8

import zipfile
import requests
import os

#Define functions to download HMDB database
def download_file(url,filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)

def unzip_and_delete(filename):
    xml_data = zipfile.ZipFile(filename,'r')
    xml_data.extractall()
    xml_data.close()
    os.remove(filename)

download_file('https://hmdb.ca/system/downloads/current/hmdb_metabolites.zip', 'hmdb_metabolites.zip')
unzip_and_delete('hmdb_metabolites.zip')
