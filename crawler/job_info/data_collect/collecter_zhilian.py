# coding=utf-8
import requests
import re
import lxml.etree as etree
import str.str_util as strutil
from crawler.job_info.util.model_items import JobInfo
import crawler.job_info.util.crawler_util as crawler_util
import time

extra_company_name = crawler_util.get_extra_company_array()
exit_url_array = crawler_util.get_exit_job_url()
company_new_job = []

headers = {
                'Referer':'https://www.zhaopin.com/',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            }

url_count = 0
parse_url_count = 0

# 获取智联招聘中的职位链接
def get_job_url_in_zhilian(job = 'java'):
    for page in range(1, 200):
        url = "http://sou.zhaopin.com/jobs/searchresult.ashx?jl=北京&kw=" + job + "&p=" + str(page) + "&sm=0&sf=0&st=99999&isadv=1&pd=7"
        get_job_items_from_urls(url)  # 加入队列
    print "* 智联累计爬取" + str(url_count) + "条信息，处理" + str(parse_url_count) + "条"
    return url_count


# 根据职位的url列表获取职位对象列表
def get_job_items_from_urls(url):
    r = requests.get(url, headers=headers)  # 发送请求
    time.sleep(1)
    job_html = r.text
    selector = etree.HTML(job_html)  # 获得招聘页面源码
    # 职位的基本信息
    job_base_divs = selector.xpath('//div[@class="newlist_wrap fl"]/div[@id="newlist_list_div"]/div[@id="newlist_list_content_table"]/table')  # 匹配到的职业名称
    divs_length = len(job_base_divs)
    if divs_length != 61:
        print "ERROR：查询url仅抓取到"+str(len(job_base_divs))+"条数据："+url
    for index in range(1, divs_length):
        job_base_div = job_base_divs[index]
        global url_count
        url_count += 1
        # 获得职位信息的节点
        job_href = job_base_div.xpath('tr/td[@class="zwmc"]/div/a/@href')
        company_name = job_base_div.xpath('tr/td[@class="gsmc"]/a/text()')
        if job_href is not None and len(job_href) > 0:
            job_href = strutil.unicode_to_utf8(job_href[0])
            if job_href.startswith('//'):
                job_href = 'http:' + job_href
            if company_name is not None and len(company_name) > 0:
                company_name = strutil.unicode_to_utf8(company_name[0]).replace(' ', '')
        # 如果公司在忽略公司的列表里面，则忽略该职位
        if company_name in extra_company_name:
            continue
        elif job_href in exit_url_array:
            continue
        else:
            get_job_item_from_url(job_href)

#根据职位url获取职位对象
def get_job_item_from_url(job_url):
    job_item = JobInfo()
    job_item.url = str(job_url)
    try:
        response = requests.post(job_url,headers=headers)  # 发送post请求
        time.sleep(1)
        job_html = response.text
        selector = etree.HTML(job_html)  # 获得招聘页面源码
        # 职位相关的信息
        name = selector.xpath('//div[@class="inner-left fl"]/h1/text()')  # 匹配到的职业名称
        # 公司名称
        company_name = selector.xpath(
            '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-right"]/div[@class="company-box"]/p[2]/a/text()')
        if company_name is None or len(company_name) == 0:
            company_name = selector.xpath(
                '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-right"]/div[@class="company-box"]/p[1]/a/text()')
        # 如果公司在忽略列表中，则不保存其职位信息
        if company_name is not None and len(company_name) > 0:
            job_item.company_name = strutil.unicode_to_utf8(company_name[0]).replace(' ', '')
        if job_item.company_name in extra_company_name:
            return None
        # 匹配到该职位的月薪
        pay = selector.xpath(
            '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[1]/strong/text()')
        # 匹配工作的地址
        address = selector.xpath(
            '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[2]/strong/a/text()')
        # 发布时间
        publish_time = selector.xpath(
            '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[3]/strong/span/text()')
        # 匹配要求的工作经验
        exp = selector.xpath(
            '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[5]/strong/text()')
        # 匹配最低学历
        education = selector.xpath(
            '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[6]/strong/text()')
        # 匹配工作的地址
        zhaopin_num = selector.xpath(
            '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[7]/strong/a/text()')
        # 公司相关的信息
        # 公司性质
        company_type = selector.xpath(
            '//div[@class="terminalpage clearfix"]/div[@class="terminalpage-right"]/div[@class="company-box"]/ul[@class="terminal-ul clearfix terminal-company mt20"]/li[2]/strong/text()')
        match = re.compile('<!-- SWSStringCutStart -->(.*?)<!-- SWSStringCutEnd -->', re.S)  # 此处为匹配对职位的描述，并且对其结构化处理
        description = re.findall(match, job_html)
        des = ''
        if len(description) > 0:
            des = description[0]
        des = crawler_util.filter_tags(des)  # filter_tags此函数下面会讲到
        des = des.strip()
        des = des.replace('&nbsp;', '')
        des = des.replace('\'', '')
        des = des.rstrip('\n')
        des = des.strip(' \t\n')
        if name is not None and len(name) > 0:
            job_item.name = strutil.unicode_to_utf8(name[0])
        if pay is not None and len(pay) > 0:
            job_item.pay = strutil.unicode_to_utf8(pay[0])
        if address is not None and len(address) > 0:
            job_item.address = strutil.unicode_to_utf8(address[0])
        if exp is not None and len(exp) > 0:
            job_item.exp = strutil.unicode_to_utf8(exp[0])
        if education is not None and len(education) > 0:
            job_item.education = strutil.unicode_to_utf8(education[0])
        if des is not None and len(des) > 0:
            job_item.des = strutil.unicode_to_utf8(des)
        if company_type is not None and len(company_type) > 0:
            job_item.company_type = strutil.unicode_to_utf8(company_type[0])
        if publish_time is not None and len(publish_time) > 0:
            job_item.publish_time = strutil.unicode_to_utf8(publish_time[0])
        # 增加每个招聘信息获取后结束后存储数据库的操作
        sql = crawler_util.gen_insert_item_sql(job_item, 'job_data')
        crawler_util.execute_sql(sql)
        crawler_util.insert_conpany_info(job_item, company_new_job)
        exit_url_array.append(job_item.url)
        global parse_url_count
        parse_url_count += 1
        print "SUCCESS：录入" + str(job_url) + "的职位信息！"
    except Exception as e:
        print "ERROR：录入" + str(job_url) + "的职位信息！"
        print e
    finally:
        return job_item


if __name__=='__main__':
    job = 'java'  # 以爬取java工程师职业为例
    # get_job_item_from_url("http://jobs.zhaopin.com/479715135250003.htm")
    job_urls = get_job_url_in_zhilian(job)
