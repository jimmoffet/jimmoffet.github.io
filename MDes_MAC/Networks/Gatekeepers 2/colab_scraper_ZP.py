from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib
import urllib.parse
from collections import deque
import re
import sys
import pandas as pd

df_urls = pd.DataFrame()
df_urls = pd.read_table('processing_A.csv', sep=',')
df_test = df_urls.head(n=100)


for index, row in df_test.iterrows():
    url = (row['Links'])
    emails = set()
    # extract base url to resolve relative links
    parts = urllib.parse.urlsplit(url)
    base_url = "{0.scheme}://{0.netloc}".format(parts)
    path = url[:url.rfind('/')+1] if '/' in parts.path else url

    # path is full path... http://...

    #get url's content
    #print("Processing %s" % url)
    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        # ignore pages with errors
        continue

    # extract all email addresses and add them into the resulting set
    new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
    emails.update(new_emails)

    # create a beautiful soup for the html document
    soup = BeautifulSoup(response.text, 'html.parser')

    # find and process all the anchors in the document
    for anchor in soup.find_all("a"):
        # extract link url from the anchor
        link = anchor.attrs["href"] if "href" in anchor.attrs else ''
        # resolve relative links
        if link.startswith('mailto'):
            emails.update(link)
            break
        elif link.startswith('/'):
            link = base_url + link
        elif not link.startswith(url):
            break
        # add the new url to the queue if it was not enqueued nor processed yet
        #if not link in new_urls and not link in processed_urls:
            #new_urls.append(link)
    new_emailsStr = str(new_emails)
    df_test.set_value(index, 'Contact Email', new_emailsStr)
    df_test.to_csv('EXPORT.csv')
    #df_test.set_value(index, 'MAILTOS', mailtos)   
    #print new_urls

    '''
    #TRY AGAIN WITH INNER CONTACT LINK
    if emails==set():
        for elem in soup(text=re.compile(r'Contact')):
            parent = (elem.parent)
            url = parent.get('href')
            # extract base url to resolve relative links
            parts = urllib.parse.urlsplit(url)
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url

            try:
                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                # ignore pages with errors
                continue

            # extract all email addresses and add them into the resulting set
            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
            emails.update(new_emails)

            # create a beautiful soup for the html document
            soup = BeautifulSoup(response.text, 'html.parser')

            # find and process all the anchors in the document
            for anchor in soup.find_all("a"):
                # extract link url from the anchor
                link = anchor.attrs["href"] if "href" in anchor.attrs else ''
                # resolve relative links
                if link.startswith('mailto'):
                    emails.update(link)
                    break
                elif link.startswith('/'):
                    link = base_url + link
                elif not link.startswith(url):
                    break
                # add the new url to the queue if it was not enqueued nor processed yet
                #if not link in new_urls and not link in processed_urls:
                    #new_urls.append(link)
            new_emailsStr = str(new_emails)
            df_test.set_value(index, 'Contact Email', new_emailsStr)
            #df_test.set_value(index, 'MAILTOS', mailtos)   
            #print new_urls
            df_test.to_csv('EXPORT.csv')
    '''

df_test.to_csv('EXPORT.csv')
#df_test