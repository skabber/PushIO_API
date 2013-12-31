#!/usr/bin/env python
# encoding: utf-8
"""
AutoPush_NewsstandUpdate.py

This script makes it super simple to start background content downloads for your Newsstand app, so users always have your latest content.
Please note that Apple does not allow you to send more than one content update push notification per 24 hour period.

Copyright (c) 2012 Push IO LLC. All rights reserved.
"""

# Find these values on the Set Up > API page from your Push IO dashboard.
PUSHIO_APP_ID = ""
PUSHIO_SERVICE_SECRET = ""

import sys
import os
from pushio import pushio

def main():
	
	pushioAPI = pushio.API(PUSHIO_APP_ID, PUSHIO_SERVICE_SECRET, debug=True)
	pushioAPI.sendNewsstandContentAvailablePushNotification()
	
					
if __name__ == '__main__':
	main()

