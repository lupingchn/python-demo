# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import data_collect.collecter_51job
import data_collect.collecter_liepin
import data_collect.collecter_zhilian

job = 'java'  # 以爬取java工程师职业为例

data_collect.collecter_51job.get_job_in_51job(job)
data_collect.collecter_zhilian.get_job_url_in_zhilian(job)
data_collect.collecter_liepin.get_job_url_in_zhilian(job)
