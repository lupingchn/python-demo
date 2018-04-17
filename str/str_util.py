# coding=utf-8

import re

def unicode_to_utf8(unicodestring):
    return unicodestring.encode("utf-8")

def gbk_to_utf8(gbkstring):
    return gbkstring.decode('gbk').encode("utf-8")


def remove_all_blank(a):
    b = re.sub('\s','',a)
    return b