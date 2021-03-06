#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import sys 
import re
from os import listdir, system
from os.path import isfile, join

'''
Code to parse ASCII lines from ISD files. 

Import parse_obs function and pass an ASCII line of the ISD file to return parsed comma-separated 

If directory of ISD files is set in main, script will accept arguments to print out an ob from an ISD file

The following example would print out any obs for Montreal (716270) during the hour of 19990115 0000 UTC.
python parse_isd_ob.py 716270 1999011500


Chris McCray - christopher.mccray@mail.mcgill.ca - March 2017]
'''

def main():
    stn = sys.argv[1]
    date = sys.argv[2]
    #ISD directory must contain subdirectories for each year (e.g. isd_directory/2007/files.gz)
    isd_directory = '/aos/home/cmccray/cages/isd'
    get_parsed_ob(stn, date, isd_directory)

def get_parsed_ob(stn, date):
    '''
    Accepts WMO station code and date in format YYYYMMDDHH, along with directory of ISD files in format base_directory/YYYY/file.gz and searches for obs for given time, then prints out obs. 
    '''

    #Present weather codes from ISD manual
    manCodes = pd.Series(index=list(range(0,100)))
    manCodes[0:50]="NP"; manCodes[50:56]="DZ"; manCodes[56:58]="FZDZ"; manCodes[58:60]="DZRA"
    manCodes[60:66]="RA"; manCodes[66:68]="FZRA"; manCodes[68:70]="RA,SN"; manCodes[70:79]="SN"
    manCodes[79]="PL"; manCodes[80:83]="RA"; manCodes[83:85]="RA,SN"; manCodes[85:87]="SN"
    manCodes[87:89]= "SN,PL"; manCodes[89:91]="GR"; manCodes[91:100]="TSRA"
    autCodes = pd.Series(index=list(range(0,100)))
    autCodes[0:40]="NP"; autCodes[40:43]="PCP"; autCodes[43:45]="LPCP"; autCodes[45:47]="SPCP"
    autCodes[47:49]="FZPCP"; autCodes[50:54]="DZ"; autCodes[54:57]="FZDZ"; autCodes[57:59]="DZ,RA"
    autCodes[60:64]="RA"; autCodes[64:67]="FZRA"; autCodes[67:69]="RA,SN"; autCodes[70:74]="SN"
    autCodes[74:77]="PL"; autCodes[77:79]="SN";autCodes[80:85]="RA"; autCodes[85:88]="SN"
    autCodes[89]="GR"; autCodes[90:97]="TSRA"; autCodes[99]="TOR"
    
    header = "USAF,WBAN,STID,SLAT,SLON,DAT,TYPE,TMPC,DWPC,SPED,DRCT,PMSL,mw1,mw2,mw3,mw4,mw5,mw6,mw7,aw1,aw2,aw3,aw4,aw5,aw6,P01M,Z01I,Z03I,Z06I,ZMISS"
    header_list = header.split(',')
    
    date_dt = pd.to_datetime(date, format='%Y%m%d%H')
    year_dir = isd_directory+'/'+str(date_dt.year)
    files = [f for f in listdir(year_dir) if isfile(join(year_dir, f))]
    for fi in files:
        if fi.startswith(str(stn)):
            matchedFile = year_dir+"/"+fi
            with gzip.open(matchedFile,'rt') as allObs:
                for ob in allObs:
                    #print(str(ob[15:25]))
                    if str(ob[15:25])==str(date):
                        parsed_ob = parse_obs(ob)
                        for field, obs in zip(header_list, parsed_ob):
                            if (field.startswith('mw')) and (obs!='M'):
                                print(field+': '+manCodes[int(obs)])	
                            elif (field.startswith('aw')) and (obs!='M'):
                                print(field+': '+autCodes[int(obs)])
                            else:
                                print(field+': '+str(obs))
                           #print parsed_ob
                           #obDate=datetime.strptime(ob[15:27],'%Y%m%d%H%M')

	
def parse_obs(ob):
	'''
	Parses a given observation ASCII line from the Integrated Surface Database into a comma-delimited string
	that can be output to a CSV
	'''
	#Regular expression matches for various fields
	manMatch= r"MW\d(\d{2})" #Manual weather observation
	autMatch= r"AW\d(\d{2})" #Automated weather observation

	pcpMatch= r"AA101(\d{4})" #Hourly precipitation total
	iceMatch1 = r" I1(\d{3})" #1,3,6 hour ice accretion
	iceMatch3 = r" I3(\d{3})"
	iceMatch6 = r" I6(\d{3})"
	missingIce = r" I1///"

	#Get data from string
	usaf = ob[4:10]; wban=ob[10:15]; obtyp=ob[41:46]; date=ob[15:23]; time=ob[23:27]
	lat=float(ob[28:34])/1000.; lon=float(ob[34:41])/1000.; stn=ob[51:56]
	tmpc=float(ob[87:92])/10.; dwpc=float(ob[93:98])/10.
	slp=float(ob[99:104])/10.; spdms = float(ob[65:69])/10.
	drct=int(ob[60:63])

	#Handle missing values. For wind, set missing direction to 0
	if drct == 999:
		drct = 0
	#Temporarily set SLP of 999.9 to a string, since numeric values of 999.9 will be changed to 'M' for missing
	if slp == 999.9:
		slp = str(slp)
	#Check for present weather codes, precip amounts,  and accretion
	manObs = re.findall(manMatch, ob)
	autObs = re.findall(autMatch, ob)
	pcpObs = re.findall(pcpMatch, ob)
	iceObs1 = re.findall(iceMatch1, ob); iceObs3 = re.findall(iceMatch3, ob); iceObs6 = re.findall(iceMatch6, ob);
	iceMissing = ['True' if re.search(missingIce, ob) else 'False'][0]
	#Parse out hourly precip in mm
	hlypcp = [float(pcpObs[0])/10. if pcpObs else 'M'][0]
	#Parse out ice accretion obs
	iceAccret1 = [float(iceObs1[0])/100. if iceObs1 else 'M'][0]
	iceAccret3 = [float(iceObs3[0])/100. if iceObs3 else 'M'][0]
	iceAccret6 = [float(iceObs6[0])/100. if iceObs6 else 'M'][0]
	#Create lists in which to place present weather observations (max 7 manual, 6 auto)	
	manList = ['M','M','M','M','M','M','M']
	autList = ['M','M','M','M','M','M']
	for n,i in enumerate(manObs[0:7]):
		manList[n] = i
	for m,j in enumerate(autObs[0:6]):
		autList[m] = j
	#Concatenate observation data into a list
	currOb = [usaf, wban, stn, lat, lon, date+"/"+time, obtyp, tmpc, dwpc, spdms, drct, slp]
	#Append present weather, precip, and ice accretion to that list if they were observed
	for manOb in manList:
		currOb.append(str(manOb))
	for autOb in autList:
		currOb.append(str(autOb))
	currOb.append(hlypcp)
	currOb.append(iceAccret1); currOb.append(iceAccret3); currOb.append(iceAccret6)
	currOb.append(iceMissing)
	#Set missing values to 'M'
	for i, val in enumerate(currOb):
		if val in [99999,9999,9999.9,999.9]:
		    currOb[i] = 'M'
	return currOb

if __name__ == "__main__":
	main()
