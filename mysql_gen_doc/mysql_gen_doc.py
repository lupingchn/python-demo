# coding=utf-8

import sys

reload(sys)
sys.setdefaultencoding('utf8')

from Mysql2docx import Mysql2docx

m = Mysql2docx()
m.do('127.0.0.1','root','123456','abs_mall',3306)