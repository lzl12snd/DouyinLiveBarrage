#!/usr/bin/python
# coding:utf-8

# @FileName:    main.py
# @Time:        2024/1/2 22:27
# @Author:      bubu
# @Project:     douyinLiveWebFetcher

from douyinlivewebfetcher.liveMan import DouyinLiveWebFetcher

if __name__ == '__main__':
    live_id = '491840906442'
    DouyinLiveWebFetcher(live_id).start()
