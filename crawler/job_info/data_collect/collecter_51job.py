# coding=utf-8
import requests
import lxml.etree as etree
import str.str_util as strutil
from crawler.job_info.util.model_items import JobInfo
import crawler.job_info.util.crawler_util as crawler_util
import time
import traceback
extra_company_name = crawler_util.get_extra_company_array()
exit_url_array = crawler_util.get_exit_job_url()
company_new_job = []

# 职位详情中各属性的xpath表达式
NAME_XPATH_IN_INFO_PAGE = '//div[@class="tHeader tHjob"]/div/div[1]/h1/text()'
PAY_XPATH_IN_INFO_PAGE = '//div[@class="tHeader tHjob"]/div/div[1]/strong/text()'
ADDRESS_XPATH_IN_INFO_PAGE = '//div[@class="tHeader tHjob"]/div/div[1]/span/text()'
EXP_XPATH_IN_INFO_PAGE = '//div[@class="tCompany_main"]/div[@class="tBorderTop_box bt"]/div[@class="jtag inbox"]/div[@class="t1"]/span[1]/text()'
EDUCATION_XPATH_IN_INFO_PAGE = '//div[@class="tCompany_main"]/div[@class="tBorderTop_box bt"]/div[@class="jtag inbox"]/div[@class="t1"]/span[2]/text()'
DES_XPATH_IN_INFO_PAGE = '//div[@class="tCompany_main"]/div[@class="tBorderTop_box"]/div[@class="bmsg job_msg inbox"]/p'
COMPANY_NAME_XPATH_IN_INFO_PAGE = '//div[@class="tHeader tHjob"]/div/div[1]/p[@class="cname"]/a/@title'
COMPANY_TYPE_XPATH_IN_INFO_PAGE = '//div[@class="tHeader tHjob"]/div/div[1]/p[@class="msg ltype"]/text()'
PUBLISH_TIME_XPATH_IN_INFO_PAGE = '//div[@class="tCompany_main"]/div[@class="tBorderTop_box bt"]/div[@class="jtag inbox"]/div[@class="t1"]/span[4]/text()'
PUBLISH_3_TIME_XPATH_IN_INFO_PAGE = '//div[@class="tCompany_main"]/div[@class="tBorderTop_box bt"]/div[@class="jtag inbox"]/div[@class="t1"]/span[3]/text()'

headers = {
                'Referer':'https://www.51job.com/',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            }

url_count = 0
parse_url_count = 0

# 获取智联招聘中的职位链接
def get_job_in_51job(job ='java'):
    url_jobs = []
    for page in range(199):
        page_num = str(page + 1)  # 爬取的页码
        url = "http://search.51job.com/list/010000,000000,0000,00,2,99,java,2," + page_num +\
              ".html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=1&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
        parse_job_base_info(url)  # 获得招聘页面源码
    print "* 51job累计爬取" + str(url_count) + "条信息，处理" + str(parse_url_count) + "条"
    return url_jobs

def parse_job_base_info(url):
    r = requests.get(url, headers=headers)  # 发送请求
    time.sleep(1)
    job_html = r.text.encode('iso-8859-1').decode('gbk')
    selector = etree.HTML(job_html)  # 获得招聘页面源码
    # 职位的基本信息
    job_base_divs = selector.xpath('//div[@id="resultList"]/div[@class="el mk"]')  # 匹配到的职业名称
    job_base_divs.extend(selector.xpath('//div[@id="resultList"]/div[@class="el"]'))
    if len(job_base_divs) != 54 and len(job_base_divs) != 50:
        print "ERROR：查询url仅抓取到"+str(len(job_base_divs))+"条数据："+url
    for job_base_div in job_base_divs:
        global url_count
        url_count += 1
        # 获得职位信息的节点
        job_href = job_base_div.xpath('p/span/a/@href')
        company_name = job_base_div.xpath('span[1]/a/@title')
        if job_href is not None and len(job_href) > 0:
            job_href = strutil.unicode_to_utf8(job_href[0])
            if job_href.startswith('//'):
                job_href = 'http:'+job_href
            if company_name is not None and len(company_name) > 0:
                company_name = strutil.unicode_to_utf8(company_name[0]).replace(' ','')
        # 如果公司在忽略公司的列表里面，则忽略该职位
        if company_name in extra_company_name:
            continue
        elif job_href in exit_url_array:
            continue
        else:
            parse_job_info_from_url(job_href)

#根据职位url获取职位对象
def parse_job_info_from_url(job_url):
    job_item = JobInfo()
    job_item.url = str(job_url)
    try:
        response = requests.post(job_url,headers=headers)  # 发送post请求
        time.sleep(1)
        job_html = response.text.encode('iso-8859-1').decode('gbk')
        selector = etree.HTML(job_html)  # 获得招聘页面源码
        # 职位相关的信息
        name = selector.xpath(NAME_XPATH_IN_INFO_PAGE)  # 匹配到的职业名称
        # 公司名称
        company_name = selector.xpath(COMPANY_NAME_XPATH_IN_INFO_PAGE)
        # 如果公司在忽略列表中，则不保存其职位信息
        if company_name is not None and len(company_name) > 0:
            job_item.company_name = strutil.unicode_to_utf8(company_name[0]).replace(' ', '')
        if job_item.company_name in extra_company_name:
            return None
        # 匹配到该职位的月薪
        pay = selector.xpath(PAY_XPATH_IN_INFO_PAGE)
        # 匹配工作的地址
        address = selector.xpath(ADDRESS_XPATH_IN_INFO_PAGE)
        # 发布时间
        publish_time = selector.xpath(PUBLISH_TIME_XPATH_IN_INFO_PAGE)
        if publish_time is None or len(publish_time) == 0:
            publish_time = selector.xpath(PUBLISH_3_TIME_XPATH_IN_INFO_PAGE)
        # 匹配要求的工作经验
        exp = selector.xpath(EXP_XPATH_IN_INFO_PAGE)
        # 匹配最低学历
        education = selector.xpath(EDUCATION_XPATH_IN_INFO_PAGE)
        # 公司性质
        company_type = selector.xpath(COMPANY_TYPE_XPATH_IN_INFO_PAGE)
        if company_type  is not None and len(company_type) > 0:
            company_type[0] = company_type[0].strip().replace('\t','').replace('\r\n','').replace(' ','')
            company_type[0] = company_type[0].split('|')[0]

        # 职位描述
        dess = selector.xpath(DES_XPATH_IN_INFO_PAGE)
        job_des = ''
        for des in dess:
            if des.xpath('text()') is not None and len(des.xpath('text()')) > 0:
                job_des = job_des + strutil.unicode_to_utf8(des.xpath('text()')[0])

        job_des = crawler_util.filter_tags(job_des)  # filter_tags此函数下面会讲到
        job_des = job_des.strip()
        job_des = job_des.replace('&nbsp;', '')
        job_des = job_des.rstrip('\n')
        job_des = job_des.strip(' \t\n')
        job_item.des = job_des

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
        if company_type is not None and len(company_type) > 0:
            job_item.company_type = strutil.unicode_to_utf8(company_type[0]).replace(' ','')
        if publish_time is not None and len(publish_time) > 0:
            job_item.publish_time = strutil.unicode_to_utf8(publish_time[0])
            if not job_item.publish_time.startswith("201"):
                job_item.publish_time = "2018-" + job_item.publish_time
            if job_item.publish_time.endswith("发布"):
                job_item.publish_time = job_item.publish_time[0: -6]

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
    job_urls = get_job_in_51job(job)
