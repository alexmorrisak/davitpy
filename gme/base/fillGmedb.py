def fillGmeDb(time='recent')
	import gme, os
	import pydarn.sdio.dbUtils as dbu
	from multiprocessing import Process
	import datetime as dt
	now = dt.datetime.now()
	
	if(time == 'recent'): sYear = now.year-1
	else: 
		sYear=1980
		db.command('repairDatabase')
		db.poes.remove()
		db.omni.remove()
		
	#fill the omni database
	p0 = Process(target=gme.mapOmniMongo, args=(sYear,now.year,1))
	#fill the omni database
	p1 = Process(target=gme.mapOmniMongo, args=(sYear,now.year))
	#fill the poes database
	p2 = Process(target=gme.mapPoesMongo, args=(sYear,now.year))
	#fill the kp database
	p3 = Process(target=gme.mapKpMongo, args=(sYear,now.year))
	#fill the kp database
	p4 = Process(target=gme.mapDstMongo, args=(sYear,now.year))
	#fill the kp database
	p5 = Process(target=gme.mapAeMongo, args=(sYear,now.year))
	
	try: p0.start()
	except Exception,e:
		print e
		print 'problem filling Omni db'
		
	try: p1.start()
	except Exception,e:
		print e
		print 'problem filling Omni db'
		
	try: p2.start()
	except Exception,e:
		print e
		print 'problem filling Poes db'
		
	try: p3.start()
	except Exception,e:
		print e
		print 'problem filling Kp db'
		
	try: p4.start()
	except Exception,e:
		print e
		print 'problem filling Dst db'
		
	try: p5.start()
	except Exception,e:
		print e
		print 'problem filling AE db'
		
		
	p0.join()
	p1.join()
	p2.join()
	p3.join()
	p4.join()
	p5.join()