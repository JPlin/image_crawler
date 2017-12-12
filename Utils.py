import re
from PIL import Image
from io import BytesIO, StringIO

class Utils(object):
    QUERY_TIMEOUT = 15
    QUERY_MAX_TRAIL = 10
    QUERY_ERROR_CODE = ['SUCC', 'FAIL', 'SKIP']

    TOPIC_KEYWORDS = re.compile('(\w+\s?)+:(\w+\s?,?)')
    FLICKR_STATICU = re.compile('https?://\w+\.staticflickr\.com/(\w+/)+([0-9]+)_\w+\.\w+')

    HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36', 
               'accept-language':'en-US,en;q=0.8', 
			   'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' }

    def __init__(self, *args, **kwargs):
        return super(Utils, self).__init__(*args, **kwargs)

    @staticmethod
    def extract_flickr_id(url):
        res = re.match(Utils.FLICKR_STATICU, url)
        if res:
            return res.group(2)
        else:
            return None

    @staticmethod
    def parse_string(ln):
        ln = ln.strip()
        if not (ln.startswith('#') 
            or ln.isspace() 
            or not ln):
            return ln
        else:
            return None

    @staticmethod
    def parse_params(fn):
        params = dict()

        fb = open(fn, 'r')
        for ln in fb:
            ln = Utils.parse_string(ln)
            if ln:
                idx = ln.find(':')
                params[ln[:idx]] = r'%s'%ln[idx+1:]
        fb.close()

        return params

    @staticmethod
    def parse_keywords(fn):
        keywords = []
        fb = open(fn, 'r' ,encoding='utf-8')
        for ln in fb:
            ln = Utils.parse_string(ln)
            if ln:
                if re.match(Utils.TOPIC_KEYWORDS, ln):
                    idx = ln.find(':')
                    topic, items = ln[:idx], ln[idx+1:]
                    ln = [topic.strip()] + [x.strip() for x in items.split(',')]
                keywords.append(ln)
        fb.close()
        
        return keywords

    @staticmethod
    def printf(msg):
        sys.stdout.write(msg)

    @staticmethod
    def seperator(total, workers, start=0):
        num = total // workers
        rem = total % workers
        ins = [start] * (workers + 1)

        for n in range(1, workers + 1):
            ins[n] = ins[n - 1] + num
            if n <= rem:
                ins[n] += 1

        return ins

    @staticmethod
    def tellf(fn, itype=0):
        '''
        0 : buffer
        1 : file handler
        2 : file name
        '''
        if itype == 0:
            fn = BytesIO(fn)

        try:
            im = Image.open(fn)
        except:
            return None

        if im.format == 'JPEG':
            return im.size + ('jpg',)
        else:
            return im.size + (im.format.lower(), )
        