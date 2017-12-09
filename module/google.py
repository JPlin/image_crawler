import os, re, time
import datetime, requests

GOOGLE_REST = u'https://www.google.com/search'
GOOGLE_PARN = re.compile(u'"ou":"([^&]+)"')

#header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'}
header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}
params = {'q':'tom cat', 'tbm':'isch'}

#date_max = datetime.datetime.utcnow()
#date_min = date_max + datetime.timedelta(days=-360)

seeds = set()
#for sz in ['islt:xga,isz:l', 'islt:xga,isz:m']:	
for sz in ['vga', 'svga', 'xga', '2mp', '4mp']:

#for nn in range(10):
	#params['cd_min'] = '%d/%d/%d'%(date_min.month, date_min.day, date_min.year)
	#params['cd_max'] = '%d/%d/%d'%(date_max.month, date_max.day, date_max.year)

	#cd_min = '%d/%d/%d'%(date_min.month, date_min.day, date_min.year)
	#cd_max = '%d/%d/%d'%(date_max.month, date_max.day, date_max.year)

	#print cd_min, cd_max
	#params['tbs'] = 'itp:photo,ift:jpg,isz:lt,islt:vga,cdr:1,cd_min:%s,cd_max%s'%(cd_min, cd_max)
	
	params['tbs'] = 'itp:photo,ift:jpg,isz:lt,islt:%s'%sz
	params['ijn'] = 0

	nfail = 0

	while True:
		rest = requests.get(GOOGLE_REST, headers=header, params=params)
		if rest.status_code == 200:
			urls = re.findall(GOOGLE_PARN, rest.content)
			if len(urls) == 0:
				break
			else:
				olds = len(seeds)
				for url in urls:
					seeds.add(url)
				print('Seeds : ', len(seeds), len(urls))

				if len(seeds) - olds == 0:
					break

				params['ijn'] += 1
	
		else:
			nfail += 1
			if nfail >= 10:
				break

			time.sleep(5)

	#date_max += datetime.timedelta(days=-361)
	#date_min += datetime.timedelta(days=-361)
	