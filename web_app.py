from flask import Flask, request, render_template , jsonify
from geolite2 import geolite2
import urllib3.util.url as U_R_L
import socket
import re
import DB

app = Flask(__name__ )
table_dict = {
    'car' : u'车辆',
    'face' : u'人脸',
    'fire' : u'火源',
    'pacer' : u'行人'
}   # from chinese to english

urls = {} # the url of last record 
count = {} # the images num
area = {} # the region area

last_area = {'car':[0,0,0,0],'face':[0,0,0,0],'fire':[0,0,0,0],'pacer':[0,0,0,0]}
last_count = {'car':0,'face':0,'fire':0,'pacer':0}
last_urls = {'car':'','face':'' ,'fire':''  , 'pacer':'' }

@app.route('/', methods=['GET', 'POST'])
def home():
    urls.clear()
    count.clear()
    db = DB.DB()
    db.start()
    
    sum = 0
    for key in table_dict:
        count[key] = db.query_count(key)
        if int(count[key]) > 0:
            last_count[key] = count[key]
        sum += last_count[key]
    last_count['total'] = sum

    for key in table_dict:
        urls[key] = db.query_last(key)
        if urls[key] is not None:
            last_urls[key] = urls[key]
        loc = turn_ip_address(turn_url_ip(urls[key]))
        if loc is not None:
            area[key] = loc
            last_area[key] = area[key]

    db.commit()
    return render_template('index.html' , count = last_count , urls = last_urls , areas = last_area)


# turn the ip into relevant address
def turn_ip_address(ip = None):
    if ip == None:
        return
    try:
        reader = geolite2.reader()
        line = reader.get(ip)
        if line == None:
            return None
        return (line['country']['names']['en'],line['continent']['names']['en'],line['location']['latitude'],line['location']['longitude'])
    finally:
        geolite2.close()

# turn the url into relevant ip
def turn_url_ip(url = None):
    
    if url == None:
        return
    try:
        # sparse the host name
        parsed_url = U_R_L.parse_url(url)
        host = parsed_url.hostname
        ip = socket.gethostbyname(host)
        return ip
    except:
        print("url: %s is wrong!"%(url))

@app.route('/data')
def dataFromAjax():
    urls.clear()
    count.clear()
    db = DB.DB()
    db.start()
    
    sum = 0
    for key in table_dict:
        count[key] = db.query_count(key)
        if int(count[key]) > 0:
            last_count[key] = count[key]
        sum += last_count[key]
    last_count['total'] = sum

    for key in table_dict:
        urls[key] = db.query_last(key)
        if urls[key] is not None:
            last_urls[key] = urls[key]
        loc = turn_ip_address(turn_url_ip(urls[key]))
        if loc is not None:
            area[key] = loc
            last_area[key] = area[key]

    db.commit()
    data = {'count': last_count , 'url': last_urls , 'area':last_area}
    return jsonify(data)

if __name__ == '__main__':
    app.run()
    #print(turn_ip_address(turn_url_ip('http://pic2.ooopic.com/11/98/31/31bOOOPIC12_1024.jpg')))