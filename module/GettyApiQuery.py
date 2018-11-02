import requests, json, threading
import sys, time, datetime
import copy
import random as rnd

from queue import Queue
from Utils import Utils
from string import Template

class GettyApi(object):
    """
    Query on Image Services with keywords or group name
    """

    GETTY_REST = u'https://api.gettyimages.com:443/v3/search/images?'

    def __init__(self, params):
        self.api_key = u'%s'%params['getty_api_key']
        self.query_pages = min(int(params.get('getty_api_query_pages', 100)), 100)
        self.query_page_size = min(int(params.get('getty_api_page_size', 100)), 100)

    def query(self, params, queue, page_from, page_to, lock):
        error = 0
        message = ''
        phrase = params.get('phrase')
        if not phrase:
            raise ValueError('Phrase to search must be supplied [GettyApi].')

        headers = {'Api-Key':self.api_key, 'Host':'api.gettyimages.com'}

        start = time.clock()
        for page in range(page_from, page_to + 1):
            params['page'] = page

            trails = 0
            while True:
                response = requests.get(GettyApi.GETTY_REST, params, headers=headers, 
                                    timeout=Utils.QUERY_TIMEOUT)

                if response:
                    if response.status_code == 200:
                        results = json.loads(response.content.decode('utf-8'))

                        for image in results['images']:
                            for entry in image['display_sizes']:
                                fname = u'[%s]_getty_api_%s.jpg'%(phrase, image[u'id'])
                                queue.put((fname, entry['uri']))
                        break
                    elif response.status_code in [400, 401, 403]:
                        error = 1
                        results = json.loads(response.content)
                        message = results['message']
                        break
                    else:
                        trails += 1
                        time.sleep(0.5 * (1 + rnd.random()))
                else:
                    trails += 1

                if trails > Utils.QUERY_MAX_TRAIL:
                    error = 1
                    message = 'Max Trails Reached'
                    break
            
            # have a rest (3 query per second limitation)
            time.sleep(0.2 * (1 + rnd.random()))

        with lock:
            end = time.clock()
            if message:
                message = '%s(%s)'%(Utils.QUERY_ERROR_CODE[error], message)
            else:
                message = Utils.QUERY_ERROR_CODE[error]
            print('Querying [%s] from GettyAPI from page %d to %d ... \t [%s] (%.3fs)'%(phrase, page_from, page_to, \
                                                                                    message, end - start))
            
        
    def query_keyword(self, keyword, thread_num=5):        
        params = {'sort_order':'best_match',
                  'file_types':'jpg',
                  'page_size':self.query_page_size,
                  'phrase':keyword}

        threads = []

        queue = Queue()
        lock = threading.Lock()

        if self.query_pages >= thread_num:
            indcs = Utils.seperator(self.query_pages, thread_num, start=1)
            
            for n in range(1, thread_num + 1):
                threads.append(threading.Thread(target=self.query,
                                                args=(copy.deepcopy(params), queue, indcs[n - 1], indcs[n], lock,)))
        else:
            for n in range(1, self.query_pages + 1):
                threads.append(threading.Thread(target=self.query,
                                                args=(copy.deepcopy(params), queue, n, n + 1, lock,)))

        for t in threads:
            t.start()
            time.sleep(0.3 * (1 + rnd.random()))

        for t in threads:
            t.join()

        seeds = set()
        while not queue.empty():
            seeds.add(queue.get())

        return list(seeds)
        
        return list(urls)

if __name__ == '__main__':
    params = {'getty_api_key':u'qese4bqat3hxtprsfzypdypm', 'query_page_size':10, 'query_pages':100}
    getty = GettyApi(params)
    urls = getty.query_keyword('cat')
    print(len(urls))
