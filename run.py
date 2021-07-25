import requests, sys, datetime
from bs4 import BeautifulSoup

# GMT Format
GMT_FORMAT =  '%a, %d %b %Y %H:%M:%S GMT'

# PUT Vulnerability Details
items = []

# Page Count
pageCount = 0

# rss channel
class channel(object):

    def __init__(self, title, author, image, link, description, language, copyright):
        self.title = title
        self.author = author
        self.image = image
        self.link = link
        self.description = description
        self.language = language
        self.copyright = copyright

# rss item
class item(object):

    def __init__(self, title, pubDate, description, link):
        self.title = title
        self.link = link
        self.description = description
        self.pubDate = pubDate

def getChannel(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # GET XML Channel
    title = "HITCON ZeroDay - {}漏洞".format(soup.find('div', class_ = 'page-sub-title').text)
    author = soup.find('meta', attrs = {'name': 'author'}).get('content')
    image = "https://zeroday.hitcon.org{}".format(soup.find('link', attrs = {'rel': 'icon', 'sizes': '192x192', 'type': 'image/png'}).get('href'))
    link = soup.find('meta', attrs = {'property': 'og:url'}).get('content')
    description = soup.find('meta', attrs = {'name': 'description'}).get('content')
    language = soup.find('meta', attrs = {'property': 'og:locale'}).get('content')
    copyright = soup.find('meta', attrs = {'name': 'copyright'}).get('content')
    print("+ [1] GET XML Channel")
    return channel(title, author, image, link, description, language, copyright)

def getItem(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # GET Vulnerability List
    vulList = soup.find_all('li', class_ = 'strip')
    for list in vulList:
        vul_Url = "https://zeroday.hitcon.org{}".format(list.a['href'])
        getDetails(vul_Url)
        print("+ [2] GET XML Items")

    # Next Page
    global pageCount
    Nextpage = soup.find('a', class_ = 'pg-next')
    if Nextpage and pageCount <= 5:
        pageCount = pageCount + 1
        getItem("https://zeroday.hitcon.org{}".format(Nextpage.get('href')))
        
        

def getDetails(url):
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # GET Vulnerability Details
    title = soup.find('li', class_ = 'title')
    title = title.find('span', class_ = 'value').text
    link = url
    description = soup.find_all('div', class_ = 'container')[2]
    pubDate = soup.find('span', class_ = 'log-date').text
    pubDate = datetime.datetime.strptime(pubDate, '%Y/%m/%d %H:%M:%S').strftime(GMT_FORMAT)
    
    # PUT Vulnerability Details
    items.append(item(title, link, description, pubDate))

def createRSS(channel, name):
    
    # XML Format - XML Channel
    rss_text = r'<rss ' \
               r' version="2.0" ' \
               r' encoding="UTF-8"> ' \
               r' <channel>' \
               r' <title>{}</title>' \
               r' <link>{}</link>' \
               r' <description>{}</description>' \
               r' <author>{}</author>' \
               r' <image>' \
               r'  <url>{}</url>' \
               r' </image>' \
               r' <language>{}</language>' \
               r' <copyright>{}</copyright>' \
        .format(channel.title, channel.link, channel.description ,channel.author, channel.image, channel.language, channel.copyright)

    # XML Format - XML Items
    for item in items:
        rss_text += r' <item>' \
                    r'  <title>{}</title>' \
                    r'  <link>{}</link>' \
                    r'  <description>{}</description>' \
                    r'  <pubDate>{}</pubDate>' \
                    r' </item>'\
            .format(item.title, item.pubDate, item.description, item.link)

    rss_text += r' </channel></rss>'

    # Write File 
    FileName = "zeroday_{}.xml".format(name)
    with open(FileName, 'w', encoding = 'utf8') as f:
        f.write(rss_text)
        f.flush()
        f.close
    print("+ [3] GET XML File")

if __name__=="__main__":
    KEY = int(sys.argv[1])
    switch = {0 : "all", 1: "", 2: "patching", 3: "disclosed"}
    value = switch.get(KEY)
    url_ = "https://zeroday.hitcon.org/vulnerability/{}".format(value)

    # 1. Channel
    channel = getChannel(url_)
    # 2. Items
    getItem(url_)
    # 3. Create RSS
    createRSS(channel, value)