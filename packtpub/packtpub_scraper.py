#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import mechanize
from bs4 import BeautifulSoup
import boto3
import os
import tempfile
import hashlib
 
 
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
 
def print_progress(val=False):
    print "----uploading---",val

aws_access_key_id = raw_input("aws_access_key_id ? \n")
aws_secret_access_key = raw_input("aws_secret_access_id ? \n")

possible_ebooks=[]
s3 = boto3.resource('s3',aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,)
bucket = s3.Bucket('dmd440')
for obj in bucket.objects.filter(Prefix='packtpub'):
    a = obj.key.replace('packtpub/','')
    if a:
        a=a.encode('utf-8')
        hashk = hashlib.md5(a).hexdigest()[:16] ## generating a unique 16 char long for each pdf title
        possible_ebooks.append(hashk)
 
br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Firefox')]
br.addheaders.append( ['Accept-Encoding','gzip'] )
br.open("https://www.packtpub.com")
br.select_form(nr=1)
br.form["email"] = 'harsh3547@gmail.com'
br.form["password"] = 'harsh_3547'
resp=br.submit()
print resp
 
### if cron job scraping then enter last part here
 
directory_name = tempfile.mkdtemp()
print directory_name
br.open("https://www.packtpub.com/account/my-ebooks")   
soup1 = BeautifulSoup(br.response().read(),"lxml")
i=0
for product in soup1.find_all('div',class_="product-line unseen"):
    nid=product['nid']
    if not product['nid']:continue
    title=product['title'].encode('utf-8').replace("[eBook]","").replace('[ebook]','').strip().replace(" ","_")+".pdf"
    #print title
    hashk = hashlib.md5(title).hexdigest()[:16]
    if hashk in possible_ebooks:continue
    print "---downloading---",title
    path_to_file = os.path.join(directory_name,title)
    br.retrieve("https://www.packtpub.com/ebook_download/"+nid+"/pdf",path_to_file)
    print "downloaded ",title
    bucket.upload_file(path_to_file,'packtpub/'+title,Callback=print_progress(title))
    if os.path.exists(path_to_file):
        os.remove(path_to_file)
    print "---deleted--",path_to_file
    print ""
os.removedirs(directory_name)
