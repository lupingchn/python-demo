# coding=utf-8

import time


class JobInfo(object):
    def __init__(self):
        self.name = 'UNKNOWN'
        self.company_name = 'UNKNOWN'
        self.company_type = 'UNKNOWN'
        self.pay = 'UNKNOWN'
        self.url = 'Null'
        self.exp = 'UNKNOWN'
        self.des = 'UNKNOWN'
        self.education = 'UNKNOWN'
        self.address = 'UNKNOWN'
        self.publish_time = 'UNKNOWN'
        self.collect_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


class CompanyInfo(object):
    def __init__(self):
        self.name = 'UNKNOWN'
        self.company_type = 'UNKNOWN'
        self.time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        self.site = 'UNKNOWN'