# -*- coding: utf-8 -*-
#import urllib2
from bs4 import BeautifulSoup
import requests

def getEx(url):
	r = requests.get(url)
	data = r.text
	soup2 = BeautifulSoup(data, "lxml")
	for graph in soup2.find_all('p'):
		for link in graph.find_all('a'):
			if 'Buy:' in graph.text:
				return graph.text.split('Buy:')[1]

r = requests.get("http://masternodes.online/")
data = r.text
soup = BeautifulSoup(data, "lxml")
section = soup.find('table')
urls = []

rows = section.findAll('tr')[1:]
for row in rows:
	deets = row.findAll('td')[2:]
	coinList = []
	print deets[0].get_text()
	newurl = 'https://masternodes.online' + deets[0].find('a').get('href')
	print newurl
	print getEx(newurl)
	### GET GENESIS BLOCK ###
	print deets[1].get_text() # price
	# print deets[2].get_text() # change
	print deets[3].get_text() # volume
	print deets[4].get_text() # marketcap
	print deets[5].get_text() # ROI
	print deets[6].get_text() # Nodes
	print deets[7].get_text() # Req'd coins
	
#print urls









