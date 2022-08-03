
# -*- coding:utf-8 -*-
#====#====#====#====
# __author__ = "liubc"
#FileName: Reference_Identification.py
#Version:1.0.0
#CreateTime:xxxx-xx-xx
#====#====#====#====

from pymongo import MongoClient


'''Filter project pairs'''
def filter_references():
    # connect MongoDB database
    client = MongoClient(unicode_decode_error_handler='ignore')
    db = client.ghtorrent
    # open collection
    coll_input = db['input']
    coll_output = db['output']
    for cursor in coll_input.find({}, no_cursor_timeout=True, batch_size=1000):
        source_org = cursor['source_org']
        type = cursor['type']
        bSign = False
        d = {}
        for key in cursor:
            re = key.find("target_org")
            if re != -1:
                target_org = cursor[key]
                target_org_new = filtration(target_org)
                if target_org_new != source_org:
                    bSign = True
                    d[key] = target_org_new
        if bSign:
            # orgin:（pullr、pullr_c、issue、issue_c、commit、commit_c）
            orign = "pullr"
            d['orgin'] = orign
            d['source_org'] = source_org
            d['sourceId'] = cursor['_id']
            d['type'] = cursor['type']
            d['updated_at'] = cursor['updated_at']
            if (orign == "pullr_c") or (orign == "pullr"):
                d['_links'] = cursor['_links']
            elif (orign == "commit_c") or (orign == "issue"):
                d['html_url'] = cursor['html_url']
            elif (orign == "commit") or (orign == "issue_c"):
                d['url'] = cursor['url']
            coll_output.insert_one(d)
    search_repos()
    return

def filtration(target_org):
    target_org_new = ""
    xg_num = target_org.count('/')
    if xg_num != 1:
        return target_org_new
    bool_s = target_org.startswith('/')
    bool_e = target_org.endswith('/')
    if bool_s:
        return target_org_new
    if bool_e:
        return target_org_new
    xg_num = target_org.find('/')
    tmp = target_org[0:xg_num]
    nixu_user = tmp[::-1]
    num = 0
    for letter in nixu_user:
        if (letter.isalnum()) or (letter == '-'):
            num += 1
        else:
            num -= 1
            break
    nixu_user = nixu_user[0:num + 1]
    if nixu_user == "":
        return target_org_new
    user = nixu_user[::-1]
    tmp_repo = target_org[xg_num+1:]
    idx = 0
    for letter in tmp_repo:
        if (letter.isalnum()) or (letter == '-') or (letter == '_') or (letter == '.'):
            idx += 1
        else:
            idx -= 1
            break
    repo = tmp_repo[0:idx + 1]
    if repo != "":
        target_org_new = user + '/' + repo
    return target_org_new

'''
Determine whether the target projects actually exist
'''
def search_repos():
    file = "./repos.txt"
    data_set = set([])
    f = open(file, 'r', encoding='utf-8')
    data = [1]
    while data:
        data = f.readline()
        data = data[:-1]
        data_set.add(data)
    f.close()
    # connect MongoDB database
    client = MongoClient(unicode_decode_error_handler='ignore')
    db = client.ghtorrent
    # open collection
    coll = db['input']
    coll_new = db['output']
    data_set = set([])
    sum = 0
    sum_r = 0
    d = {}
    for cursor in coll.find({}, no_cursor_timeout=True, batch_size=100):
        mylist = []
        sign = False
        source_org = cursor['source_org']
        sign = source_org in data_set
        if sign:
            tag = {}
            for key in cursor:
                ret = key.find('target_org')
                if ret != -1:
                    tag[key] = cursor[key]
                    mylist.clear()
            for key in tag:
                str = tag[key]
                if str in data_set:
                    mylist.append(key)
            if len(mylist) > 0:
                d.clear()
                d['_id'] = cursor['_id']
                d['source_org'] = cursor['source_org']
                for x in mylist:
                    dic = {}
                    dic['full_name'] = cursor[x]
                    origin = cursor['orgin']
                    dic['origin'] = origin
                    dic['type'] = cursor['type']
                    dic['updated_at'] = cursor['updated_at']
                    dic['sourceId'] = cursor['sourceId']
                    if (origin == "pullr_c") or (origin == "pullr"):
                        dic['_links'] = cursor['_links']
                    elif (origin == "commit_c") or (origin == "issue"):
                        dic['html_url'] = cursor['html_url']
                    elif (origin == "commit") or (origin == "issue_c"):
                        dic['url'] = cursor['url']
                    d[x] = dic
                coll_new.insert_one(d)
                sum_r += 1
                print("Successfully found project pairs：", sum_r)
            else:
                sum += 1
                print("Filter project pairs：", sum)
        else:
            sum += 1
            print("Filter project pairs：", sum)
        s = sum + sum_r
        print("The number of data processed：", s)
    return