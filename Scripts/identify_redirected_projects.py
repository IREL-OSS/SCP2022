
# -*- coding:utf-8 -*-
#====#====#====#====
# __author__ = "liubc"
#FileName: Reference_Identification.py
#Version:1.0.0
#CreateTime:xxxx-xx-xx
#====#====#====#====
from pymongo import MongoClient
import requests
import itertools

'''
Function: Identify changes to project names
Step 1: Extract names for all projects
Step 2: Determine whether the name of each project change. Save the new project name when project's name change
Step 3: Replace the old name with the new one
'''
def identify_redirectedProjects():
    idx = 0
    sum = 0
    dict = {}
    dataset = set([])
    f = open('dataset.txt', 'a+')
    # connect MongoDB database
    client = MongoClient(unicode_decode_error_handler='ignore')
    db = client.ghtorrent
    # open collection
    coll_input = db['input']
    for cursor in coll_input.find({}, no_cursor_timeout=True, batch_size=100):
        ID = cursor['_id']
        source = cursor['source_org']
        if source not in dataset:
            dataset.add(source)
            dict['_id'] = ID
            dict['full_name'] = source
            source += '\n'
            f.write(source)
            idx += 1
        for key in cursor:
            if key.find('target_org') != -1:
                tag = cursor[key]
                target = tag['full_name']
                if target not in dataset:
                    dataset.add(target)
                    target += '\n'
                    f.write(target)
                    idx += 1
        sum += 1
        print('traverse tha database：', sum)
    f.close()
    print('The database traversal is complete~')
    print('Total number of projects is：', idx)
    #Step 2
    file = open('repos.txt', 'r', encoding='utf-8')
    data_list = file.readlines()
    file.close()
    # Crawl the project url
    # connect MongoDB database
    coll_redirected = db['redirected_projects']
    for str in data_list:
        repo = str[:-1]
        repo_list = siteCrawl(repo)
        dict['status_code'] = repo_list['status_code']
        ret = repo_list.get('redirection')
        if ret != None:
            dict['redirection'] = repo_list['redirection']
        newname = repo_list.get('new_name')
        if newname != None:
            dict['new_name'] = repo_list['new_name']
        dict['crawler'] = True
        coll_redirected.insert_one(dict)
    replaceNewName()
    return

def replaceNewName():
    # Step 3
    rdictlist = []
    olddict = {}
    newdict = {}
    dict = {}
    # connect MongoDB database
    client = MongoClient(unicode_decode_error_handler='ignore')
    db = client.ghtorrent
    # open collection
    coll_redirected = db['redirected_projects']
    coll_input = db['input']
    coll_output = db['output']
    for curcor in coll_redirected.find({}, no_cursor_timeout=True, batch_size=1000):
        full_name = curcor['full_name']
        new_name = curcor['new_name']
        rdictlist.append(full_name)
        rdictlist.append(new_name)
        olddict[full_name] = new_name
        newdict[new_name] = full_name
    for curcor_in in coll_input.find({}, no_cursor_timeout=True, batch_size=1000):
        source = curcor_in['source_org']
        if source in rdictlist:
            dict = combinedict(source, olddict, newdict)
            coll_output.insert_one(dict)
        else:
            for key in curcor_in:
                if key.find('target_org') != -1:
                    dict = curcor_in[key]
                    target = dict['full_name']
                    if target in rdictlist:
                        dict = combinedict(target, olddict, newdict)
                        coll_output.insert_one(dict)
    return


def siteCrawl(full_name):
    token_list = [
        '915544cbbb05b34ca25803bc18f829b0912eba9e',
        'f47cdf56353f15afd987748873d9cbde1caafecb'
    ]
    token_iter = itertools.cycle(token_list)
    token = token_iter.__next__()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8;application/vnd.github.v3.star+json',
        'Accept-Language': 'en',
        'Authorization': 'token ' + token
    }
    dict = {}
    url = 'https://api.github.com/repos/' + full_name
    re = requests.get(url, headers=headers, timeout=3)
    status_code = re.status_code
    if status_code == 200:
        response_dict = re.json()
        if 'html_url' in response_dict:
            html = response_dict['html_url']
            mylist = html.split('/')
            new_name = mylist[3] + '/' + mylist[4]
        else:
            new_name = full_name
        redirection = 'False'
        if new_name != full_name:
            redirection = 'True'
        dict['full_name'] = full_name
        dict['status_code'] = status_code
        dict['redirection'] = redirection
        dict['new_name'] = new_name
    return dict

def combinedict(name, olddict, newdict):
    dict = {}
    ret = olddict.get(name)
    if ret == None:
        ret = newdict.get(name)
        dict['full_name'] = ret
        dict['new_name'] = name
    else:
        dict['full_name'] = name
        dict['new_name'] = ret
    return dict