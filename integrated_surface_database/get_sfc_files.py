#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftplib
import os
import re
import socket

ftp = ftplib.FTP('ftp.ncdc.noaa.gov');
ftp.login("anonymous","christopher.mccray@mail.mcgill.ca")
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
