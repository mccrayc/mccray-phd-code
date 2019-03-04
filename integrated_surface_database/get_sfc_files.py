#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftplib
import os
import re
import socket

'''
FTP log in to NOAA server to get ISD files for given range of years.
Searches for files that start with 7#####, as these are mostly North American stations. 
Retries once if it doesn't work.
'''
#Enter email below
email = " "
ftp = ftplib.FTP('ftp.ncdc.noaa.gov');
ftp.login("anonymous",email)
ftp.cwd("/pub/data/noaa")
	
for year in range(2016,2017):
	
	direct = "/pub/data/noaa/"+str(year)
	ftp.cwd(direct)
	files = ftp.nlst()
	for fname in files:
            if re.match("7\d{5}-i*",fname):
		print fname+"\n"
		localf = "./"+str(year)+"/"+fname
		#localf = os.path.join(str(year),fname)
	    	with open(localf,'wb') as fil:
	    	     while True:
		               		
			     try:
				ftp.retrbinary('RETR '+fname,fil.write)
				
			     except ftplib.all_errors as e:
				print "%s" % e
                                continue
			     break			
	
ftp.quit()
