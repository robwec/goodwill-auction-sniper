import requests
import os
import re
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from dateutil import parser, tz
import pytz
import math

print("===================")
print("==Goodwill Sniper==")
print("===================\n")

mytz = pytz.timezone('US/Eastern')
nowtime = datetime.now(tz=mytz)

##[][][]add a routine to test and refresh bearer

##load snipes and wait for schedule. Snipe 7 seconds in advance, but if multiple auctions end around the same time add intervals of 7 seconds per near-time auction.[][][]

def loadSnipes():
	##load times and convert into Eastern Time
	mydf = pd.read_csv('snipelist.csv', dtype='object').fillna('')
	mydf['End Time'] = mydf['End Time'].apply(lambda x: parser.parse(x, tzinfos={'PT': tz.gettz('US/Pacific')}).astimezone(tz=mytz))
	mydf = mydf[mydf['End Time'] > nowtime] #cut old auctions out.
	mydf = mydf.sort_values(by='End Time', ascending=True)
	return mydf

def fancyPrintTimeRemaining(mytimedelta):
	hours = mytimedelta.seconds // 3600
	minutes = (mytimedelta.seconds % 3600) // 60
	seconds = (mytimedelta.seconds % 60)
	daystr = (str(mytimedelta.days) + " day"+('s' if mytimedelta.days != 1 else '') + ' ') if mytimedelta.days > 0 else ''
	return  daystr + str(hours) + ' hours ' + str(minutes) + ' minutes ' + str(seconds) + ' seconds'

taxrate = 1.0975
profitfactor = 1.67
shipcost = 4.00

def calcMyBid(thisrow):
	mybid = round(float(thisrow['Item Value'])/profitfactor / taxrate - float(thisrow['Shipping']) - shipcost, 2)
	#print(mybid)
	mybid = round(math.ceil(mybid) + 0.77, 2)
	#print(mybid)
	return mybid

def printNextSnipe(mydf):
	if len(mydf) == 0:
		print("No snipes remaining.")
		return
	
	thisrow = mydf.iloc[0]
	print("Title:", thisrow['Title'])
	print("URL:", 'https://shopgoodwill.com/item/'+thisrow['ID'])
	print('End Time (EST):', thisrow['End Time'])
	print('Time Remaining:', fancyPrintTimeRemaining(thisrow['End Time'] - datetime.now(tz=mytz)))
	print('Item Value:', '$'+thisrow['Item Value'])
	print('Shipping:', '$'+thisrow['Shipping'])
	mybid = calcMyBid(thisrow)
	print('My Bid:', '$'+str(mybid))
	print('Max Total Price if Won:', '$'+str((round(float(mybid) + float(thisrow['Shipping'])*taxrate, 2))))
	print('')
	return

def sendSnipe(mybearer, itemid, mybidprice):
	headers = {
		'authority': 'buyerapi.shopgoodwill.com',
		'accept': 'application/json',
		'accept-language': 'en-US,en;q=0.6',
		'access-control-allow-credentials': 'true',
		'access-control-allow-origin': '*',
		'authorization': 'Bearer '+mybearer,
		'content-type': 'application/json',
		'dnt': '1',
		'origin': 'https://shopgoodwill.com',
		'sec-ch-ua': '"Brave";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Linux"',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-site',
		'sec-gpc': '1',
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
	}
	
	json_data = {
		'itemId': itemid,
		'quantity': 1,
		'sellerId': 2,
		'bidAmount': str(round(float(mybidprice), 2)), ##[][][]format dollars and cents without dollar sign, 2 sig figs
	}
	
	resp = requests.post('https://buyerapi.shopgoodwill.com/api/ItemBid/PlaceBid', headers=headers, json=json_data)
	return resp


try:
	mybearer = json.load(open('nobackup/bearer.json', 'r'))
except:
	mybearer = ""

if mybearer == '':
	raise Exception("need to refresh bearer token!")

mydf = loadSnipes()
if len(mydf.drop_duplicates('ID')) != len(mydf):
	raise Exception("fix item ID duplicates!!!!")

if len(mydf.drop_duplicates('End Time')) != len(mydf):
	print("inspect end time duplicates...")
	input('')

#print("total max bid + ship:")
#print(mydf["Shipping"].astype(float).sum() + mydf['My Bid'].astype(float).sum())
#print("")

#def main():
##load snipes, sleep until time is within 3-7 seconds of auction end, then snipe and mark as sniped.
print("Next Snipe:")
printNextSnipe(mydf)

seconds_in_advance_to_snipe = 7
while 1:
	if len(mydf) == 0:
		print("All snipes done. Quitting.")
		exit()
	
	remainingtime = mydf.iloc[0]['End Time'] - datetime.now(tz=mytz)
	if remainingtime.days == 0 and remainingtime.seconds <= seconds_in_advance_to_snipe:
		print("sniping next auction...")
		try:
			print("time of snipe", str(datetime.now()))
			mybid = calcMyBid(mydf.iloc[0])
			resp = sendSnipe(mybearer, mydf.iloc[0]['ID'], mybid)
			print("snipe success:")
			print(resp)
			print(resp.text)
		except Exception as e:
			print("snipe error!")
			print(e)
		
		mydf = mydf.iloc[1:]
		print("\nNext Snipe:")
		printNextSnipe(mydf)
	
	time.sleep(1)

