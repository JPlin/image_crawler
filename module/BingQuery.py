# -*- coding:utf-8 -*-
import os, re, sys, time
import requests
import random as rnd
from Utils import Utils


class Bing(object):
    BING_REST = u'http://www.bing.com/images/async'
    BING_PARN = re.compile(u'imgurl&quot;:&quot;([^&]+)&quot;')
    #BING_PARN = re.compile(u'src=&quot;([^&]+)&quot;')
    HEADERS = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }

    def __init__(self, *args, **kwargs):
        super(Bing, self).__init__(*args, **kwargs)
        self.engine_name = 'bing'

    @staticmethod
    def bing_query(keyword):
        params = {'q': keyword, 'count': '150', 'async': 'content'}

        seeds = []

        seen = set()
        for sn, sz in enumerate(['medium', 'large', 'wallpaper'][::-1]):
            params['first'] = 0
            params['qft'] = 'filterui:photo-photo filterui:imagesize-%s' % sz

            trails = 0
            while True:
                sys.stdout.write(
                    'Querying [%s] with Bing [size:%s from:%4d] ... ' %
                    (keyword, sz, params['first']))

                start = time.clock()
                response = requests.get(
                    Bing.BING_REST,
                    headers=Utils.HEADERS,
                    params=params,
                    timeout=Utils.QUERY_TIMEOUT)
                if response:

                    if response.status_code == 200:
                        sys.stdout.write('\t Done. [SUCC] (%.2fs)\n' %
                                         (time.clock() - start))
                        #print(response.content.decode('utf-8','ignore'))
                        urls = re.findall(
                            Bing.BING_PARN,
                            response.content.decode('utf-8', 'ignore'))
                        print("url num ", len(urls))
                        if len(urls) == 0:
                            break
                        elif len(seen) >= 10000:
                            break
                        else:
                            osize = len(seen)
                            for ofs, url in enumerate(urls):
                                if url not in seen:
                                    seen.add(url)
                                    seeds.append(
                                        ('s%d_f%04d' %
                                         (sn, params['first'] + ofs), url))

                            if len(seen) == osize and params['first'] > 0:
                                break
                            params['first'] += len(urls)
                    else:
                        sys.stdout.write(
                            '\t . [FAIL] (TRAIL %d ... )\n' % (trails + 1))
                        trails += 1
                        time.sleep(1)
                else:
                    trails += 1

                if trails >= 10:
                    sys.stdout.write('... \t MAX TRAILS REACHED [ABOART]. \n')
                    break

                time.sleep(0.2 * (1 + rnd.random()))

        return seeds

    def query_keyword(self, keyword):
        result_set = self.bing_query(keyword)

        seeds = []

        seen = set()
        for name, url in result_set:
            seen.add(url)
            fn = '[%s]_bing_%s' % (keyword, name)
            seeds.append((fn, url))

        return seeds
