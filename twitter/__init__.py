#coding: utf8
import StringIO
import re
import urllib
import pycurl

class Twitter:
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookie_file = username + '.twitter_cookie'
        self.b = StringIO.StringIO()
        self.c = pycurl.Curl()
        self.reset()
    
    def reset(self):
        b = self.b
        c = self.c
        b.truncate()
        c.reset()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        return b,c
        
    def login(self):
        b, c = self.reset()
        c.setopt(pycurl.COOKIEJAR, self.cookie_file)
        c.setopt(pycurl.URL, "https://mobile.twitter.com/session/new")
        c.setopt(pycurl.REFERER, 'http://mobile.twitter.com/')
        c.setopt(pycurl.USERAGENT, 'Opera/9.60')
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.perform()
        m = re.search('''name="authenticity_token" .*?value="([^"]+?)"''', b.getvalue())
        self.authenticity_token = m.group(1)
        print self.authenticity_token
        
        b, c = self.reset()
        c.setopt(pycurl.COOKIEJAR, self.cookie_file)
        c.setopt(pycurl.URL, "https://mobile.twitter.com/session")
        c.setopt(pycurl.REFERER, "https://mobile.twitter.com/session/new")
        c.setopt(pycurl.USERAGENT, 'Opera/9.60')
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.setopt(pycurl.POST, True)
        c.setopt(pycurl.POSTFIELDS, urllib.urlencode({
            'authenticity_token': self.authenticity_token,
            'username': self.username,
            'password': self.password,
        }))
        c.perform()
        return b.getvalue()
        
    def update(self, status):
        b, c = self.reset()
        c.setopt(pycurl.COOKIEJAR, self.cookie_file)
        c.setopt(pycurl.URL, "http://mobile.twitter.com/")
        c.setopt(pycurl.REFERER, "http://mobile.twitter.com/")
        c.setopt(pycurl.USERAGENT, 'Opera/9.60')
        c.setopt(pycurl.POST, True)
        c.setopt(pycurl.FOLLOWLOCATION, True)
        c.setopt(pycurl.POSTFIELDS, urllib.urlencode({
            'authenticity_token': self.authenticity_token,
            'tweet[text]': status,
        }))
        c.perform()
        return b.getvalue()



def get_twitter_status(username, prevtime):
    import sys
    sys.path.append('..')
    from lib import *
    from datetime import datetime
    ptime = datetime.strptime(prevtime, '%a, %d %b %Y %H:%M:%S +0000')
    url = 'http://twitter.com/statuses/user_timeline/%s.rss' %  username
    data = fetch(url)
    if not data:
        return []
    from xml.dom import minidom
    try:
        tree = minidom.parseString(data)
    except:
        return []
    desc = tree.getElementsByTagName('description')[1:]
    date = tree.getElementsByTagName('pubDate')
    
    statuses = []
    lst = range(len(desc))
    lst.reverse()
    prefix = '%s: ' % username
    prefix_len = len(prefix)
    for i in lst:
        try:
            status = decodeHtmlentities(mb_code(desc[i].childNodes[0].data))
            if status.startswith(prefix): status = status[prefix_len:]
        except: continue
        pubdate = date[i].childNodes[0].data
        if datetime.strptime(pubdate , '%a, %d %b %Y %H:%M:%S +0000') > ptime:
            statuses.append((status, pubdate))
    
    return statuses