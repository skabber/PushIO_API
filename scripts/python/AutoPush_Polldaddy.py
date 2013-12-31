#!/usr/bin/env python
# encoding: utf-8
"""
AutoPush_Polldaddy.py

This script makes it easy send push notifications via Push IO when a new Polldaddy.com poll is created.
You can run this script from cron, in order to automate the process. 

Copyright (c) 2012 Push IO LLC. All rights reserved.
"""

# Your Polldaddy API Key
POLLDADDY_API_KEY = ""

# Find these values on the Set Up > API page from your Push IO dashboard.
PUSHIO_APP_ID = ""
PUSHIO_SERVICE_SECRET = ""

# The segment of your users you want to target.
# Corresponds to a category registration.
PUSHIO_CATEGORY = ""

# A file where we persist q unique ID to track if a notification has already been sent
PICKLE_FILENAME = "AutoPush_Polldaddy.pkl"

import sys
import os
import urllib
import json
import pickle
from pushio import pushio

class PushioPolldaddy:

	def __init__(self):
	
		pushioAPI = pushio.API(PUSHIO_APP_ID, PUSHIO_SERVICE_SECRET, debug=True)
	
		try:
			self.pdUserCode = self.getPDUserCode()
		except:
			print "Failed to get Polldaddy API usercode"
		else:
			if self.pdUserCode:
				polls = self.getPDPolls()
				for poll in polls:
					if poll.has_key("id"):
						pollID = poll["id"]
					if poll.has_key("content"):
						pollContent = poll["content"]
					if poll.has_key("closed"):
						pollClosed = poll["closed"]

					if pollID and pollContent:
						if pollClosed == 0:
							if (hasAlertBeenSent(pollID)):
								print "Push notification has already been sent: %s\n" %(pollID)
								continue
							else:

								message = "New Poll: %s" %(pollContent)
								pollUrl = "www.polldaddy.com/polls/%s" %(pollID)
								extraDict = { "u" : pollUrl }
								
								apns = pushio.APNS(extra=extraDict)
								notification = pushio.Notification(message=message, payload_apns=apns.payload)
								
								# Send a targeted notification
								#pushioAPI.sendCategoryPushNotification(notification, PUSHIO_CATEGORY)
								# or...	
								# Send a broadcast notification
								pushioAPI.sendBroadcastPushNotification(notification)
								markAlertBeenSent(pollID)
	
	def sendPDApiRequest(self, jsonRequest):

		try:
			response = urllib.urlopen("https://api.polldaddy.com/", jsonRequest)
		except URLError, e:
			print "===Polldaddy API response==="
			print "%d failure\n" %(e.code)
			print e.read()
		
		responseDict = json.loads(response.read())

		if responseDict.has_key("pdResponse"):
			pdResponse = responseDict["pdResponse"]
			return pdResponse

					
	def getPDUserCode(self):
	
		request = {
		    "pdAccess": {
		    	"partnerGUID": POLLDADDY_API_KEY,
		        "partnerUserID": "0",
		        "demands": {
		            "demand": {
		                "id": "GetUserCode"
		            }
		        }
		    }
		}
		
		jsonRequest = json.dumps(request)
		response = self.sendPDApiRequest(jsonRequest)
		if response.has_key("userCode"):
			return response["userCode"]
		return None
			
	def getPDPolls(self):
	
		request = {
			"pdRequest" : {
				"partnerGUID" : POLLDADDY_API_KEY,
				"userCode" : self.pdUserCode,
				"demands" : {
					"demand" : {
							"id" : "GetPolls"
						}
				}
			}
		}

		jsonRequest = json.dumps(request)
		response = self.sendPDApiRequest(jsonRequest)
		if response.has_key("demands"):
			demands = response["demands"]
			if demands.has_key("demand"):
				demand = demands["demand"]
				for d in demand:
					if d.has_key("polls"):
						polls =  d["polls"]
						if polls.has_key("poll"):
						 	pollList = polls["poll"]
							return pollList
		
def hasAlertBeenSent(uniqueID):

	try:
		pickleFile = open(PICKLE_FILENAME, 'rb')
	except:
		return False
	else:
		pickleDict = pickle.load(pickleFile)
		pickleFile.close()

		if pickleDict.has_key(uniqueID):
			return True
		else:
			return False

def markAlertBeenSent(uniqueID):
	try:
		pickleFile = open(PICKLE_FILENAME, 'rb')
	except:
		pickleDict = {}
	else:
		pickleDict = pickle.load(pickleFile)
		pickleFile.close()

	pickleDict[uniqueID] = True

	pickleFile = open(PICKLE_FILENAME, 'wb')
	pickle.dump(pickleDict, pickleFile)
	pickleFile.close()

			
if __name__ == '__main__':
	pd = PushioPolldaddy()

