"""
.. module:: tec
   :synopsis: A module for reading, writing, and storing TEC Data

.. moduleauthor:: Evan, 20130130

**Module**: gme.tec.tec
*************************
**Classes**:
	* :class:`tecRec`
**Functions**:
	* :func:`readTec`
	* :func:`readTecFtp`
	* :func:`mapTecMongo`
"""
import gme
class tecRec(gme.base.gmeBase.gmeData):
	"""a class to represent a record of tec data.  Extends gmeData.  Insight on the class members can be obtained from `the NASA SPDF site <ftp://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/hroformat.txt>`_.  note that Omni data is available from 1995-present day (or whatever the latest NASA has uploaded is), in 1 and 5 minute resolution.
	
	.. warning::
		AE,AL,AU,SYM/H,SYM/D,ASYM/H,and ASYM/D are included in the omni files and thus are read into this class.  I cannot verify the quality of these indices distributed with Omni data.  For quality assurance on these indices, use the functions in the gme.mag.indices module.
		
	**Members**: 
		* **time** (`datetime <http://tinyurl.com/bl352yx>`_): an object identifying which time these data are for
		* **glat** (int): geographic latitude of the tec measurement, degrees
		* **glon** (int): geographic longitude of the tec measurement, degrees
		* **tec** (float): total electron content measurement, TECU or 1x10^16 electrons/m^2
		* **dtec** (float): error in total electron content measurement, TECU
		* **info** (str): information about where the data come from.  *Please be courteous and give credit to data providers when credit is due.*
		
	.. note::
		If any of the members have a value of None, this means that they could not be read for that specific time
   
	**Methods**:
		* :func:`parseFtp`
	**Example**:
		::
		
			emptyTecObj = gme.tec.tecRec()
		
	written by Evan, 20130130
	"""
		
	def parseFtp(self,line):
		"""This method is used to convert a line of TEC data read from the Millstone Hill Madrigal site into a :class:`tecRec` object.
		
		.. note::
			In general, users will not need to worry about this.
		
		**Belongs to**: :class:`tecRec`
		
		**Args**: 
			* **line** (str): the ASCII line from the FTP server
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myTecObj.parseFtp(ftpLine)
			
		written by Evan, 20130131
		"""
		import datetime as dt
		
		#a dict to map from the column number in the line to attribute name
		mappingdict = {9:'timeshift',13:'bMagAvg',14:'bx',15:'bye',16:'bze',17:'bym', \
										18:'bzm',21:'flowSpeed',22:'vxe',23:'vye',24:'vze',25:'np', \
										26:'temp',27:'pDyn',28:'e',29:'beta',30:'machNum',37:'ae', \
										38:'al',39:'au',40:'symd',41:'symh',42:'asyd',43:'asyh'}
										
		#split the line into cols
		cols = line.split()
		self.time = dt.datetime(int(cols[0]), 1, 1, int(cols[2]),int(cols[3])) + \
									dt.timedelta(days=(int(cols[1])-1))
									
		#go through the columns and assign the attribute values 
		for i in range(9,len(cols)):
			if(not mappingdict.has_key(i)): continue
			temp = cols[i]
			temp = temp.replace('.','')
			temp = temp.replace('9','')
			if(temp == ''): continue
			try: setattr(self,mappingdict[i],float(cols[i]))
			except Exception,e:
				print e
				print 'problem assigning value to',mappingdict[i]
			
	def __init__(self, ftpLine=None, dbDict=None):
		"""the intialization function for a :class:`tecRec` object.  
		
		.. note::
			In general, users will not need to worry about this.
		
		**Belongs to**: :class:`tecRec`
		
		**Args**: 
			* [**ftpLine**] (str): an ASCII line from the FTP server. if this is provided, the object is initialized from it.  default=None
			* [**dbDict**] (dict): a dictionary read from the mongodb.  if this is provided, the object is initialized from it.  default = None
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myTecObj = tecRec(ftpLine=aftpLine)
			
		written by Evan, 20130130
		"""
		#initialize the attributes
		#note about where data came from
		self.dataSet = 'TEC'
		self.info = 'These data were downloaded from Madrigal.  *Please be courteous and give credit to data providers when credit is due.*'
		self.glat = None
		self.glon = None
		self.tec = None
		self.dtec = None
		#if we're initializing from an object, do it!
		if(ftpLine != None): self.parseFtp(ftpLine)
		if(dbDict != None): self.parseDb(dbDict)
	
def readTec(sTime,eTime=None,glat=None,glon=None,tec=None,dtec=None):
	"""This function reads TEC data.  First, it will try to get it from the mongodb, and if it can't find it, it will look on the Madrigal server using :func:`readTecFtp`
	
	**Args**: 
		* **sTime** (`datetime <http://tinyurl.com/bl352yx>`_ or None): the earliest time you want data for
		* [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, end Time will be 1 day after sTime.  default = None
		* [**glat**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with glat values in the range [a,b] will be returned.  default = None
		* [**glon**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with glon values in the range [a,b] will be returned.  default = None
		* [**tec**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with tec values in the range [a,b] will be returned.  default = None
		* [**dtec**] (list or None): if this is not None, it must be a 2-element list of numbers, [a,b].  In this case, only data with dtec values in the range [a,b] will be returned.  default = None
	**Returns**:
		* **tecList** (list or None): if data is found, a list of :class:`tecRec` objects matching the input parameters is returned.  If no data is found, None is returned.
	**Example**:
		::
		
			import datetime as dt
			tecList = gme.tec.readTec(sTime=dt.datetime(2011,1,1),eTime=dt.datetime(2011,6,1),glat=[0,90],glon=[-180,-90])
		
	written by Evan, 20130130
	"""
	
	import datetime as dt
	import pydarn.sdio.dbUtils as db
	
	#check all the inputs for validity
	assert(isinstance(sTime,dt.datetime)), \
		'error, sTime must be a datetime object'
	assert(eTime == None or isinstance(eTime,dt.datetime)), \
		'error, eTime must be either None or a datetime object'
	var = locals()
	for name in ['glat','glon','tec','dtec']:
		assert(var[name] == None or (isinstance(var[name],list) and \
			isinstance(var[name][0],(int,float)) and isinstance(var[name][1],(int,float)))), \
			'error,'+name+' must None or a list of 2 numbers'
		
	if(eTime == None): eTime = sTime+dt.timedelta(days=1)
	qryList = []
	#if arguments are provided, query for those
	qryList.append({'time':{'$gte':sTime}})
	if(eTime != None): qryList.append({'time':{'$lte':eTime}})
	var = locals()
	for name in ['glat','glon','tec','dtec']:
		if(var[name] != None): 
			qryList.append({name:{'$gte':min(var[name])}})
			qryList.append({name:{'$lte':max(var[name])}})
			
	#construct the final query definition
	qryDict = {'$and': qryList}
	#connect to the database
	tecData = db.getDataConn(dbName='gme',collName='tec')
	
	#do the query
	if(qryList != []): qry = tecData.find(qryDict)
	else: qry = tecData.find()
	if(qry.count() > 0):
		tecList = []
		for rec in qry.sort('time'):
			tecList.append(tecRec(dbDict=rec))
		print '\nreturning a list with',len(tecList),'records of tec data'
		return tecList
	#if we didn't find anything on the mongodb
	else:
		print '\ncould not find requested data in the mongodb'
		print 'we will look on the Madrigal server, but your conditions will be (mostly) ignored'
		
		#read from Madrigal server
		tecList = readTecFtp(sTime, eTime)
		
		if(tecList != None):
			print '\nreturning a list with',len(tecList),'recs of tec data'
			return tecList
		else:
			print '\n no data found on Madrigal server, returning None...'
			return None
			
def readTecFtp(sTime,eTime=None):
	"""This function reads TEC data from the MIT Haystack Madrigal server.
	
	.. warning::
		You should not use this. Use the general function :func:`readTec` instead.
	
	**Args**: 
		* **sTime** (`datetime <http://tinyurl.com/bl352yx>`_): the earliest time you want data for
		* [**eTime**] (`datetime <http://tinyurl.com/bl352yx>`_ or None): the latest time you want data for.  if this is None, eTime will be equal to sTime.  default = None
	**Returns**:
		* **tecList** (list or None): if data is found, a list of :class:`tecRec` objects matching the input parameters is returned.  If no data is found, None is returned.
	**Example**:
		::
		
			import datetime as dt
			tecList = gme.tec.readTecFtp(dt.datetime(2011,1,1,1,50),eTime=dt.datetime(2011,1,1,10,0))
		
	written by Evan, 20130131
	"""
	
	from ftplib import FTP
	import datetime as dt
	import madrigalWeb.madrigalWeb
	
	assert(isinstance(sTime,dt.datetime)),'error, sTime must be datetime'
	if(eTime == None): eTime=sTime
	assert(isinstance(eTime,dt.datetime)),'error, eTime must be datetime'
	assert(eTime >= sTime), 'error, end time greater than start time'
	
	#Madrigal login information
	user_fullname = 'Evan Thomas'
	user_email = 'egthomas@vt.edu'
	user_affiliation = 'Virginia Tech'
	
	madrigalUrl = 'http://madrigal.haystack.mit.edu/madrigal'
	instcode = 8000		#World-wide GPS Receiver Network
	kindat = 3500		#Minimum scalloping TEC processing
	category = 1		#Default file to download
	
	#connect to Madrigal
	testData = madrigalWeb.madrigalWeb.MadrigalData(madrigalUrl)
	
	#call API to list all experiments for given instruments and a time range
	try: expList = testData.getExperiments(instcode, sTime.year, sTime.month, sTime.day, sTime.hour, sTime.minute, sTime.second,
						eTime.year, eTime.month, eTime.day, eTime.hour, eTime.minute, eTime.second)
	except Exception,e:
		print e
		print 'problem connecting to Madrigal server'
	
	#loop through all experiments
	for i in range(len(expList)):
		#get a list of all files in that experiment
		fileList = testData.getExperimentFiles(expList[i].id)
		
		#loop through each file until the right kindat found for basic parameter data
		for thisFile in fileList:
			if thisFile.category == category and thisFile.kindat == kindat:
				thisFilename = thisFile.name
				break
		
		#get the TEC data
		try: data = testData.isprint(thisFilename, 'hour,min,gdlat,glon,tec,dtec', 'badval=-1.0000e+00',
						user_fullname, user_email, user_affiliation)
		except Exception,e:
			print e
			print 'error retrieving',thisFilename
			
	return data

	
	##list to hold the lines
	#lines = []
	##get the omni data
	#for yr in range(sTime.year,eTime.year+1):
		#if(res == 1): fname = 'omni_min'+str(yr)+'.asc'
		#else: fname = 'omni_5min'+str(yr)+'.asc'
		#print 'RETR '+fname
		#try: ftp.retrlines('RETR '+fname,lines.append)
		#except Exception,e:
			#print e
			#print 'error retrieving',fname
	
	##convert the ascii lines into a list of tecRec objects
	#myTec = []
	#if(len(lines) > 0):
		#for l in lines:
			#linedate = dt.datetime(int(l[0:4]), 1, 1, int(l[8:11]), int(l[11:14])) + \
									#dt.timedelta(int(l[5:8]) - 1)
			#if(sTime <= linedate <= eTime):
				#myTec.append(tecRec(ftpLine=l,res=res))
			#if(linedate > eTime): break
		#return myTec
	#else:
		#return None
		
def mapTecMongo(sYear,eYear=None):
	"""This function reads TEC data from the Madrigal server via remote connection and maps it to the mongodb.  
	
	.. warning::
		In general, nobody except the database admins will need to use this function
	
	**Args**: 
		* **sYear** (int): the year to begin mapping data
		* [**eYear**] (int or None): the end year for mapping data.  if this is None, eYear will be sYear
		* [**res**] (int): the time resolution for mapping data.  Can be either 1 or 5.  default=5
	**Returns**:
		* Nothing.
	**Example**:
		::
		
			gme.tec.mapTecMongo(2007)
		
	written by Evan, 20130130
	"""
	
	import pydarn.sdio.dbUtils as db
	import os, datetime as dt
	
	#check inputs
	assert(isinstance(sYear,int)),'error, sYear must be int'
	if(eYear == None): eYear=sYear
	assert(isinstance(eYear,int)),'error, sYear must be None or int'
	assert(eYear >= sYear), 'error, end year greater than start year'
	
	#get data connection
	mongoData = db.getDataConn(username=os.environ['DBWRITEUSER'],password=os.environ['DBWRITEPASS'],\
								dbAddress=os.environ['SDDB'],dbName='gme',collName='tec')
	
	#set up all of the indices
	mongoData.ensure_index('time')
	mongoData.ensure_index('glat')
	mongoData.ensure_index('glon')
	mongoData.ensure_index('tec')
	mongoData.ensure_index('dtec')
		
	#read the TEC data from the Madrigal server
	for yr in range(sYear,eYear+1):
		templist = readTecFtp(dt.datetime(yr,1,1), dt.datetime(yr,12,31,23,59,59,99999))
		for rec in templist:
			#check if a duplicate record exists
			qry = mongoData.find({'$and':[{'time':rec.time},{'res':rec.res}]})
			print rec.time
			tempRec = rec.toDbDict()
			cnt = qry.count()
			#if this is a new record, insert it
			if(cnt == 0): mongoData.insert(tempRec)
			#if this is an existing record, update it
			elif(cnt == 1):
				print 'foundone!!'
				dbDict = qry.next()
				temp = dbDict['_id']
				dbDict = tempRec
				dbDict['_id'] = temp
				mongoData.save(dbDict)
			else:
				print 'strange, there is more than 1 record for',rec.time
	
	