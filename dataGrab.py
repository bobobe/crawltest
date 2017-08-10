#encoding:utf-8
from crawltest import *;
import re;
from bs4 import BeautifulSoup
import lxml.html
from lxml.cssselect import CSSSelector
import time;
import csv;
#使用网页:http://example.webscraping.com/places/default/view/Albania-3
#抓取字段
key = ["places_national_flag__row",
    "places_area__row",
    "places_population__row",
    "places_iso__row",
    "places_country__row",
    "places_capital__row",
    "places_continent__row",
    "places_tld__row",
    "places_currency_code__row",
    "places_currency_name__row",
    "places_phone__row",
    "places_postal_code_format__row",
    "places_postal_code_regex__row",
    "places_languages__row",
    "places_neighbours__row"];

#获取网页数据的三种方式
def regexTest():#1正则表达式模式
    url = 'http://example.webscraping.com/places/default/view/Albania-3'
    html = download(url);
    list = re.findall('<tr id="places_country__row"><td class="w2p_fl">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>',html);#使用非贪婪模式
    print list;

def regexTest1():#获取示例国家所有的属性值
    url = 'http://example.webscraping.com/places/default/view/Albania-3'
    html = download(url);
    list = re.findall('<tr id="places_.*?__row">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>',html);
    #print list;
    all_list={};
    for i in range(len(key)):
        all_list[key[i]] = list[i];
    return all_list;

def bs4Test():#2使用BeautifulSoup4模块
    broken_html = '<ul class = country><li>Area<li>Population</ul>'
    soup = BeautifulSoup(broken_html,'html5lib');#将html文件解析成soup文档
    fixed_html = soup.prettify();#修复错误的html格式
    ul = soup.find('ul',attrs = {'class':'country'});
    print ul.find('li');
    print ul.find_all('li');#返回一个列表

def bs4Test1():#获取示例国家面积
    url = 'http://example.webscraping.com/places/default/view/Albania-3';
    html = download(url);
    soup = BeautifulSoup(html,'html5lib');
    fixed_html = soup.prettify();
    tr = soup.find(attrs = {'id':'places_area__row'});
    area = tr.find(attrs = {'class':'w2p_fw'});
    print area.text;#得到标签里的内容

def bs4Test2():#获取示例国家所有信息
    url = 'http://example.webscraping.com/places/default/view/Albania-3';
    html = download(url);
    soup = BeautifulSoup(html,'html5lib');
    fixed_html = soup.prettify();
    tr = soup.find_all('tr');
    all_list = {};
    for i in range(len(tr)):
        value = tr[i].find(attrs = {'class':'w2p_fw'}).text;
        all_list[key[i]] = value;
    return all_list;


def lxmlTest():#使用lxml模块
    broken_html = '<ul class = country><li>Area<li>Population</ul>'
    tree = lxml.html.fromstring(broken_html);#解析
    fixed_html = lxml.html.tostring(tree,pretty_print = True);
    print fixed_html;

def lxmlTest1():#获取示例国家面积
    url = 'http://example.webscraping.com/places/default/view/Albania-3';
    html = download(url);
    tree = lxml.html.fromstring(html);#解析
    td = tree.cssselect('tr#places_area__row>td.w2p_fw')[0];#css选择器语法直接百度即可
    print td.text_content();

def lxmlTest2():#获取示例国家的所有信息
    url = 'http://example.webscraping.com/places/default/view/Albania-3';
    html = download(url);
    tree = lxml.html.fromstring(html);#解析
    all_list = {};
    for k in key:
        all_list[k] = tree.cssselect('tr#%s > td.w2p_fw'%k)[0].text_content();
    return all_list;

def compare3():#比较三种模块的速度
    num_iter  = 10;
    #url = 'http://example.webscraping.com/places/default/view/Albania-3';
    for name,model in [('Regular expressions',regexTest1),
    ('BeautifulSoup',bs4Test2),
    ('Lxml',lxmlTest2)]:

        throttle = Throttle(2);
        url = 'http://example.webscraping.com/places/default/view/Albania-3';#限速标志
        start = time.time();
        for i in range(num_iter):
            throttle.wait(url);#限速
            if model == regexTest1:
                re.purge();
            result = model();
            assert(result['places_area__row'] == '28,748 square kilometres');#assert断言，如果为假则抛出异常
        end = time.time();

        print '%s:%.2f seconds' %(name,end-start);

def call_crawler(url,user_agent = 'test',max_depth = -1,call_back = None):#添加回调函数
    if not robot_parse(url,user_agent):#首先检查爬虫限制
        print trans_encode("禁止此用户爬取");
        return;
    max_depth = 2;#想要禁用搜索深度限制，只需设置该值为负数
    crawl_queue = [url];
    seen_url = {url:{'depth':0}};#字典存放已经遍历过的url的一些信息，目前只存放该url的深度（从源页面经过了几个页面）
    throttle = Throttle(2);#对同一域名下的网页，每2秒抓取一次
    while crawl_queue:
        url = crawl_queue.pop(0);#队列头出
        depth = seen_url[url]['depth'];
        if depth == max_depth:#超出链接深度则停止搜索
            continue;
        url = urlparse.urljoin('http://example.webscraping.com',url);#测试用
        throttle.wait(url);#限速
        html = download(url);
        if html is None:
            continue;
        urlList = [];
        if call_back:
            urlList.extend(call_back(url,html) or []);#这行其实就是为了回调函数，urllist不会增加元素，callback中只有写入文件操作，没有返回
        webpage = re.compile('<a[^>]+href=[]"\'](.*?)["\']',re.IGNORECASE);
        urlList = webpage.findall(html);
        for i in urlList:
            if i not in seen_url.keys():#避免重复搜索
                seen_url[i] = {'depth':depth+1};#搜索深度+1
                crawl_queue.append(i);#队列尾进'''

def call_back(url,html):
    if re.search('/view/', url):
        tree = lxml.html.fromstring(html);
        row = [tree.cssselect('table > tr#%s > td.w2p_fw' %k)[0].text_content() for k in key]
        print url,row;

class call_back1:#回调类
    def __init__(self):
        self.writer = csv.writer(open('countries.csv','w'));
        self.fields = key[:];
        self.writer.writerow(self.fields);

    #call方法使类可以当函数使用，如call_back1(url,html),即调用的__call__方法，等效于a = call_back1();call_back1.__call__(url,html)
    #所以这样调用不是实例化类，而是调用方法。
    #所以__init__只执行了一次。即做为参数传到call_crawler中时(call_back = call_back1())
    #所以文件只打开一次，后来的写入都是在已打开的文件中写入
    def __call__(self,url,html):#特殊方法，调用此类时自动执行该方法
        if re.search('/view/', url):
            tree = lxml.html.fromstring(html);
            row = [tree.cssselect('table > tr#%s > td.w2p_fw' %k)[0].text_content() for k in self.fields];
            self.writer.writerow(row);
def test():
    call_crawler('http://example.webscraping.com',call_back = call_back1());
