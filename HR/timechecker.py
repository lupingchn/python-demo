# -*- coding: utf-8 -*-
import xdrlib
import sys
import xlrd
import re

import xlwt
import datetime as dt

reload(sys)
sys.setdefaultencoding('utf8')

def genSQLtxt(file = "1.xls", isNeedDelete = False):
    tables = excel_table(file)
    return

#根据索引获取Excel表格中的数据
def excel_table(file):
    data = open_excel(file)
    newdata = xlwt.Workbook()
    sheet1 = newdata.add_sheet(u'sheet1',cell_overwrite_ok=True)
    xlssheet = data.sheet_by_index(0);
    style = set_style('Times New Roman', 220, True, 4)
    style2 = set_style('Times New Roman', 220, True , 5)
    errorsize = 0
    for rowNum in range(1,xlssheet.nrows):
        nameindex = 0;
        starttimeindex = 2;
        endtimeindex = 3;
        needrefresh = False;
        if (xlssheet.cell(rowNum, nameindex).value == xlssheet.cell(rowNum - 1, nameindex).value):
            lastdate = int(xlssheet.cell(rowNum - 1, endtimeindex).value)
            nowdate = int(xlssheet.cell(rowNum, starttimeindex).value)
            if (lastdate != nowdate and lastdate + 1 != nowdate):
                lasttime = getdate(xlssheet.cell(rowNum - 1, endtimeindex).value)
                nowtime = getdate(xlssheet.cell(rowNum, starttimeindex).value)
                if lasttime.year > 9000 or nowtime != lasttime + dt.timedelta(days = 1):
                    needrefresh = True;
                    errorsize = errorsize + 1
        if(needrefresh):
            sheet1.write(rowNum,2,xlssheet.cell(rowNum, starttimeindex).value,style2)
        else:
            sheet1.write(rowNum,2,xlssheet.cell(rowNum, starttimeindex).value,style)
    newdata.save('test.xls')
    print str(errorsize)
    return

def set_style(name, height, bold=False, clour = 4):
    style = xlwt.XFStyle()  # 初始化样式
    style.num_format_str = 'YYYY-M-D'
    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 4

    style.font = font
    if(clour != 4):
        pat = xlwt.Pattern()
        pat.pattern_fore_colour = 5
        pat.pattern_back_colour = 16
        pat.pattern = pat.SOLID_PATTERN
        style.pattern = pat

    return style

__s_date = dt.date (1899, 12, 31).toordinal() - 1
def getdate(date ):
    if isinstance(date , float ):
        date = int(date )
    d = dt.date .fromordinal(__s_date + date )
    return d

def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception,e:
        print str(e)

if __name__=="__main__":
    print genSQLtxt()