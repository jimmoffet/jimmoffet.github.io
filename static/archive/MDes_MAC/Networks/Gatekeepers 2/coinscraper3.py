from __future__ import print_function
import requests
import requests.exceptions
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
from pprint import pprint
import time
import csv
import os.path
from copy import deepcopy

userhome = os.path.expanduser('~')
#stamp = int(time.time()) # current unix time in seconds
now = 1511454297 # time.time keeps changing...

def getCoinIds():
    # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    u = 'http://www.cryptocompare.com/api/data/coinlist/'
    r = requests.get(u)
    #print r
    resp = r.json()

    coinids = {}
    data = resp['Data']
    for key, value in data.items():
        #print key, data[key]['Id']
        coinids[key] = data[key]['Id'] # dictionary looks like {'BTC' : '1182', 'ETH' : '7605', etc... }
    info = coinids

    with open('coinids.json', 'w') as outfile:
        json.dump(coinids, outfile)

    return 'success'

def getHistoPrice(path):
    # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    data = json.load(open(path))
    month = int(60*60*24*(((365*4)+1)/48)) # number of seconds in a month
    
    for i in range(0,96):
        timestamp = str(now - (month * i))

        print('i is '+str(i))

        cnt = 0
        for key, value in data.items():
            coinid = key
            try:            
                u = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=' + coinid + '&tsyms=BTC,USD,EUR&ts='+timestamp
                r = requests.get(u)
                resp = r.json()
                tempList = [timestamp, coinid]
                for k,v in resp.items():
                    for k,v in v.items():
                        tempList.append(format(v,'.16f'))

                with open('monthly.csv', 'a') as myFile: 
                    writer = csv.writer(myFile)
                    writer.writerow(tempList)

            except:
                with open('monthly.csv', 'a') as myFile: 
                    writer = csv.writer(myFile)
                    writer.writerow([timestamp,coinid,'FAIL','FAIL','FAIL'])
                    print('fail')
                    print(resp)

            myFile.close()

            #time.sleep(0.5)
            cnt+=1
            if cnt % 13 == 0:
                print('processing currency {} of 2000 for {} months ago'.format(cnt,i))
                print('time: {}'.format(int(time.time())))
            
    return 'success'

path = 'coinids.json'
getHistoPrice(path)
print('done')



