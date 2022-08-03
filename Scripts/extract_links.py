# -*- coding:utf-8 -*-
#====#====#====#====
# __author__ = "liubc"
#FileName: Reference_Identification.py
#Version:1.0.0
#CreateTime:xxxx-xx-xx
#====#====#====#====
import re
from pymongo import MongoClient


global SIGN
SIGN = False

'''
function:extract links in Bson files from ghtorrent
'''
def link_extraction():
    # connect MongoDB database
    client = MongoClient(unicode_decode_error_handler='ignore')
    db = client.ghtorrent
    # open collection
    coll_input = db['input']
    # new collection
    coll_output = db['output']

    # Building regular expression
    target1 = 'github.com/(.+?)/(.+?)'
    target2 = '(.+?)/(.+?)#(\d+)'
    target3 = '(.+?)/(.+?)@([a-zA-Z0-9]+)'
    # pre-compile
    pattern1 = re.compile(target1)
    pattern2 = re.compile(target2)
    pattern3 = re.compile(target3)
    patterns = (pattern1, pattern2, pattern3)
    i = 0
    pattern_num = 0
    lenmax = len(patterns)
    while pattern_num < lenmax:
        pattern = patterns[pattern_num]
        for cursor in coll_input.find({'body': {'$regex': pattern}}, no_cursor_timeout=True, batch_size=1000):
            d = {}
            SIGN = False
            str_body = cursor['body']
            sign_num = pattern_num + 1
            idx = 0
            list_body = str_body.split()
            for str_full in list_body:
                num_re = -1
                if sign_num == 1:
                    num_re = str_full.find('github.com')
                elif sign_num == 2:
                    if (str_full.find('github.com')) == -1:
                        num_re = str_full.find('#')
                    else:
                        continue
                elif sign_num == 3:
                    if (str_full.find('github.com')) == -1:
                        num_re = str_full.find('@')
                    else:
                        continue
                else:
                    continue
                if num_re != -1:
                    try:
                        d = AnalysisData(str_full, sign_num, idx, d)
                        idx = idx + 1
                    except:
                        continue
            if SIGN:
                # extract information
                d['type'] = sign_num
                d['sourceId'] = cursor['_id']
                d['updated_at'] = cursor['updated_at']
                # pull_request_comments
                d['_links'] = cursor['_links']
                sourceRepo = cursor['repo']
                sourceUser = cursor['owner']
                d['source_org'] = sourceUser + '/' + sourceRepo
                coll_output.insert_one(d)
                i = i + 1
        pattern_num = pattern_num + 1
    return

def AnalysisData(str_full, sign_num, idx, d):
    global SIGN
    if sign_num == 1:
        list_http = str_full.split("/")
        num_len = len(list_http)
        i = 0
        while i < num_len:
            str_tmp = list_http[i]
            sum_tmp = str_tmp.find('github.com')
            sum_api = str_tmp.find('api.github.com')
            if sum_tmp != -1:
                if (sum_api == -1) and (num_len > i + 2):
                    SIGN = True
                    usr = list_http[i + 1]
                    repo = list_http[i + 2]
                    num_idx = '%d' % idx
                    d['target_org' + num_idx] = usr + '/' + repo
                    d['sample' + num_idx] = str_full
                    break
                elif (sum_tmp != -1) and (num_len > i + 3):
                    SIGN = True
                    usr = list_http[i + 2]
                    repo = list_http[i + 3]
                    num_idx = '%d' % idx
                    d['target_org' + num_idx] = usr + '/' + repo
                    d['sample' + num_idx] = str_full
                    break
            i = i + 1
    if sign_num == 2:
        list_j = str_full.split("#")
        if list_j:
            str_xg = list_j[0]
            list_xg = str_xg.split("/")
            if len(list_xg) > 1:
                SIGN = True
                usr = list_xg[-2]
                repo = list_xg[-1]
                num_idx = '%d' % idx
                d['target_org' + num_idx] = usr + '/' + repo
                d['sample' + num_idx] = str_full
    if sign_num == 3:
        list_j = str_full.split("@")
        if list_j:
            str_xg = list_j[0]
            list_xg = str_xg.split("/")
            if len(list_xg) > 1:
                SIGN = True
                usr = list_xg[-2]
                repo = list_xg[-1]
                num_idx = '%d' % idx
                d['target_org' + num_idx] = usr + '/' + repo
                d['sample' + num_idx] = str_full
    return d