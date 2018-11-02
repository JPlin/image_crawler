import os, re, sys, time
import requests, threading
import random as rnd
from bs4 import BeautifulSoup

from queue import Queue
from Utils import Utils

class Getty(object):
    GETTY_REST = u'http://www.gettyimages.com/search/2/image'
    
    def __init__(self, params):
        self.max_pages = int(params.get('getty_max_pages', 10))
        
    @staticmethod
    def getty_query(keyword, queue, lock, page_from, page_to):
        params = {'family':'creative,editorial', 'sort':'best', 'excludenudity':'true', 'phrase':keyword}

        total_images = 0
        start = time.clock()
        for page in range(page_from, page_to):
            params['page'] = page
            
            message = ''

            trails = 0
            while True:
                response = requests.get(Getty.GETTY_REST, headers=Utils.HEADERS, params=params,
                                        timeout=Utils.QUERY_TIMEOUT)
                if response:
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
                        links = soup.find_all('a', {"class":"search-result-asset-link"})

                        for link in links:
                            getty_id = link['target']
                            image = link.findChild('img')
                            if image and image['src']:
                                total_images += 1
                                queue.put(('[%s]_getty_p%d_%s.jpg'%(keyword, page, getty_id), image['src']))

                        message = 'SUCC'
                        break
                    else:
                        trails += 1
                        time.sleep(0.2)
                else:
                    trails += 1
                    time.sleep(0.2)
                
                if trails >= Utils.QUERY_MAX_TRAIL: # 10 times at most
                    message = 'ABOART'
                    break

            # sleep for while 
            time.sleep(0.2 * (1 + rnd.random()))

        with lock:
            sys.stdout.write('''Querying [%s] with Getty from page %s to %d ... \t [%s] [%d images] (%.3fs)\n'''
                             %(keyword, page_from, page_to, message, total_images, time.clock() - start))
                
    def query_keyword(self, keyword, nthreads=10):
        seeds = set()
        pages = 1

        lock = threading.Lock()
        queue = Queue()

        sys.stdout.write('Start to query [%s] with Getty for top %d pages ... \n'%(keyword, self.max_pages))

        threads = []
        indices = Utils.seperator(self.max_pages, nthreads, start=1)
        for start_page, end_page in zip(indices[:-1], indices[1:]):
            threads.append(threading.Thread(target=self.getty_query,
                                            args=(keyword, queue, lock, 
                                                    start_page, end_page, )))

        for td in threads:    
            td.start()
            time.sleep(0.2 * (1 + rnd.random()))

        for td in threads:
            td.join()

        while not queue.empty():
            seeds.add(queue.get())

        return seeds

if __name__ == '__main__':
    getty = Getty(100)

    queue = Queue.Queue()
    lock = threading.Lock()
    getty.query_keyword('cat')
    
    #getty.getty_query('cat', queue, lock, 1, 2)
    
    #seeds = set()
    #while not queue.empty():
    #    seeds.add(queue.get())

    #print len(seeds)
