from lxml import html, etree
import requests
import re
import os
import sys
import csv
import argparse
import json
from exceptions import ValueError

def parse():

	headers = {	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
				'accept-encoding': 'gzip, deflate, sdch, br',
				'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
				'referer': 'https://www.glassdoor.com/',
				'upgrade-insecure-requests': '1',
				'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
				'Cache-Control': 'no-cache',
				'Connection': 'keep-alive'
	}

	location_headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.01',
		'accept-encoding': 'gzip, deflate, sdch, br',
		'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
		'referer': 'https://www.google.com/',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
		'Cache-Control': 'no-cache',
		'Connection': 'keep-alive'
	}
	# data = {"term": place,
	# 		"maxLocationsToReturn": 10}

	location_url = "https://masternodes.online/"

	try:
		# Getting location id for search location
		# print "Fetching location details"
		# location_response = requests.post(location_url, headers=location_headers).json()
		# place_id = location_response[0]['locationId']
		# print place_id
		job_listing_url = 'https://masternodes.online/'
		# Form data to get job results
		# data = {
		# 	'clickSource': 'searchBtn',
		# 	'sc.keyword': keyword,
		# 	'locT': 'C',
		# 	'locId': place_id,
		# 	'jobType': 'fulltime',
		# 	'radius': '5',
		# 	'fromAge': time
		# }
		# data = {
		# 	'clickSource': 'searchBtn',
		# 	'sc.keyword': keyword,
		# 	'locT':C,
		# 	'locId': place_id,
		# 	'jobType':'',
		# 	'fromAge': '2'
		# }

		

		job_listings = []

		next_url = job_listing_url
		previous_url = ''

		# cnt2 = 0
		# if place_id:
		# 	cnt = 0
		# 	while previous_url != next_url and cnt < 10:
		# 		print "count is ",cnt
		# 		#print "previous_url is ",previous_url
		# 		#print "next url is ",next_url
		# 		cnt += 1


		response = requests.post(job_listing_url, headers=headers)
		print response


		# extracting data from
		# https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=true&clickSource=searchBtn&typedKeyword=andr&sc.keyword=android+developer&locT=C&locId=1146821&jobType=
		parser = html.fromstring(response.text)
		# Making absolute url 
		base_url = "https://masternodes.online/"
		parser.make_links_absolute(base_url)

		XPATH_ALL_JOB = '//*[@id="masternodes_table"]/tbody/tr[1]/td[3]/strong/a/@href'
		# XPATH_NAME = './/a/text()'
		# XPATH_JOB_URL = './/a/@href'
		# XPATH_LOC = './/span[@class="subtle loc"]/text()'
		# XPATH_COMPANY = './/div[@class="flexbox empLoc"]/div/text()'
		# XPATH_SALARY = './/*[@class="green small"]/text()'
		# #XPATH_NEXT = '//*[@class="pagingControls cell middle"]/ul/li[7]/a/@href'
		# XPATH_NEXT = '//*[@id="FooterPageNav"]/div/ul/li[@class="next"]/a/@href'
		# #XPATH_NEXT = '//*[@id="FooterPageNav"]/div/ul/li[7]/a/@href'
		# XPATH_AGE = '//*[@id="MainCol"]/div/ul/li[11]/div[2]/div[3]/div[2]/span[1]/span/text()'

		# previous_url = next_url

		listings = parser.xpath(XPATH_ALL_JOB)
		print listings

		#print "Next url is: ", parser.xpath(XPATH_NEXT)[0]

		# try:
		# 	next_url = parser.xpath(XPATH_NEXT)[0]
		# 	#print "url successfully changed to ", next_url
		# 	#print "previous url is ", previous_url
		# except:
		# 	print "trying next url failed"

				

		# 		for job in listings:
		# 			cnt2 += 1
		# 			raw_job_name = job.xpath(XPATH_NAME)
		# 			#print raw_job_name
		# 			raw_job_url = job.xpath(XPATH_JOB_URL)
		# 			raw_lob_loc = job.xpath(XPATH_LOC)
		# 			raw_company = job.xpath(XPATH_COMPANY)
		# 			raw_salary = job.xpath(XPATH_SALARY)
		# 			#print raw_salary
		# 			raw_age = job.xpath(XPATH_AGE)

		# 			# Cleaning data
		# 			job_name = ''.join(raw_job_name).encode("ascii","ignore") if raw_job_name else None
		# 			job_location = ''.join(raw_lob_loc) if raw_lob_loc else None
		# 			raw_state = re.findall(",\s?(.*)\s?", job_location)
		# 			state = ''.join(raw_state).strip()
		# 			raw_city = job_location.replace(state, '')
		# 			city = raw_city.replace(',', '').strip()
		# 			company = ''.join(raw_company).encode("ascii","ignore").strip()
		# 			salary = ''.join(raw_salary).strip()

		# 			nope = [
		# 			'lyft',
		# 			'executive',
		# 			'legal',
		# 			'construction',
		# 			'audit',
		# 			'research',
		# 			'bilingual',
		# 			'sales',
		# 			'director',
		# 			'engineer',
		# 			'licensed',
		# 			'regional',
		# 			'patient',
		# 			'nurse',
		# 			'medical affairs',
		# 			'clinical',
		# 			'billing',
		# 			'3d',
		# 			'ux',
		# 			'interior',
		# 			'brokerage',
		# 			'motion graphics',
		# 			'architect',
		# 			'industrial designer'
		# 			]

		# 			if any(word in job_name.lower() for word in nope):
		# 				continue

		# 			if salary:
		# 				# Check starting salary
		# 				check = salary.split('-')[0]
		# 				#print "check is ",check
		# 				check = check.strip('$')
		# 				#print "check is ",check
		# 				check = check.strip('k')
		# 				#print "check is ",check
		# 				check = int(check)
		# 				#print "check is ",check
		# 				if check < 29:
		# 					#print "check is less than 25"
		# 					#print "skipping job that starts at ",check
		# 					continue
		# 				if check > 39:
		# 					#print "check is less than 25"
		# 					#print "skipping job that starts at ",check
		# 					continue

		# 			#print "salary is {}".format(salary)
		# 			job_url = raw_job_url[0] if raw_job_url else None
		# 			age = ''.join(raw_age).encode("ascii","ignore").strip() 

		# 			jobs = {
		# 				"ID": cnt2,
		# 				"Name": job_name,
		# 				"Company": company,
		# 				"State": state,
		# 				"City": city,
		# 				"Age": age,
		# 				"Salary": salary,
		# 				"Location": job_location,
		# 				"Url": job_url
		# 			}
		# 			job_listings.append(jobs)



		# 	return job_listings
		# else:
		# 	print "location id not available"

	except:
		print "Failed to load locations"

parse()