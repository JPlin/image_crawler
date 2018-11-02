import re, time, json, copy
import requests, threading
import random as rnd

from queue import Queue
from Utils import Utils

class Fivepx(object):
    """
    500px API service wrapper
    """

    FIVEPX_REST = 'https://api.500px.com/v1/photos/search'

    def __init__(self, params):
        self.consumer_key = params['500px_consumer_key']
        self.query_tags_only = int(params.get('500px_query_tags_only', 0))
        self.query_results_per_page = int(params.get('500px_query_results_per_page', 100))
        self.query_pages = int(params.get('500px_query_pages', 20))
        self.query_categories = params.get('500px_query_categories', None)

    @staticmethod 
    def query(params, queue, pmin, pmax, lock, thres=0.3):
        error = 0
        print(params)
        keyword = params.get('term')
        if not keyword:
            keyword = params.get('tag')
        if not keyword:
            raise ValueError('Keyword to search must be supplied [500px].')
            

        start = time.clock()
        stats = set()

        imofs = (pmin - 1) * params['rpp']
        for page in range(pmin, pmax):
            params['page'] = page

            trails = 0
            while True:
                if trails > Utils.QUERY_MAX_TRAIL:
                    error = 1 ## FAIL
                    break

                reqs = requests.get(Fivepx.FIVEPX_REST, params)
                if reqs.status_code == 200:
                    cont = json.loads(str(reqs.content))
                    if page > cont['total_pages']:
                        error = 2
                    break

                else:
                    trails += 1
                    time.sleep(0.5 * (1 + rnd.random()))

            if error == 0:
                for elem in cont[u'photos']: ## Aggregation
                    owner = elem[u'user_id']
                    if owner not in stats or rnd.random() < thres:
                        ext = elem['image_format'].lower()
                        fnm = '[%s]_500px_f%04d_%s.%s'%(keyword, imofs, elem[u'id'], ext)
                        queue.put((fnm, elem['image_url']))
                        stats.add(owner)
                    imofs += 1
            else:
                break			

            time.sleep(0.2 * (1 + rnd.random()))

        with lock:
            end = time.clock()
            print('Querying [%s] with 500px from page %d to %d ... \t [%s] (%.3fs) '%(keyword, pmin, pmax - 1,  \
                                                                                    Utils.QUERY_ERROR_CODE[error], \
                                                                                    (end - start)))
        
    def query_keyword(self, keyword, thread_num=20):
        params = {'consumer_key':self.consumer_key, 'rpp':self.query_results_per_page, 'image_size':4, 'sort':'_score'}
        if not self.query_tags_only:
            params['term'] = keyword
        else:
            params['tag'] = keyword

        if self.query_categories:
            params['only'] = self.query_categories

        threads = []
        
        queue = Queue()
        tlock = threading.Lock()

        if self.query_pages >= thread_num:
            indcs = Utils.seperator(self.query_pages, thread_num, start=1)
            
            for n in range(1, thread_num + 1):
                threads.append(threading.Thread(target=self.query,
                                                args=(copy.deepcopy(params), queue, indcs[n - 1], indcs[n], tlock,)))
        else:
            for n in range(1, self.query_pages + 1):
                threads.append(threading.Thread(target=self.query,
                                                args=(copy.deepcopy(params), queue, n, n + 1, tlock,)))

        for t in threads:
            t.start()
            time.sleep(0.2 * (1 + rnd.random()))

        for t in threads:
            t.join()

        seeds = set()
        while not queue.empty():
            seeds.add(queue.get())

        return list(seeds)