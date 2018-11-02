import os, re, sys, time
import requests
import random as rnd

class SearchEigens(object):
    GOOGLE_REST = u'https://www.google.com/search'
    #GOOGLE_PARN = re.compile(u'imgurl=([^&]+)&amp;')
    GOOGLE_PARN = re.compile(u'"ou":"([^&]+)"')

    BING_REST = u'http://www.bing.com/images/async'
    BING_PARN = re.compile(u'imgurl:&quot;([^&]+)&quot;')

    HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}

    def __init__(self, *args, **kwargs):
        return super(SearchEigens, self).__init__(*args, **kwargs)

    '''
    def find_ext(self, url):
        surl = url.lower()
        if surl.find('.jpg') != -1:
            return 'jpg'
        if surl.find('.jpeg') != -1:
            return 'jpg'
        elif surl.find('.png') != -1:
            return 'png'
        elif surl.find('.bmp') != -1:
            return 'bmp'
        else:
            return ''
    '''

    def query_keyword(self, keyword):
        bseeds = self.bing_query(keyword)
        gseeds = self.google_query(keyword)
        
        seeds = []

        seen = set()
        for name, url in bseeds:
            seen.add(url)
            fn = '[%s]_bing_%s'%(keyword, name)
            seeds.append((fn, url))

        for name, url in gseeds:
            if url not in seen:
                fn = '[%s]_google_%s'%(keyword, name)
                seeds.append((fn, url))

        #asseds = set.union(bseeds, gseeds)
        #for nidx, seed in enumerate(aseeds):
        #	#ext = self.find_ext(seed)
        #	#if ext == 'jpg':
        #	#	pass

        #	pad = anz - len(str(nidx + 1))
            
        #	if seed in bseeds:
        #		prefix = 'bing'
        #	else:
        #		prefix = 'google'

        #	fn = '[%s]_%s_n%s%d'%(keyword, prefix, '0' * pad, nidx + 1)
        #	seeds.append((fn, seed))

        return seeds

    @staticmethod
    def bing_query(keyword):
        params = {'q':keyword, 'count':'150', 'dgsrr':'false', 'async':'content'}

        seeds = []

        seen = set()
        for sn, sz in enumerate(['medium', 'large', 'wallpaper'][::-1]):
            params['first'] = 0
            params['qft'] = 'filterui:photo-photo filterui:imagesize-%s'%sz

            nfail = 0
            while True:
                sys.stdout.write('Querying [%s] with Bing [size:%s from:%4d] ... '%(keyword, sz, params['first']))

                tstart = time.clock()
                rest = requests.get(SearchEigens.BING_REST, headers=SearchEigens.HEADERS, params=params)

                if rest.status_code == 200:
                    sys.stdout.write('\t Done. [SUCC] (%.2fs)\n'%(time.clock() - tstart))

                    urls = re.findall(SearchEigens.BING_PARN, rest.content) 
                    if len(urls) == 0:
                        break
                    elif len(seen) >= 10000:
                        break
                    else:
                        osize = len(seen)
                        for ofs, url in enumerate(urls):
                            if url not in seen:
                                seen.add(url)
                                seeds.append(('s%d_f%04d'%(sn, params['first'] + ofs), url))

                        if len(seen) - osize == 0 and params['first'] > 0:
                            break
                        params['first'] += len(urls)
                else:
                    sys.stdout.write('\t . [FAIL] (TRAIL %d ... )\n'%(nfail + 1))
                    
                    nfail += 1
                    if nfail >= 10:
                        sys.stdout.write('===============> MAX TRAILS REACHED. [ABOART]. \n')
                        break
                    time.sleep(5)

                time.sleep(0.2 * (1 + rnd.random()))
        
        return seeds
    
    @staticmethod
    def google_query(keyword):
        params = {'q':keyword, 'tbm':'isch', 'as_st':'y', 'safe':'active'}

        seeds = []

        seen = set()
        for sn, sz in enumerate(['vga', 'svga', 'xga', '2mp', '4mp'][::-1]):
            params['tbs'] = 'itp:photo,ift:jpg,isz:lt,islt:%s'%sz
            params['ijn'] = 0

            nfail, imofs = 0, 0
            while True:
                sys.stdout.write('Querying [%s] with Google [size:%s page:%2d] ... '%(keyword, sz, params['ijn']))

                tstart = time.clock()
                rest = requests.get(SearchEigens.GOOGLE_REST, headers=SearchEigens.HEADERS, params=params)

                if rest.status_code == 200:
                    sys.stdout.write('\t Done. [SUCC] (%.2fs)\n'%(time.clock() - tstart))

                    urls = re.findall(SearchEigens.GOOGLE_PARN, rest.content)
                    if len(urls) == 0:
                        break
                    elif len(seen) >= 10000:
                        break
                    else:
                        osize = len(seen)
                        for url in urls:
                            if url not in seen:
                                seen.add(url)
                                seeds.append(('s%d_f%04d'%(sn, imofs), url))
                            imofs += 1

                        if len(seen) - osize == 0 and params['ijn'] > 0:
                            break

                        params['ijn'] += 1
                else:
                    sys.stdout.write('\t . [FAIL] (TRAIL %d ... )\n'%(nfail + 1))

                    nfail += 1
                    if nfail >= 10:
                        sys.stdout.write('===============> MAX TRAILS REACHED. [ABOART]. \n')
                        break
                    time.sleep(5)

                time.sleep(0.2 * (1 + rnd.random()))
        return seeds
