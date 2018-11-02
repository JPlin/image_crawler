import os, re, sys, time
import requests
import random as rnd
from Utils import Utils

class Google(object):
    GOOGLE_REST = u'https://www.google.com.hk/search'
    #GOOGLE_PARN = re.compile(u'imgurl=([^&]+)&amp;')
    GOOGLE_PARN = re.compile(u'"ou":"([^,]+)"')

    def __init__(self, *args, **kwargs):
        return super(Google, self).__init__(*args, **kwargs)

    @staticmethod
    def google_query(keyword):
        # params = {'q':keyword, 'oq':keyword, 'tbm':'isch', 'safe':'active'}
        params = {'q':keyword, 'oq':keyword, 'tbm':'isch'}

        seeds = []

        seen = set()
        for sn, sz in enumerate(['vga', 'svga', 'xga', '2mp'][::-1]):
        #for sn, sz in enumerate(['qsvga'][::-1]):
            params['tbs'] = 'itp:photo,isz:lt,islt:%s'%sz
            params['ijn'] = 0

            trails, imofs = 0, 0
            while True:
                sys.stdout.write('Querying [%s] with Google [size:%s page:%2d] ... '%(keyword, sz, params['ijn']))

                start = time.clock()
                response = requests.get(Google.GOOGLE_REST, headers=Utils.HEADERS, params=params, timeout=Utils.QUERY_TIMEOUT)
                if response:
                    if response.status_code == 200:
                        sys.stdout.write('\t Done. [SUCC] (%.2fs)\n'%(time.clock() - start))

                        urls = re.findall(Google.GOOGLE_PARN, response.content.decode('utf-8'))

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

                            if len(seen) == osize and params['ijn'] > 0:
                                break

                            params['ijn'] += 1
                    else:
                        sys.stdout.write('\t . [FAIL] (TRAIL %d ... )\n'%(trails + 1))
                        trails += 1
                        time.sleep(1)
                else:
                    trails += 1

                if trails >= Utils.QUERY_MAX_TRAIL:
                    sys.stdout.write('... \t MAX TRAILS REACHED. [ABOART]. \n')
                    break

                time.sleep(0.2 * (1 + rnd.random()))
        return seeds

    def query_keyword(self, keyword):
        result_set = self.google_query(keyword)
        
        seeds = []

        seen = set()
        for name, url in result_set:
            if url not in seen:
                fn = '[%s]_google_%s.jpg'%(keyword, name)
                seeds.append((fn, url))

        return seeds
