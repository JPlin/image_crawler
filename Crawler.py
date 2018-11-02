import requests
import re
import os
import sys
import time
import struct
import io
import threading
import DB
import hashlib

from queue import Queue
from html.parser import HTMLParser
from Utils import Utils
from PIL import Image


class BlackList(object):
    BAD_URL = [
        re.compile('photo_unavailable\w*\.\w+'),  ## flickr unavailable images
        re.compile('https?://\w+\.louisvuitton\.com/images/is/image/'
                   ),  ## lv blank images
    ]


class Crawler(object):
    """
    High Speed Image Crawler
    Download Images By Urls
    """

    def __init__(self,
                 name,
                 home,
                 formats,
                 min_image_size=0,
                 max_image_size=0,
                 db_name='url',
                 store_db = False):
        ## alias for this
        self.name = name

        ## des dir to save
        self.home = os.path.join(home, name)
        self.image_folder_name = 'images'

        self.formats = formats[:]
        self.min_image_size = min_image_size
        self.max_image_size = max_image_size

        ## database name
        self.db_name = db_name
        self.db = DB.DB() if store_db else None

        if 'jpeg' in self.formats:
            jidx = self.formats.index('jpeg')
            self.formats[jidx] = 'jpg'

        os.makedirs(self.home, exist_ok=True)
        os.makedirs(
            os.path.join(self.home, self.image_folder_name), exist_ok=True)

    @staticmethod
    def urlunspace(url):
        return HTMLParser().unescape(url)

    ## filter bad urls based on black list
    @staticmethod
    def checku(url):
        for pn in BlackList.BAD_URL:
            if re.search(pn, url):
                return False
        return True

    ## get query content status
    @staticmethod
    def processor(res):
        if res.status_code == 200:
            if Crawler.checku(res.url):
                try:
                    return 0, res.content
                except:
                    return 0, None

            else:
                return 2, None
        else:
            return 1, None

    @staticmethod
    def downloader(out_queue, in_pool, timeout=30):
        '''
        Retrive stream data
        '''

        ## Disable warnings from urllib3
        requests.packages.urllib3.disable_warnings()

        unfinished = []
        for fn_, url_ in in_pool:
            #url_ = Crawler.urlunspace(url_)
            if url_:
                try:
                    res = requests.get(url_, timeout=timeout)
                except:
                    unfinished.append((fn_, url_))
                    continue

                err, con = Crawler.processor(res)

                if err == 0 and con:
                    out_queue.put((fn_, url_, con))
                elif err == 1:
                    unfinished.append((fn_, url_))

        ## retry unfinished image
        if unfinished:
            time.sleep(30)
            for fn_, url_ in unfinished:
                if url_:
                    try:
                        res = requests.get(url_, stream=True, timeout=timeout)
                    except:
                        continue  ## abort

                    err, con = Crawler.processor(res)
                    if err == 0 and con:
                        out_queue.put((fn_, url_, con))

        return

    def store_db(self, dic):
        self.db.start()
        try:
            while True:
                name, value = dic.popitem()
                key = hashlib.md5(value.encode('utf-8')).hexdigest()[8:-8]
                self.db.insert(
                    self.db_name, '(md5 , name , url)',
                    '(\'' + key + '\' , \'' + name + '\' , \'' + value + '\')')
        except:
            return
        finally:
            self.db.commit()

    def checkf(self, ext):
        if not self:
            return False

        _ext = ext.strip().lower()
        while _ext.startswith('.'):
            _ext = _ext[1:]

        if _ext == 'jpeg':
            _ext = 'jpg'

        if _ext in self.formats:
            return True
        else:
            return False

    def start(self, pool, thread_num=256, timeout=5):
        if pool:
            queue = Queue()
            threads = []

            ## Producer
            if len(pool) >= thread_num:
                indcs = Utils.seperator(len(pool), thread_num)

                for n in range(1, thread_num + 1):
                    threads.append(
                        threading.Thread(
                            target=Crawler.downloader,
                            args=(
                                queue,
                                pool[indcs[n - 1]:indcs[n]],
                            )))
            else:
                for n in range(1, len(pool) + 1):
                    threads.append(
                        threading.Thread(
                            target=Crawler.downloader,
                            args=(
                                queue,
                                pool[n - 1:n],
                            )))
            ## start crawling
            print('\nStart Crawling Images ... \t [%d urls]' % (len(pool)))
            start = time.clock()
            for t in threads:
                t.start()

            time.sleep(15)

            ## Consumer
            def dispf(cn, fn):
                sys.stdout.write('\rSaving N%d ... \t [%s] \t\t' % (cn, fn))
                sys.stdout.flush()

            cntim = 1
            fn_url = {}
            while True:
                try:
                    item = queue.get(True, timeout)
                except:
                    if threading.active_count() == 1:
                        break
                    continue

                if item:
                    fn_, url_, buff_ = item
                    # ext_ = Utils.tellf(buff_)
                    bytes_ = io.BytesIO(buff_)

                    try:
                        img_ = Image.open(bytes_)
                        if img_.format == 'JPEG':
                            ext_ = ('jpg', )
                        else:
                            ext_ = (img_.format.lower(), )

                        # resize the image in case it is too large
                        if self.max_image_size > 0 and max(
                                img_.size) > self.max_image_size:
                            ratio_ = self.max_image_size / max(img_.size)
                            nwidth_ = int(round(img_.size[0] * ratio_))
                            nheight_ = int(round(img_.size[1] * ratio_))
                            img_ = img_.resize((nwidth_, nheight_),
                                               resample=Image.LANCZOS)

                            buff_ = io.BytesIO()
                            img_.save(buff_, 'JPEG', quality=95)
                            buff_ = buff_.getvalue()
                            ext_ = ('jpg', )

                        # ignore small images (order cannot be changed)
                        if self.min_image_size > 0 and min(
                                img_.size) < self.min_image_size:
                            ext_ = None

                    except:
                        # ignore bad image
                        ext_ = None

                    if ext_:
                        ext_ = ext_[-1]
                        if self.checkf(ext_):
                            fnm_ = os.path.splitext(fn_)[0]
                            fnm__ = fnm_
                            fnm_ = os.path.join(self.home, self.image_folder_name, f'{fnm_}.{ext_}')
                            # save image
                            with open(fnm_, 'wb') as fb:
                                dispf(cntim, fnm_)

                                fb.write(buff_)

                                fn_url[f'{fnm__}.{ext_}'] = url_
                                cntim += 1

                                # save url to db per 10 steps
                                if self.db and cntim % 10 == 0:
                                    self.store_db(fn_url)
                                    fn_url.clear()

                    #ext = os.path.splitext(fn_)[1]
                    #if ext and self.checkf(ext):
                    #    with open(fnm, 'wb') as fb:
                    #        dispf(cntim, fnm)

                    #        fb.write(buff_)
                    #        cntim += 1
                    #else:
                    #    ext = imghdr.what(None, buff_)
                    #    if ext and self.checkf(ext):
                    #        fnm = '%s.%s'%(fnm, ext)
                    #        with open(fnm, 'wb') as fb:
                    #            dispf(cntim, fnm)

                    #            fb.write(buff_)
                    #            cntim += 1

            # Wait for all of these threads terminate
            for t in threads:
                t.join()

            print('\nCrawling is Done. \t [%d files] (%.2fs)\n' %
                  (cntim, time.clock() - start))

        else:
            raise ValueError('Task pool is empty. [Crawler]')
