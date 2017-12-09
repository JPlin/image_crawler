import re, time, requests

BING_REST = u'http://www.bing.com/images/async'
BING_PARN = re.compile(u'imgurl:&quot;([^&]+)&quot;')

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}

#header = {'Uer-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36'}

def bing_query(keyword):
	params = {'q':keyword, 'count':'150'}

	seeds = set()
	for sz in ['medium', 'large', 'wallpaper']:
		params['first'] = 0
		params['qft'] = 'filterui:photo-photo filterui:imagesize-%s'%sz

		while True:
			rest = requests.get(BING_REST, headers=HEADERS, params=params)

			if rest.status_code == 200:
				urls = re.findall(BING_PARN, rest.content) 
				if len(urls) == 0:
					break
				else:
					osize = len(seeds)
					for url in urls:
						seeds.add(url)

					if len(seeds) - osize == 0:
						break

					print('Seeds : ', len(seeds), len(urls))
					params['first'] += len(urls)

			else:
				time.sleep(1)
	
	return seeds

#for seed in seeds:
#	res = requests.get(seed, stream=True, timeout=20)
#	if res.status_code == 200:
#		dst = os.path.join('D:\\Dst', os.path.basename(seed))

#		img = open(dst, 'wb')
#		img.write(res.content)
#		img.close()



#parser = HTMLParser()

#text = r"imgurl=http://images.clipartpanda.com/cup-clip-art-royalty-free-cup-clipart-illustration-1127911.jpg&amp;imgrefurl=http://www.clipartpanda.com/categories/coffee-cup-clip-art-black-white&amp;faefaefaefaefefimgurl=http://images.clipartpanda.com/cup-clip-art-royalty-free-cup-clipart-illustration-1127911.jpg&amp;imgrefurl=http://www.clipartpanda.com/categories/coffee-cup-clip-art-black-white&amp;"

## imgurl
#pattern = re.compile(u'imgurl=([^&]+)')
#res = re.findall(pattern, text)
#print len(res)

## parse HTML
#with open(r"C:\Users\v-ximing.FAREAST\Desktop\f.txt", 'r') as fp:
#	html = fp.read()


#res = re.findall(pattern, html) 
#print res[0]
