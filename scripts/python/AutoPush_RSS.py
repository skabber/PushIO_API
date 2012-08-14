#!/usr/bin/env python
# encoding: utf-8
"""
AutoPush_RSS.py

This script makes it easy send push notifications via Push IO when a new RSS story is published.
You can run this script from cron, in order to automate the process. 

Copyright (c) 2012 Push IO LLC. All rights reserved.
"""

# Find these values on the Set Up > API page from your Push IO dashboard.
PUSHIO_APP_ID = ""
PUSHIO_SERVICE_SECRET = ""

# The segment of your users you want to target.
# Corresponds to a category registration.
PUSHIO_CATEGORY = ""

RSS_URL = ""
# A few samples...
#RSS_URL = "http://news.yahoo.com/rss/"
#RSS_URL = "http://rss.cnn.com/rss/cnn_topstories.rss"

# A file where we persist q unique ID to track if a notification has already been sent
PICKLE_FILENAME = "AutoPush_RSS.pkl"

import sys
import os
import feedparser
import pickle
import pushio


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
	
		

def main():
	
	pushioAPI = pushio.API(PUSHIO_APP_ID, PUSHIO_SERVICE_SECRET, debug=True)
	
	try:
		rssData = feedparser.parse(RSS_URL)
	except:
		print "Failed to open RSS url: %s" %(RSS_URL)
	else:
		if rssData.has_key("feed"):
			entries = rssData["entries"]
			for entry in entries:
				title = entry["title"]

				# We are going to use the id (usually a URL path for the article), as the way to determine if
				# the notification needs to be sent or has already been pushed.
				uniqueID = entry["id"]

				if (hasAlertBeenSent(uniqueID)):
					print "Push notification has already been sent: %s\n" %(uniqueID)
					continue
				else:
					
					notification = pushio.Notification(message=title)
					
					# Send a targeted notification
					sendCategoryPushNotification(notification, PUSHIO_CATEGORY)
					# or...	
					# Send a broadcast notification
					#sendBroadcastPushNotification(notification)
					markAlertBeenSent(uniqueID)

	
					
if __name__ == '__main__':
	main()

