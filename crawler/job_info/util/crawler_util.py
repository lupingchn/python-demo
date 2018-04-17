# coding=utf-8

import pymysql
import re
from crawler.job_info.util.model_items import CompanyInfo
import time

# 获取数据库中已忽略的公司列表
def get_extra_company_array():
    company_name_array = []
    conn = pymysql.connect(host='192.168.168.168', user='root', passwd='123456', db='zhiye_data', port=3306,
                           charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute('select `name` from extra_company')
        results = cursor.fetchall()
        for row in results:
            name = row[0]
            company_name_array.append(name.encode('utf-8'))
        conn.commit()
    except Exception as e:
        print (e)
    cursor.close()
    conn.close()
    return company_name_array

# 获取数据库中已添加的url列表
def get_exit_job_url():
    url_array = []
    conn = pymysql.connect(host='192.168.168.168', user='root', passwd='123456', db='zhiye_data', port=3306,
                           charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute('select `url` from job_data')
        results = cursor.fetchall()
        for row in results:
            url = row[0]
            url_array.append(url.encode('utf-8'))
        conn.commit()
    except Exception as e:
        print (e)
    cursor.close()
    conn.close()
    return url_array

# 插入新职位的公司信息
def insert_conpany_info(job_item, conside_company):
    # 对于已插入数据库的公司不再重复插入
    if job_item.company_name not in conside_company:
        conside_company.append(job_item.company_name)
        company = CompanyInfo()
        company.name = job_item.company_name
        company.company_type = job_item.company_type
        company.site = "zhilian"
        result = execute_sql('select `name` from conside_company where name = \'' + company.name + '\'')
        if result is None or len(result) == 0:
            sql = gen_insert_item_sql(company, 'conside_company')
            result = execute_sql(sql)
        else:
            result = execute_sql('update conside_company SET time = \'' + time.strftime('%Y-%m-%d',time.localtime(time.time())) + '\' where name = \'' + company.name + '\'')
        conside_company.append(job_item.company_name)
        return result
    else:
        return None

def gen_insert_items_sql(job_items):
    item_sqls = ''
    for job_item in job_items:
        item_sql = gen_insert_item_sql(job_item, 'job_data')
        item_sqls = item_sqls + item_sql + '\n'
    item_sqls
    return item_sqls


def gen_insert_item_sql(job_item, table_name):
    sql_dict = {}
    sql_dict.update(job_item.__dict__)
    column_names = 'INSERT INTO `'+table_name+'` ('
    values = 'VALUES('
    for column_name in sql_dict.keys():
        column_names = column_names + '`' + column_name + '`,'
        values = values + '\'' + sql_dict.get(column_name) + '\','
    column_names = column_names[0: len(column_names) - 1] + ') '
    values = values[0: len(values) - 1] + ')'
    item_sql = column_names + values + ';'
    return item_sql

def execute_sql(sql):
    conn = pymysql.connect(host='192.168.168.168', user='root', passwd='123456', db='zhiye_data', port=3306,
                           charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.commit()
    except Exception as e:
        print (e)
    cursor.close()
    conn.close()
    return results


def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    #s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s = s.replace('\r','')
    s = s.replace('\n','')
    return s


def remove_all_blank(a):
    b = re.sub('\s','',a)
    return b