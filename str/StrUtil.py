# coding=utf-8

def unicode_to_utf8(unicodestring):
    return unicodestring.encode("utf-8")

def gbk_to_utf8(gbkstring):
    return gbkstring.decode('gbk').encode("utf-8")
