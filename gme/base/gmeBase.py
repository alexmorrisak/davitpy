"""
.. module:: gmeBase
   :synopsis: A base class for gme data.  Allows definition of common routines

.. moduleauthor:: AJ, 20130129

*****************************
**Module**: gmeBase
*****************************
**Classes**:
	* :class:`gmeData`
"""
class gmeData:
	def parseDb(self,dbDict):
		"""This method is used to parse a dictionary of gme data from the mongodb into a :class:`gmeData` object.  
		
		.. note:: 
			In general, users will not need to use this.
		
		**Belongs to**: :class:`gmeData`
		
		**Args**: 
			* **dbDict** (dict): the dictionary from the mongodb
		**Returns**:
			* Nothing.
		**Example**:
			::
			
				myObj.parseDb(mongoDbDict)
			
		written by AJ, 20130129
		"""
		#iterate over the mongo dict
		for attr, val in dbDict.iteritems():
			#check for mongo _id attribute
			if(attr == '_id'): pass
			elif(attr == 'kp'):
				for i in range(len(dbDict['kp'])):
					num = str(int(dbDict['kp'][i]))
					mod = dbDict['kp'][i] - int(dbDict['kp'][i])
					if(mod == .3): mod = '-'
					elif(mod == .7): mod = '+'
					else: mod = ''
					self.kp.append(num+mod) 
			else:
				#assign the value to our object
				try: setattr(self,attr,val)
				except Exception,e:
					print e
					print 'problem assigning',attr
					
	def toDbDict(self):
		"""This method is used to convert a :class:`gmeData` object into a mongodb data dictionary.
		
		.. note::
			In general, users will not need to worry about this
		
		**Belongs to**: :class:`gmeData`
		
		**Args**: 
			* Nothing.
		**Returns**:
			* **dbDict** (dict): a dictionary in the correct format for writing to the mongodb
		**Example**:
			::
			
				mongoDbDict = myObj.todbDict()
			
		written by AJ, 20130129
		"""
		#initialize a new dictionary
		dbDict = {}
		#create dictionary entries for all out our attributes
		for attr, val in self.__dict__.iteritems():
			if(attr == 'kp'):
				dbDict['kp'] = []
				for i in range(len(self.kp)):
					num = int(self.kp[i][0:1])
					mod = self.kp[i][1:2]
					if(mod == '+'): num += .7
					elif(mod == '-'): num += .3
					else: num += .5
					dbDict['kp'].append(num)
			else: dbDict[attr] = val
		return dbDict
		
	def __repr__(self):
		myStr = self.dataSet+' record FROM: '+str(self.time)+'\n'
		for key,var in self.__dict__.iteritems():
			myStr += key+' = '+str(var)+'\n'
		return myStr
	
	def __init__():
		self.time = None
		self.dataSet = None
		self.info = None