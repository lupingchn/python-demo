# -*- coding: utf-8 -*-
import sys
import xlrd

from datetime import datetime
from xlrd import xldate_as_tuple

reload(sys)
sys.setdefaultencoding('utf8')

table_name = "test"
# replace_security_dict = {"119412": "669272",
#                          "119413": "669273",
#                          "119414": "669274",
#                          "119415": "669275",
#                          "119416": "669276",
#                          "119417": "669277",
#                          "119418": "669278",
#                          "119419": "669279",
#                          "119420": "669280",
#                          "119421": "669281",
#                          "119422": "669282",
#                          "119423": "669283",
#                          "119424": "669284",
#                          "119425": "669285",
#                          "119426": "669286",
#                          "119427": "669287",
#                          }

replace_security_dict = {"119412": "120773",
                         "119413": "120774",
                         "119414": "120775",
                         "119415": "120776",
                         "119416": "120777",
                         "119417": "120778",
                         "119418": "120779",
                         "119419": "120780",
                         "119420": "120781",
                         "119421": "120782",
                         "119422": "120783",
                         "119423": "120784",
                         "119424": "120785",
                         "119425": "120786",
                         "119426": "120787",
                         "119427": "120788",
                         }

title_row_index = 0
data_col_index = 1


def genSQLtxt(file="test_table_" + table_name + ".xls"):
    tables = excel_table(file)
    return


# 根据索引获取Excel表格中的数据
def excel_table(file):
    data = open_excel(file)
    xlssheet = data.sheet_by_index(0)
    for rowNum in range(title_row_index + 1, xlssheet.nrows):
        insert_str = "INSERT INTO abs_mall_" + table_name + "("
        value_str = "VALUES("
        for colNum in range(data_col_index, xlssheet.ncols):
            clo_str = str(xlssheet.cell(title_row_index, colNum).value)
            insert_str = insert_str + clo_str + ","
            value_item = getdate(xlssheet.cell(rowNum, colNum))
            if value_item == "" or value_item == "null" or value_item == "NULL":
                value_item = "null"
            else:
                value_item = "'" + value_item + "'"
            value_str = value_str + value_item + ","
        print insert_str[0:-1] + ")"
        print value_str[0:-1] + ");"
    return


def getdate(cell):
    ctype = cell.ctype  # 表格的数据类型
    value = cell.value
    if ctype == 2 and value % 1 == 0:  # 如果是整形
        value = str(int(value))
    elif ctype == 3:
        # 转成datetime对象
        date = datetime(*xldate_as_tuple(value, 0))
        value = str(date.strftime('%Y/%m/%d %H:%M:%S'))
    elif ctype == 4:
        value = str(True) if value == 1 else str(False)
    else:
        value = str(value)
    if value in replace_security_dict.keys():
        value = replace_security_dict[value]
    return value


def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception, e:
        print str(e)


if __name__ == "__main__":
    genSQLtxt()
