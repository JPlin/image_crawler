# -*- coding:utf-8 -*-
from module.BingQuery import Bing
from module.GoogleQuery import Google
from module.FlickrQuery import Flickr
from module.FivepxQuery import Fivepx
from module.GettyQuery import Getty
from module.GettyApiQuery import GettyApi

from Crawler import Crawler

from Utils import Utils

import random as rnd
import os, codecs, sys
from multiprocessing import Pool


# query keyword by the engine supplied
def queryk(engines, keyword, seeds):
    for engine in engines:
        seeds += engine.query_keyword(keyword)


# this is used to deduplicate the urls
def deduplicate(urls):
    seeds = []

    fseen, useen = set(), set()
    for fn, url in urls:
        fid = Utils.extract_flickr_id(url)
        if fid:  ## Flickr Stype URL
            if fid not in fseen:
                fseen.add(fid)
                seeds.append((fn, url))
        else:  ## Common URL
            if url not in useen:
                useen.add(url)
                seeds.append((fn, url))

    return seeds


## one process for one keyword
def run_proc(db_name, keyword, params, engines):
    print('Child processs %s start.' % (db_name))

    formats = list(
        set([x.strip().lower() for x in params['formats'].split(',')]))
    min_image_size = int(params.get('min_image_size', 0))
    max_image_size = int(params.get('max_image_size', 0))

    ## get all image url
    seeds = []

    if type(keyword) == list:
        topic = keyword[0]
        if int(int(params.get('use_flickr', 0))) == 1 and int(
                params.get('flickr_query_tags_only',
                           0)) == 1:  ## query tags only mode
            print(":??s")
            flickr = Flickr(params)
            flickr.query_keyword(keyword[1:])
        else:
            for _keyword in keyword[1:]:
                queryk(engines, _keyword, seeds)

    elif type(keyword) == str:
        topic = keyword
        queryk(engines, keyword, seeds)

    seeds = deduplicate(seeds)
    rnd.shuffle(seeds)

    ## download all images by urls
    crawler = Crawler(
        topic,
        params['database'],
        formats,
        min_image_size=min_image_size,
        max_image_size=max_image_size,
        db_name=db_name)

    with codecs.open(
            os.path.join(params['database'], topic, 'urls.txt'), 'w',
            'utf-8') as writer:
        for fn_, url in seeds:
            writer.write('%s,%s\n' % (fn_, url.replace('\n', '')))
    crawler.start(seeds)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        params = Utils.parse_params(sys.argv[1])
        keywords = Utils.parse_keywords(sys.argv[2])

        engines = []
        if int(params.get('use_bing', 0)) == 1:
            engines.append(Bing())

        if int(params.get('use_google', 0)) == 1:
            engines.append(Google())

        if int(params.get('use_flickr', 0)) == 1:
            engines.append(Flickr(params))

        if int(params.get('use_500px', 0)) == 1:
            engines.append(Fivepx(params))

        if int(params.get('use_getty', 0)) == 1:
            engines.append(Getty(params))

        if int(params.get('use_getty_api', 0)) == 1:
            engines.append(GettyApi(params))

        namedict = {u'眼镜男': 'glass_man', u'眼镜女': 'glass_woman'}

        p = Pool(4)
        for keyword in keywords:
            if keyword in namedict.keys():
                name = namedict[keyword]
            else:
                name = 'url'  # default put url in table 'url'
            p.apply_async(
                run_proc, args=(
                    name,
                    keyword,
                    params,
                    engines,
                ))
        p.close()
        p.join()
        print('All subprocess done.')

    else:
        print('Usage : python QueryKeywords.py PARAMS_CFG KEY_WORDS_LIST')
        # PARAMS_CFG params' file name
        # KEY_WORDS_LIST key_words_list's file name
