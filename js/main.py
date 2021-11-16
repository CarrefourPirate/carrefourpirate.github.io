# -*- coding = utf-8 -*-
# @Author : Peirato
# @Software : PyCharm

import csv
import hashlib
import os
import re
import shutil
import time
import uuid

import requests

fTT = re.compile('(.*?)".*?;', re.S)
fbk = re.compile('\{(.*?)\}', re.S)
cpTxt = re.compile('"(.*?)";', re.S)
cpCn = re.compile('"translation":\["(.*?)"],', re.S)
YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '7f348019f4c4e9da'
APP_SECRET = 'paWlXFJtBsgRp7GFU20NBcemyXWOjksQ'
ft = re.compile('TXTXTXT', re.S)
dictPath = 'C:\\Users\\1\\Desktop\\En2Cn\\Dict'

def trans(q, tf='auto', tt='auto'):
    def encrypt(signStr):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode('utf-8'))
        return hash_algorithm.hexdigest()

    def truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]

    def do_request(data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(YOUDAO_URL, data=data, headers=headers)

    data = {}
    curtime = str(int(time.time()))
    salt = str(uuid.uuid1())
    data['q'] = q
    data['from'] = tf
    data['to'] = tt
    data['signType'] = 'v3'
    data['curtime'] = curtime
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['sign'] = sign
    res = do_request(data)
    return re.findall(cpCn, str(res.content.decode('utf-8')))[0]


def transFile(file):
    data = open(file, 'r', encoding='utf-8').read()
    dict = rdCsvAsDict(dictPath)
    kwds = re.findall(cpTxt, data)
    oFile = re.sub(cpTxt, '"TXTXTXT";', data)
    if len(kwds) == 0:
        return data
    for i in kwds:
        if len(i) == 0 or i == " ":
            oFile = re.sub(ft, i, oFile, count=1)
            continue
        if i in dict:
            print('%s-匹配到字典！' % (i))
            sti = str2unicode(dict[i])
            oFile = re.sub(ft, sti, oFile, count=1)
        else:
            ti = trans(i)
            if '“' in ti:
                ti = ti.replace('“', "'")
                ti = ti.replace('”', "'")
            print("%s | 翻译建议:%s" % (i, ti))
            t = input("请输入: ")
            sti = str2unicode(ti)
            if t:
                ti = t
                oFile = re.sub(ft, sti, oFile, count=1)
            else:
                oFile = re.sub(ft, sti, oFile, count=1)
            dict[i] = ti
    saveDictAsCsv(dict, dictPath)
    return oFile


def dict2list(dict):
    dlist = []
    for x in dict:
        dlist.append([x, dict[x]])
    return dlist


def list2dict(lists):
    dict = {}
    for x in lists:
        dict[x[0]] = x[1]
    return dict


def rdCsvAsDict(fileName):
    try:
        cvsData = open("%s.csv" % (fileName), 'r+', encoding='utf-8')
    except Exception:
        cvsData = open("%s.csv" % (fileName), 'w+', encoding='utf-8')
    lists = []
    csvReader = csv.reader(cvsData)
    for i in csvReader:
        lists.append(i)
    return list2dict(lists)

def saveDictAsCsv(dict, fileName):
    lists = dict2list(dict)
    csvFile = open("%s.csv" % (fileName), 'w+', encoding='utf-8', newline="")
    csvWriter = csv.writer(csvFile)
    for i in lists:
        csvWriter.writerow(i)
    csvFile.close()


def str2unicode(strs):
    s = strs.encode('unicode-escape').decode().replace('\\', '\\\\')
    return s


def saveData(data, filePath):
    file = open(filePath, 'w+')
    file.write(data)
    file.close()


def bpFiles(file, bpFile):
    if bpFile in os.listdir(os.getcwd()):
        print('无法备份，请更换备份文件名！')
    if file in os.listdir(os.getcwd()):
        shutil.copytree(file, bpFile)
        print('文件备份成功！')
    else:
        print('文件不存在！')


def chgFileTp(file, t):
    for x, y, z in os.walk(os.getcwd() + '\\%s' % (file)):
        for i in os.listdir(x):
            if '.' in i:
                os.rename('%s\\%s' % (x, i), '%s\\%s%s' % (x, i[0:i.find('.') + 1], t))
            else:
                continue
    print('格式转化成功！')


def rmFiles(file):
    try:
        shutil.rmtree(file)
        print("文件删除成功！")
    except Exception:
        print("文件删除失败！")


def learner(fEn, fCn):
    print('Learning %s'%(fCn))
    dict = rdCsvAsDict(dictPath)
    dataEn = getTxtCrsp(fEn)
    dataCn = getTxtCrsp(fCn)
    if not dataCn and dataEn:
        raise Exception("文件错误！")
    for x in dataEn:
        if x in dataCn and not dataEn[x] in dict:
            dict[cTxt(dataEn[x])] = cTxt(dataCn[x])
    saveDictAsCsv(dict, dictPath)


def getTxtPath(fileNm):
    pathList = []
    for x, y, z in os.walk(os.getcwd() + '\\%s' % (fileNm)):
        for i in os.listdir(x):
            if '.' in i:
                pathList.append('%s\\%s' % (x, i))
    return pathList


def runlearner(enFile, cnFile):
    enP = getTxtPath(enFile)
    cnP = getTxtPath(cnFile)
    erroFiles = []
    mainPath = []
    for x in enP:
        for y in cnP:
            if x[::-1][0:x[::-1].index('\\')] == y[::-1][0:y[::-1].index('\\')]:
                mainPath.append([x, y])
                break
    for p in mainPath:
        try:
            learner(p[0], p[1])
        except Exception:
            erroFiles.append(p[0])
            print(erroFiles)
    if len(erroFiles) >= 1:
        csvFile = open('errorFiles.csv', 'w+', encoding='utf-8', newline='')
        csvWriter = csv.writer(csvFile)
        for i in erroFiles:
            csvWriter.writerow(i)
        csvFile.close()


def cTxt(txt):
    return txt.strip().replace("\n", '').replace('\t', '')


def runTranslator(fileNm, opFileNm):
    try:
        shutil.rmtree(opFileNm)
        print("文件移除成功！")
    except Exception:
        pass
    bpFiles(fileNm, opFileNm)
    chgFileTp(opFileNm, 'txt')
    for x, y, z in os.walk(os.getcwd() + '\\%s' % (opFileNm)):
        for i in os.listdir(x):
            if '.' in i:
                print('正在翻译: %s' % (i))
                print('==================')
                saveData(transFile('%s\\%s' % (x, i)), '%s\\%s' % (x, i))
            else:
                continue
    chgFileTp(opFileNm, 'str')


def getTxtCrsp(path):
    dict = {}
    txt = open(path, 'r', encoding='unicode_escape').read()
    try:
        fstW = re.findall(fTT, re.findall(fbk, txt)[0])
    except Exception:
        return False
    lstW = re.findall(cpTxt, txt)
    c = 0
    for i in fstW:
        if not i in dict and len(lstW[c]) >= 1:
            dict[cTxt(i)] = lstW[c]
        c += 1
    return dict


def checkFiles(fileName):
    fileList = os.listdir(os.getcwd())
    if fileName in fileList:
        return True
    else:
        return False

if __name__ == '__main__':
    fileNm = 'strings_us'
    opFileNms = ['strings_cn','strings_zh-CN']
    if not checkFiles(fileNm):
        print("找不到文件！")
        exit()
    while True:
        print("\nA | 学习模式\nB | 翻译模式\nX | 退出程序")
        choice = input("请选择: ").upper()
        if choice == 'A':
            opFileNm = ''
            for f in opFileNms:
                if checkFiles(f):
                    opFileNm = f
                    break
            if not opFileNm:
                print("找不到文件！")
                exit()
            runlearner(fileNm,opFileNm)
            break
        elif choice == 'B':
            runTranslator(fileNm,opFileNms[0])
            print('翻译完成！')
            break
        elif choice == 'X':
            exit()
        else:
            print("请输入正确的选项！")
            continue
