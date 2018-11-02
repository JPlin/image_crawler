import requests, json, threading
import sys, time, datetime
import copy
import random as rnd

from queue import Queue
from Utils import Utils
from string import Template

class Flickr(object):
    """
    Query on Image Services with keywords or group name
    """

    FLICKR_REST = u'https://api.flickr.com/services/rest/'
    FLICKR_IMAGE = Template(u'https://farm${farm}.staticflickr.com/${server}/${id}_${secret}_b.jpg')

    def __init__(self, params):
        self.api_key = u'%s'%params['flickr_api_key']
        self.query_tags_only = int(params.get('flickr_query_tags_only', 0))
        self.query_tags_mode = params.get('flickr_query_tags_mode', 'all')
        self.query_counter = int(params.get('flickr_query_counter', 1))
        self.query_interval = int(params.get('flickr_query_interval', 30))
        self.query_pages = int(params.get('flickr_query_pages', 1))
        self.query_photos_per_page = int(params.get('flickr_query_photos_per_page', 100))

    @staticmethod 
    def query(params, queue, query_pages, lock, thres=0.05):
        error = 0

        keyword = params.get('text')
        if not keyword:
            keyword = params.get('tags')
        if not keyword:
            raise ValueError('Keyword to search must be supplied [Flickr].')

        stats = set()

        imofs = 0

        start = time.clock()
        for page in range(1, query_pages + 1):
            params['page'] = str(page)

            trails = 0
            while True:
                response = requests.get(Flickr.FLICKR_REST, params, timeout=Utils.QUERY_TIMEOUT)
                if response:
                    if response.status_code == 200:
                        cont = json.loads(response.content.decode('utf-8'))
                    
                        if cont[u'stat'] == u'ok' and len(cont[u'photos'][u'photo']) > 0:
                            break
                        elif page > int(cont[u'photos'][u'pages']):
                            error = 2
                            break
                        else:
                            trails += 1
                            time.sleep(0.5 * (1 + rnd.random()))
                    else:
                        trails += 1
                        time.sleep(0.5 * (1 + rnd.random()))
                else:
                    trails += 1

                if trails > Utils.QUERY_MAX_TRAIL:
                    error = 1 ## FAIL
                    break

            if error == 0:
                for elem in cont[u'photos'][u'photo']: ## Aggregation
                    owner = elem[u'owner']
                    if owner not in stats or rnd.random() < thres:
                        fn = '[%s]_flickr_f%04d_%s.jpg'%(keyword, imofs, elem[u'id'])
                        queue.put((fn, Flickr.FLICKR_IMAGE.substitute(elem)))
                        stats.add(owner)
                    imofs += 1
            else:
                break

            time.sleep(0.2 * (1 + rnd.random()))

        with lock:
            end = time.clock()
            print('Querying [%s] with flickr from %s to %s ... \t [%s] [%2d Pages] (%.3fs) '%(keyword, \
                                                                                            params['min_upload_date'], \
                                                                                            params['max_upload_date'], \
                                                                                            Utils.QUERY_ERROR_CODE[error], \
                                                                                            page, (end - start)))

    def query_keyword(self, keyword):
        date_max = datetime.datetime.utcnow()
        date_min = date_max + datetime.timedelta(days=-self.query_interval)
        
        # search flickr images under CC licenses and sort by posted date
        params = {'method':'flickr.photos.search', 
                  'api_key':self.api_key, 'media':'photos',
                  'per_page':self.query_photos_per_page, 
                  'license':'2,3,4,5,6,9', 'sort': 'relevance',
                  'format':'json', 'nojsoncallback':'1'}

        if not self.query_tags_only:
            params['text'] = keyword
        else:
            params['tags'] = keyword
            params['tag_mode'] = self.query_tags_mode

        queue = Queue()
        lock = threading.Lock()

        threads = []
        for _ in range(self.query_counter):
            params['min_upload_date'] = date_min.strftime('%Y-%m-%d %H:%M:%S') 
            params['max_upload_date'] = date_max.strftime('%Y-%m-%d %H:%M:%S')

            threads.append(threading.Thread(target=self.query,
                                            args=(copy.deepcopy(params), queue, self.query_pages, lock, )))
            
            ## update time interval
            date_max += datetime.timedelta(days=-self.query_interval-1)
            date_min += datetime.timedelta(days=-self.query_interval-1)
        
        for td in threads:
            td.start()
            time.sleep(0.2 * (1 + rnd.random()))

        for td in threads:
            td.join()

        seeds = set()
        while not queue.empty():
            seeds.add(queue.get())

        return list(seeds)
                    
    def query_group(self, group):
        raise NotImplementedError



