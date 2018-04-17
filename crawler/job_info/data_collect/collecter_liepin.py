# coding=utf-8
import lxml.etree as etree
import str.StrUtil as strutil
from crawler.job_info.util.model_items import JobInfo
import crawler.job_info.util.crawler_util as crawler_util
from bs4 import BeautifulSoup
import requests
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')

extra_company_name = crawler_util.get_extra_company_array()
exit_url_array = crawler_util.get_exit_job_url()
company_new_job = []

headers = {
                'Referer':'https://www.liepin.com/',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            }

url_count = 0
parse_url_count = 0

# 获取智联招聘中的职位链接
def get_job_url_in_zhilian(job = 'java'):
    url_jobs = []
    # 先查询国企
    for page in range(199):
        company_type_pre = u'猎聘'
        # java+北京+近七天
        url = 'https://www.liepin.com/zhaopin/?pubTime=7&ckid=5ac323b614701474&fromSearchBtn=2&compkind=&isAnalysis=&init=-1&searchType=1&dqs=010' \
              '&industryType=&jobKind=2&sortFlag=15&degradeFlag=0&industries=&salary=&compscale=&key=%s&clean_condition=&headckid=5ac323b614701474&curPage=%d' % (
            job, page)
        parse_job_base_info_result(url, company_type_pre)  # 获得招聘页面源码
    print "* 猎聘累计爬取" + str(url_count) + "条信息，处理" + str(parse_url_count) + "条"
    return url_jobs


def parse_job_base_info_result(url, company_type_pre):
    r = requests.get(url, headers=headers)  # 发送请求
    time.sleep(1)
    job_html = r.text
    selector = etree.HTML(job_html)  # 获得招聘页面源码
    # 职位的基本信息
    job_base_divs = selector.xpath('//div[@class="container"]/div[@class="wrap"]/div[@class="job-content"]/div[@class="sojob-result "]/ul[@class="sojob-list"]/li')  # 匹配到的职业名称
    if len(job_base_divs) != 40:
        print "ERROR：查询url仅抓取到"+str(len(job_base_divs))+"条数据："+url
    for job_base_div in job_base_divs:
        global url_count
        url_count += 1
        # 获得职位信息的节点
        job_href = job_base_div.xpath('div[@class="sojob-item-main clearfix"]/div[@class="job-info"]/h3/a/@href')
        company_name = job_base_div.xpath('div[@class="sojob-item-main clearfix"]/div[@class="company-info nohover"]/p/a/text()')
        if job_href is not None and len(job_href) > 0:
            job_href = strutil.unicode_to_utf8(job_href[0])
            if job_href[0] == '/':
                job_href = 'https://www.liepin.com' + job_href
            if company_name is not None and len(company_name) > 0:
                company_name = strutil.unicode_to_utf8(crawler_util.remove_all_blank(company_name[0]))
        # 如果公司在忽略公司的列表里面，则忽略该职位
        if company_name in extra_company_name:
            continue
        elif job_href in exit_url_array:
            continue
        else:
            get_job_item_from_url(job_href, company_type_pre)

#根据职位url获取职位对象
def get_job_item_from_url(job_url, company_type_pre):
    job_item = JobInfo()
    job_item.url = str(job_url)
    try:
        response = requests.post(job_url,headers=headers)  # 发送post请求
        time.sleep(1)
        job_html = response.text
        job_html = job_html[job_html.index('<!DOCTYPE html>'): len(job_html)]
        bs2 = BeautifulSoup(job_html, "lxml")

        title_info = bs2.find('div', class_='title-info')
        # 职位相关的信息
        name = title_info.find('h1').text
        # 公司名称
        company_name = u'猎头-'
        if title_info.find('h3').find('a') is not None:
            company_name= title_info.find('h3').find('a').text
        else:
            company_name= title_info.find('h3').text
        job_info = bs2.find('div', class_='job-item')
        # 匹配到该职位的月薪
        job_title_left = bs2.find('div',class_='job-title-left')
        pay = 'UNKNOWN'
        if job_title_left.find('p',class_='job-item-title')  is not None:
            pay = job_title_left.find('p', class_='job-item-title').contents[0].strip()
        else:
            pay = job_title_left.find('p', class_='job-main-title').contents[0].strip()

        # 匹配工作的地址
        address = u'北京'
        try:
            address = job_title_left.find('p',class_='basic-infor').find('a').text
        except Exception as e:
            address = job_title_left.find('p',class_='basic-infor').find_all('span')[0].text

        # 发布时间
        publish_time = '3333'
        try:
            publish_time = job_title_left.find('p',class_='basic-infor').find('time')['title']
        except Exception as e:
            publish_time = job_title_left.find('p', class_='basic-infor').find_all('span')[1].text

        # 匹配要求的工作经验
        exp = ''
        education = ''
        if job_title_left.find('div',class_='job-qualifications') is not None:
            exp = job_title_left.find('div',class_='job-qualifications').find_all('span')[1].text
            education = job_title_left.find('div',class_='job-qualifications').find_all('span')[0].text
        else:
            exp = job_title_left.find('div').find_all('span')[1].text
            education = job_title_left.find('div').find_all('span')[0].text
        # 公司性质
        company_type = u'猎头'
        try:
            company_type = bs2.find('div',class_='side').find('ul',class_='new-compintro').find('li').text
        except Exception as e:
            try:
                company_type = bs2.find('div',class_='side').find('div',class_='publisher-infor').find_all('p')[-1].text
            except Exception as e:
                company_type = u'猎头'
        company_type = strutil.unicode_to_utf8(company_type)
        if '上市' in company_type:
            company_type = company_type_pre + u'-上市公司'
        elif '股份' in company_type:
            company_type = company_type_pre + u'-股份制企业'
        elif '国企' in company_type:
            company_type = u'国企'
        else:
            company_type = company_type_pre + u'-其他'
        # 职位描述
        job_des = u''
        if bs2.find('div',class_='job-item main-message job-description') is not None:
            job_des = bs2.find('div',class_='job-item main-message job-description').find('div',class_='content content-word').text
        elif bs2.find('div',class_='job-item main-message') is not None:
            job_des = bs2.find('div',class_='job-item main-message').find('div',class_='content content-word').text

        job_item.name = strutil.unicode_to_utf8(crawler_util.remove_all_blank(name))
        job_item.company_name = strutil.unicode_to_utf8(crawler_util.remove_all_blank(company_name))
        job_item.company_type = strutil.unicode_to_utf8(crawler_util.remove_all_blank(company_type))
        job_item.publish_time = strutil.unicode_to_utf8(crawler_util.remove_all_blank(publish_time))
        job_item.address = strutil.unicode_to_utf8(crawler_util.remove_all_blank(address))
        job_item.des = strutil.unicode_to_utf8(crawler_util.remove_all_blank(job_des).replace('\'',''))
        job_item.education = strutil.unicode_to_utf8(crawler_util.remove_all_blank(education))
        job_item.exp = strutil.unicode_to_utf8(crawler_util.remove_all_blank(exp))
        job_item.pay = strutil.unicode_to_utf8(crawler_util.remove_all_blank(pay))
        job_item.url = strutil.unicode_to_utf8(crawler_util.remove_all_blank(job_url))

        # 增加每个招聘信息获取后结束后存储数据库的操作
        sql = crawler_util.gen_insert_item_sql(job_item, 'job_data')
        crawler_util.execute_sql(sql)
        crawler_util.insert_conpany_info(job_item, company_new_job)
        exit_url_array.append(job_item.url)
        global parse_url_count
        parse_url_count += 1
        print "SUCCESS：录入" + str(job_url) + "的职位信息！"
    except Exception as e:
        print ''
        print "ERROR：录入" + str(job_url) + "的职位信息！"
        print e
    finally:
        return job_item


if __name__=='__main__':
    job = 'java'  # 以爬取java工程师职业为例
    job_urls = get_job_url_in_zhilian(job)
