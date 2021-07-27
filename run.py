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
        print("+ [2] GET XML Items: {}".format(vul_Url))
        getDetails(vul_Url)
        
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
    description = getDescription(soup.find_all('div', class_ = 'container')[2])
    pubDate = soup.find('span', class_ = 'log-date').text
    pubDate = datetime.datetime.strptime(pubDate, '%Y/%m/%d %H:%M:%S').strftime(GMT_FORMAT)
    
    # PUT Vulnerability Details
    items.append(item(title, link, description, pubDate))

def getDescription(soup):
    text = ''
    sections = soup.find_all('section', class_ = "vul-detail-section")

    for i in range(2,len(sections)-3):
        h3 = sections[i].find('h3').text
        content = sections[i].find('div', class_ = 'section-content')
        text += r'<h3>{0}</h3>' \
                r'{1}' \
            .format(h3, content.prettify())

    # status = soup.find('ul', attrs={'id': 'vul-status-log-list'})
    # info = soup.find('div', class_ = 'section-content info')
    # reference = soup.find('div', class_ = 'section-content url')
    # url = soup.find('div', class_ = 'urls').string
    # narrate = soup.find_all('div', class_ = 'section-content zdui-md-content')[0]
    # # print(repair)
    # text = r'<h3>處理狀態</h3>' \
    #        r'{0}' \
    #        r'<h3>詳細資料</h3>' \
    #        r'{1}' \
    #        r'<h3>參考資料</h3>' \
    #        r'{2}' \
    #        r'<h3>相關網址</h3>' \
    #        r'{3}' \
    #        r'<h3>敘述</h3>' \
    #        r'{4}' \
    #     .format(status, info, reference, url, narrate)

    return text

def createRSS(channel, name):
    
    # XML Format - XML Channel
    rss_text = r'<rss ' \
               r'version="2.0" ' \
               r'encoding="UTF-8">' \
               r'<channel>' \
               r'<title>{}</title>' \
               r'<link>{}</link>' \
               r'<description>{}</description>' \
               r'<author>{}</author>' \
               r'<image>' \
               r'<url>{}</url>' \
               r'</image>' \
               r'<language>{}</language>' \
               r'<copyright>{}</copyright>' \
        .format(channel.title, channel.link, channel.description ,channel.author, channel.image, channel.language, channel.copyright)

    # XML Format - XML Items
    for item in items:
        rss_text += r'<item>' \
                    r'<title>{}</title>' \
                    r'<link>{}</link>' \
                    r'<description>{}</description>' \
                    r'<pubDate>{}</pubDate>' \
                    r'</item>' \
            .format(item.title, item.pubDate, item.description, item.link)

    rss_text += r'</channel></rss>'

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