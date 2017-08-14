from bs4 import BeautifulSoup
import requests
import re
import urllib2
import os
import cookielib
import json
from PIL import Image
def get_soup(url,header):
    return BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)),'html.parser')


def download_images(query,num_images=2):
    image_type="image"
    query= query.split()
    querys='+'.join(query)
    url="https://www.google.com/search?q="+querys+"&source=lnms&safe=active&tbm=isch&tbs=isz:m"# &as_sitesearch=wikipedia.org ,iar:w iar-aspect ratio, isz-size, 
    query='_'.join(query)
    print url
    #add the directory for your image here
    DIR="./picture/tmp"
    header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }
    soup = get_soup(url,header)


    ActualImages=[]# contains the link for Large original images, type of  image
    for a in soup.find_all("div",{"class":"rg_meta"}):
        link , Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
        ActualImages.append((link,Type))
    ActualImages = ActualImages[:num_images]
    print  "there are total" , len(ActualImages),"images"

    if not os.path.exists(DIR):
        os.mkdir(DIR)
    DIR = os.path.join(DIR, query.split()[0])

    if not os.path.exists(DIR):
                os.mkdir(DIR)
    ###print images
    for i , (img , Type) in enumerate( ActualImages):
        try:
            req = urllib2.Request(img, headers={'User-Agent' : header})
            raw_img = urllib2.urlopen(req).read()

            cntr = len([i for i in os.listdir(DIR) if image_type in i]) + 1
            print cntr
            if len(Type)==0:
                f = open(os.path.join(DIR , image_type + "_"+ str(cntr)+".jpg"), 'wb')
            else :
                f = open(os.path.join(DIR , image_type + "_"+ str(cntr)+"."+Type), 'wb')


            f.write(raw_img)
            f.close()
        except Exception as e:
            print "could not load : "+img
            print e

    files = (fn for fn in os.listdir('./picture/tmp/'+query) if fn.endswith('.jpg') or fn.endswith('.png') or fn.endswith('.PNG') or fn.endswith('.JPG') or fn.endswith('.jpeg') or fn.endswith('.JPEG'))
    for f in files:
        im = Image.open('./picture/tmp/'+query+'/'+f)
        width, height = im.size
        if width < 300 or width > 1100:
            os.remove('./picture/tmp/'+query+'/'+f)
        if height < 200 or height > 800:
            os.remove('./picture/tmp/'+query+'/'+f)





# query = raw_input("QUERY: ")
# download_images(query)