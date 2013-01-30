import gme
class dstRec(gme.base.gmeBase.gmeData):
	"""a class to represent a record of dst data.  Extends :class:`gme.base.gmeBase.gmeData` . Note that Dst data is available from 1980-present day (or whatever the latest WDC has uploaded is).  The data are 1-hour values.
	"""
	
	def parseWeb(self,line):
		import datetime as dt
		cols = line.split()
		self.time = dt.datetime(int(cols[0][0:4]),int(cols[0][5:7]),int(cols[0][8:10]), \
															int(cols[1][0:2]),int(cols[1][3:5]),int(cols[1][6:8]))
		if(float(cols[3]) != 99999.0): self.dst = float(cols[3])
		
	def __init__(self, webLine=None, dbDict=None):
		#note about where data came from
		self.dataSet = 'Dst'
		self.time = None
		self.info = 'These data were downloaded from WDC For Geomagnetism, Kyoto.  *Please be courteous and give credit to data providers when credit is due.*'
		self.dst = None
		
		#if we're initializing from an object, do it!
		if(webLine != None): self.parseWeb(webLine)
		if(dbDict != None): self.parseDb(dbDict)
		
def readDst(sTime=None,eTime=None,dst=None):
	"""This function reads dst data from the mongodb.
	written by AJ, 20130130
	"""
	import datetime as dt
	import pydarn.sdio.dbUtils as db
	
	#check all the inputs for validity
	assert(sTime == None or isinstance(sTime,dt.datetime)), \
		'error, sTime must be a datetime object'
	assert(eTime == None or isinstance(eTime,dt.datetime)), \
		'error, eTime must be either None or a datetime object'
	assert(dst == None or (isinstance(dst,list) and \
		isinstance(dst[0],(int,float)) and isinstance(dst[1],(int,float)))), \
		'error,dst must None or a list of 2 numbers'
		
	if(eTime == None and sTime != None): eTime = sTime+dt.timedelta(days=1)
	qryList = []
	#if arguments are provided, query for those
	if(sTime != None): qryList.append({'time':{'$gte':sTime}})
	if(eTime != None): qryList.append({'time':{'$lte':eTime}})
	if(dst != None): 
		qryList.append({'dst':{'$gte':min(dst)}})
		qryList.append({'dst':{'$lte':max(dst)}})
			
	#construct the final query definition
	qryDict = {'$and': qryList}
	#connect to the database
	dstData = db.getDataConn(dbName='gme',collName='dst')
	
	#do the query
	if(qryList != []): qry = dstData.find(qryDict)
	else: qry = dstData.find()
	if(qry.count() > 0):
		dstList = []
		for rec in qry.sort('time'):
			dstList.append(dstRec(dbDict=rec))
		print '\nreturning a list with',len(dstList),'records of dst data'
		return dstList
	#if we didn't find anything on the mongodb
	else:
		print '\ncould not find requested data in the mongodb'
		return None
			
def readDstWeb(sTime,eTime=None):
	import datetime as dt
	import mechanize
	
	assert(isinstance(sTime,dt.datetime)),'error, sTime must be a datetime object'
	if(eTime == None): eTime = sTime
	assert(isinstance(eTime,dt.datetime)),'error, eTime must be a datetime object'
	assert(eTime >= sTime), 'error, eTime < eTime'
	
	sCent = sTime.year/100
	sTens = (sTime.year - sCent*100)/10
	sYear = sTime.year-sCent*100-sTens*10
	sMonth = sTime.strftime("%m")
	eCent = eTime.year/100
	eTens = (eTime.year - eCent*100)/10
	eYear = eTime.year-eCent*100-eTens*10
	eMonth = eTime.strftime("%m")
	
	br = mechanize.Browser()
	br.set_handle_robots(False)   # no robots
	br.set_handle_refresh(False)  # can sometimes hang without this
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
	br.open('http://wdc.kugi.kyoto-u.ac.jp/dstae/index.html')
	
	br.form = list(br.forms())[0]
	
	br.form.find_control('SCent').value = [str(sCent)]
	br.form.find_control('STens').value = [str(sTens)]
	br.form.find_control('SYear').value = [str(sYear)]
	br.form.find_control('SMonth').value = [sMonth]
	br.form.find_control('ECent').value = [str(eCent)]
	br.form.find_control('ETens').value = [str(eTens)]
	br.form.find_control('EYear').value = [str(eYear)]
	br.form.find_control('EMonth').value = [eMonth]
	
	br.form.find_control('Output').value = ['DST']
	br.form.find_control('Out format').value = ['IAGA2002']
	br.form.find_control('Email').value = "vt.sd.sw@gmail.com"
	
	response = br.submit()
	
	lines = response.readlines()

	dstList = []
	for l in lines:
		#check for headers
		if(l[0] == ' ' or l[0:4] == 'DATE'): continue
		cols=l.split()
		try: dstList.append(dstRec(webLine=l))
		except Exception,e:
			print e
			print 'problemm assigning initializing dst object'
		
	if(dstList != []): return dstList
	else: return None

def mapDstMongo(sYear,eYear=None):
	import pydarn.sdio.dbUtils as db
	import os, datetime as dt
	
	#check inputs
	assert(isinstance(sYear,int)),'error, sYear must be int'
	if(eYear == None): eYear=sYear
	assert(isinstance(eYear,int)),'error, sYear must be None or int'
	assert(eYear >= sYear), 'error, end year greater than start year'
	
	#get data connection
	mongoData = db.getDataConn(username=os.environ['DBWRITEUSER'],password=os.environ['DBWRITEPASS'],\
								dbAddress=os.environ['SDDB'],dbName='gme',collName='dst')
	
	#set up all of the indices
	mongoData.ensure_index('time')
	mongoData.ensure_index('dst')
	
	for yr in range(sYear,eYear+1):
		#1 day at a time, to not fill up RAM
		templist = readDstWeb(dt.datetime(yr,1,1),dt.datetime(yr,12,31))
		for rec in templist:
			#check if a duplicate record exists
			qry = mongoData.find({'time':rec.time})
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
				print 'strange, there is more than 1 DST record for',rec.time
		del templist
		

	