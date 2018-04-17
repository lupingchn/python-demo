# coding=utf-8
import sys
import os
from time import sleep


def ping(ip):
    os.system(ip)
    return 1


if __name__ == '__main__':
    count = 1
    while True:
        result = ping('ping 172.16.33.236')
        count += 1
        print count