#encoding:utf-8
import urllib2
import re;
import sys;
import robotparser;#解析robots.txt文件的模块
import urlparse;#用于连接url参数等等
import datetime;
import time;
type = sys.getfilesystemencoding();#获取当前系统编码，解决输出中文乱码问题
class Throttle:#对爬虫进行限速类
    def __init__(self,delay):
        self.delay = delay ;
        self.domains = {};#domains里每个键值对，存放域名和对应的上次访问时间
    def wait(self,url):
        domain = urlparse.urlparse(url).netloc;#提取域名
        last_accessed = self.domains.get(domain);

        if self.delay>0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now()-last_accessed).seconds;
            if sleep_secs>0:
                time.sleep(sleep_secs);
        self.domains[domain] = datetime.datetime.now();

def download(url,user_agent = 'wswp',proxy = None,num_try=3):#第二个参数是用户名,第三个参数是代理名
    print 'downloading:',url;
    headers = {'User_agent': user_agent};
    request = urllib2.Request(url,headers = headers);

    opener = urllib2.build_opener();
    if proxy:#如果使用代理
        proxy_params = {urlparse.urlparse(url).scheme:proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params));
    try:#可能会出现页面不存在等异常
        html = opener.open(request).read();
        #html = urllib2.urlopen(request).read();
    except urllib2.URLError as e:
        print 'Download error',e.reason
        html = None;
        if num_try > 0:
            #如果返回的错误码是5××，说明是服务器错误，那么我们可以一直尝试下载，等待服务器恢复
            if hasattr(e,'code') and 500 <= e.code <600:
                print 'error_code:',e.code;
                return download(url,user_agent,num_try - 1)
    mess ='下载完毕'
    print trans_encode(mess);
    return html;

def trans_encode(mess):
    return mess.decode('UTF-8').encode(type);#换成当前系统编码,使其能输出中文

def write(data):#写入文件
    f = open('data.txt','w');
    f.write(data);
    f.close();

def crawl_sitemap(url):
    sitemap = download(url);
#用正则表达式找到<loc>标签中的所有地址
    links = re.findall('<loc>(.*?)</loc>',sitemap);
#下载每个地址的页面
    for link in links:
        html = download(link);
        print html;

def cyc_crawl():#按照网页索引参数循环抓取
    max_errs = 5;
    cur_errs = 0;
    for i in range(100):
        url = 'http://example.webscraping.com/view/%d'%(i+1);#类似php sql语句的语法
        html = download(url)
        if html is None:
            cur_errs += 1;
            if cur_errs == max_errs:#连续出现5次下载失败则退出
                break;
        else:
            cur_errs = 0;

def link_crawl(url):#链接爬虫，即通过页面的url不断爬取(简单递归版本（栈）)
    html = download(url);
    if html is None:
        return ;
    webpage = re.compile('<a[^>]+href=[]"\'](.*?)["\']',re.IGNORECASE);
    urlList = webpage.findall(html);
    for i in urlList:
        link_crawl(i);

def link_crawl1(url,user_agent = 'test',max_depth = -1):#利用队列(先进先出)&&改进:已下载过的页面不会重复下载
    if not robot_parse(url,user_agent):#首先检查爬虫限制
        print trans_encode("禁止此用户爬取");
        return;
    max_depth = -1;#想要禁用搜索深度限制，只需设置该值为负数
    crawl_queue = [url];
    seen_url = {url:{'depth':0}};#字典存放已经遍历过的url的一些信息，目前只存放该url的深度（从源页面经过了几个页面）
    throttle = Throttle(2);#对同一域名下的网页，每2秒抓取一次
    while crawl_queue:
        url = crawl_queue.pop(0);#队列头出
        depth = seen_url[url]['depth'];
        if depth == max_depth:#超出链接深度则停止搜索
            continue;
        #url = urlparse.urljoin('http://example.webscraping.com',url);#测试用
        throttle.wait(url);#限速
        html = download(url);
        if html is None:
            continue;
        webpage = re.compile('<a[^>]+href=[]"\'](.*?)["\']',re.IGNORECASE);
        urlList = webpage.findall(html);
        for i in urlList:
            if i not in seen_url.keys():#避免重复搜索
                seen_url[i] = {'depth':depth+1};#搜索深度+1
                crawl_queue.append(i);#队列尾进

def robot_parse(url,user_agent):#解析robots.txt文件，看当前代理是否可以访问该网站，或查看哪些页面不能被爬取等等。
    rp = robotparser.RobotFileParser();#python中有专门解析robots文件的模块
    rp.set_url('http://example.webscraping.com/robots.txt');
    rp.read();#读取robots.txt文件
    return rp.can_fetch(user_agent,url);#true or false
