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
Power Gradient,渐变
Type,类型
U,U
V,V
Diagonal,对角
Radial,径向
Circular,圆形
Box,盒子
Star,星形
Four Corner,四角
Interpolation,插值
None,无
Linear,线性
Exponent Up,指数上升
Exponent Down,指数下降
Smooth,光滑
High Density,高密度
Low Density,低密度
Position,位置
Turbulence,湍流
Octaves,阶度
Scale,缩放
Frequency,频率
Absolute,绝对
Point,点
Edge,边缘
Applying Filter...,应用过滤器…
Object '#',对象 '#'
Record,记录
Strength,强度
Magpie Pro import...,Magpie Pro 导入...
Select Magpie Pro file,选择Magpie Pro文件
Wrong data format|Magpie Pro import failed!,数据格式错误|Magpie Pro导入失败!
C++ SDK - Spherify,C++ SDK - 球面化
C++ SDK - Rounded Tube,C++ SDK - 圆角管道
C++ SDK - Atom,C++ SDK - Atom
C++ SDK - Double Circle,C++ SDK - 双环
C++ SDK - Triangulate,C++ SDK - 三角定位
C++ SDK - OpenGL test object,C++ SDK - OpenGL测试对象
C++ SDK - Look At Camera,C++ SDK - 相机对齐
C++ SDK - Simple Material,C++ SDK - 简易材质
C++ SDK - Funky OpenGL material,C++ SDK - Funky OpenGL材质
C++ SDK - Particle Volume,C++ SDK - 粒子体积
C++ SDK - Mandelbrot,C++ SDK - Mandelbrot
C++ SDK - SDK Gradient,C++ SDK - SDK 渐变
C++ SDK - Bitmap Distortion,C++ SDK - 位图失真
C++ SDK - Blinker,C++ SDK - 闪烁
C++ SDK - Gravity,C++ SDK - 重力
C++ SDK - BFF,C++ SDK - BFF
C++ SDK - STL (*.stl),C++ SDK - STL (*.stl)
C++ SDK - SCULPT (*.scp),C++ SDK - SCULPT (*.scp)
C++ SDK - Menu Test,C++ SDK - 菜单测试
C++ SDK - Async Test,C++ SDK - 异步测试
C++ SDK - Active Object Dialog,C++ SDK - 活动对象对话框
C++ SDK - PGP Test,C++ SDK - PGP测试
C++ SDK - Listview Example,C++ SDK - Listview Example
C++ SDK/Threshold...,C++ SDK/阈值...
C++ SDK/Matrix...,C++ SDK/矩阵...
C++ SDK - Selective Colorize,C++ SDK - 选择着色
C++ SDK - Liquid Painting Tool,C++ SDK - 液体绘画工具
C++ SDK - Sub-Dialog Example,C++ SDK - 子对话框示例
C++ SDK - Invert Image,C++ SDK - 反转图像
C++ SDK - Visualize Channel,C++ SDK - 可视化通道
C++ SDK - Morph Mixer,C++ SDK - 变形混合器
C++ SDK - Visualize Normals,C++ SDK - 可视化法线
C++ SDK - Reconstruct Image,C++ SDK - 重建图像
C++ SDK - Stereoscopic,C++ SDK - 立体
C++ SDK - Example Serial Hook,C++ SDK - 示例串行挂钩
C++ SDK - Edge Cut,C++ SDK - 边缘切割
C++ SDK - Reverse Normals,C++ SDK - 反转法线
C++ SDK - Simple Sculpting Tool,C++ SDK - 简单雕刻工具
C++ SDK - Sculpt Draw Poly Tool,C++ SDK - 多边形绘制工具
C++ SDK - Sculpt Pull Brush Tool,C++ SDK - 拉取刷工具
C++ SDK - Sculpt Grab Brush Tool,C++ SDK - 抓取刷工具
C++ SDK - Sculpt Draw Poly Brush Tool,C++ SDK - 绘制多边形刷工具
C++ SDK - Sculpt Cubes Brush Tool,C++ SDK - 立方体刷工具
C++ SDK - Sculpt Selection Brush Tool,C++ SDK - 选择画笔工具
C++ SDK - Sculpt Spline Brush Tool,C++ SDK - 样条笔刷工具
C++ SDK - Pick Object Tool,C++ SDK - 选择对象工具
Demonstrates how to use ViewportSelect::PickObject,演示如何使用ViewportSelect::PickObject
C++ SDK - Layer Shader Browser,C++ SDK - 层着色器浏览器
C++ SDK - Random Falloff,C++ SDK - 随机衰减
C++ SDK - Noise Effector,C++ SDK - 噪波效果器
C++ SDK - Drop to Surface Effector,C++ SDK - 降至表面效果器
Hair SDK - Comb Deformer,毛发 SDK - 梳子变形器
Hair SDK - Object Force,毛发 SDK - 强制对象
Hair SDK - Collider Object,毛发 SDK - 碰撞器对象
Hair SDK - Constraint,毛发 SDK - 约束
Hair SDK - Grass,毛发 SDK - 草
Hair SDK - Shader,毛发 SDK - 着色器
C++ SDK - Videopost,C++ SDK - 录像机
Hair SDK - Styling,毛发 SDK -造型
Hair SDK - Render Modifier,毛发 SDK - 渲染修饰
Hair SDK - Generator Object,毛发 SDK - 生成器对象
C++ SDK - Sculpt Deformer,C++ SDK - 造型变形器
C++ SDK - Sculpt Modifier,C++ SDK - 造型修饰器
C++ SDK - Sculpt Twist Brush Tool,C++ SDK - 雕刻扭曲刷工具
C++ SDK - Sculpt Multistamp Brush Tool,C++ SDK - 雕刻多级放大工具
C++ SDK - Paint Brush,C++ SDK - 油漆刷
C++ SDK - Paint And Sculpt Brush,C++ SDK - 油漆和造型刷
Paint on polygon objects,绘制多边形对象
Paint and Sculpt at the same time.,绘画和雕刻同时进行。
C++ SDK - Nullsnap,C++ SDK - Nullsnap
C++ SDK - Custom GUI Dots,C++ SDK - 自定义GUI点
C++ SDK - Custom Datatype Dots,C++ SDK - 自定义数据类型点
C++ SDK - Example Dialog,C++ SDK - 示例对话框
C++ SDK - Descriptions Example Object,C++ SDK - 描述示例对象
C++ SDK - Get-/SetDParameter Example Object,C++ SDK - Get-/SetDParameter示例对象
CentiLeo Material,CentiLeo 材质
Reflection 1,反射 1
Reflection 2,反射 2
Reflection 2 bump,反射 2 凹凸
Base color,基本颜色
Transmission,传输
Bump,凹凸
Diffuse,扩散
Translucency,半透明
SSS1,SSS1
SSS2,SSS2
SSS3,SSS3
Subsurface,次表面
Alpha,Alpha
Emission,发光
Displacement,置换
Absorption,吸收
Shallow layer,浅层
Mid layer,中层
Deep layer,深层
Weight,重量
Map,图谱
Color,颜色
Mix,混合
Roughness,粗糙度
IOR,IOR
Anisotropy,各向异性
Rotation,旋转
Radius,半径
Overall,整体
Radius Scale,半径缩放
Scattering,散射
Distance,距离
Distance Scale,距离缩放
Light Shift,光线切换
Height scale,高度缩放
Power,强度
Displacement Alpha,Alpha置换
Edge [pixels],边缘[像素]
Edge [world],边缘[世界]
Subdiv Iterations,细分迭代
Tesselate,镶嵌
Tesselate Reset,镶嵌重置
Autobump power,自动凹凸强度
Autobump,自动凹凸
Adapt to pixels,适应像素
Waterlevel,水位
Bump Reflection 1,凹凸反射 1
Bump Reflection 2,凹凸反射 2
Bump Diffuse,凹凸漫射
Bump Transmission,凹凸传输
Bump Translucency,凹凸半透明
Anisotropy Tangent,各向异性切
Tangent,切
spherical,球形
cylindrical,圆柱
UVW channel 1,UVW通道1
UVW channel 2,UVW通道2
UVW channel 3,UVW通道2
UVW channel 4,UVW通道2
UVW channel 5,UVW通道2
UVW channel 6,UVW通道2
UVW channel 7,UVW频道2
UVW channel 8,UVW通道8
UVW channel 9,UVM通道9
UVW channel 10,UVW通道10
UVW Tangent,UVW 切线
Tag Index,标签值
Reflection as coat,反射涂层
Liquid IOR track,液体IOR追踪
Shaders,着色器
Used shaders:,使用着色器:
Color based mixing,基于颜色的混合
Use glossyness,使用光泽
Matte,不光滑的
Light pass,光线通道
Matte Shadow Weight,哑光阴影权重
Emission Scale,发射缩放
Camera,相机
Reflection,反射
Translucent,透明度
SSS,SSS
Direct Lighting,直接照明
Indirect Lighting,间接照明
Color Tint,色彩
Importance Sampling,重要性抽样
CentiLeo Multi Mtl,CentiLeo 多层材质
Mask,蒙版
Mask Map,绘制蒙版
Material,标准材质
Is coat,IS COAT
Base Layer,基础层
Layer 1,图层 1
Layer 2,图层 2
Layer 3,图层 3
Layer 4,Layer 4
Layer 5,Layer 5
Layer 6,Layer 6
Layer 7,Layer 7
Layer 8,Layer 8
Layer 9,Layer 9
,
Material Shaders,材质着色器
CentiLeo Preferences,CentiLeo 偏好设置
GPU Settings,GPU设置
Texture Settings,结构设置
CPU texture cache [MB],CPU纹理缓存[MB]
Disc storage for Texture cache,用于纹理缓存的磁盘存储
In original file location,在原始文件位置
Single cache folder for all textures,单个缓存文件夹为所有纹理
Cache folder,缓存文件夹
Apply Settings,应用设置
Open Console,打开控制台
GPU0,GPU0
GPU1,GPU1
GPU2,GPU2
GPU3,GPU3
GPU4,GPU4
GPU5,GPU5
GPU6,GPU6
GPU7,GPU7
GPU8,GPU8
GPU9,GPU9
GPU10,GPU10
GPU11,GPU11
GPU12,GPU12
GPU13,GPU13
GPU14,GPU14
GPU15,GPU15
CentiLeo settings,CentiLeo设置
Renderer settings,渲染器设置
Test1,Test1
Test2,Test2
Num samples,Num 采样
DimX,DimX
DimY,迪米
Pixel,像素
Rand scale,随机缩放
Ax,Ax
Ay,Ay
Grid size,网格大小
wo.x,wo.x
wo.y,wo.y
wo.z,wo.z
Grid cells,网格
Max iterations,最大迭代
Min iterations,最小迭代
Noise level,噪点等级
Camera Projection,摄像机投射
Standard,标准
Spherical,球形
Static Noise pattern,静态噪点
Clamp direct light,直接光照
Clamp specular,镜面反射
Clamp indirect,间接
Mult,多
Expected Exposure,预期曝光
Fireflies killer strength,光斑去除强度
Render iteration compute power,渲染迭代计算能力
Max ray bounces,最大光线弹射
Max diffuse bounces,最大漫射深度
Pixel filter size [pixels],像素滤镜大小
Default environment color,默认环境颜色
IPR,IPR
IPR refresh time[ms],IPR 刷新时间[ms]
IPR priority,IPR 优先级
IPR width,IPR 宽度
IPR height,IPR 高度
Lock aspect,锁定方位
Autofit,自适应
IPR start,IPR 开始
AOVs/passes,AOVs/通道
Beauty passes (visible material layers),颜色通道(可见材质层)
Light passes,光线
Transparent Background,透明背景
Beauty Main pass,色彩主要通道
Alpha channel,Alpha通道
Premult alpha,预乘Alpha
Denoise images,降噪图像
Keep raw and denoised AOVs,保持Raw格式与降噪AOVs
Send RAW AOVs (gamma = 1) to Picture Viewer,发送RAW AOVs (gamma = 1)到图片查看器
Update AOVs in Picture Viewer after render completion,在渲染完成后更新图片查看器中的Aovs
Beauty: Diffuse,色彩:漫射
Beauty: Reflection,色彩:反射
Beauty: Reflection 2,色彩:反射 2
Beauty: Translucent,色彩:透明度
Beauty: SSS,色彩:SSS
Beauty: Transmission,色彩:传输
Beauty: Background,色彩:背景
Beauty: Emission,色彩:发光
Light pass 0,灯光通道 0
Light pass 1,灯光通道 1
Light pass 2,灯光通道 2
Light pass 3,灯光通道 3
Light pass 4,灯光通道 4
Light pass 5,灯光通道 5
Light pass 6,灯光通道 6
Light pass 7,灯光通道 7
Blender Beauty passes,混合色彩通道
Blender Light passes,混合光线通道
Info passes,信息通道
Normals geometric,法线几何
Normals shading,法线阴影
Depth of Field,景深
Enabled,启用
Sensor width,传感器宽度
Focus dist,焦距
Num blades,Num Blades
Blade angle,叶面角度
Motion Blur,运动模糊
Transformation keys,转换键
Deformation enabled,启用变形
Shutter Begin,快门开始
End,结束
Tip: simulations need to be cached for proper motion blur,提示:模拟需要缓存适当的运动模糊
Displacement Mapping,置换映射
polygon edge size [pixels],多边形边缘大小[像素]
max tesselation iterations,最大细分迭代
max new polygons [millions],最大新增多边形[]万
Hardware Settings,硬件设置
GPU geometry cache [MB],GPU几何缓存[MB]
GPU texture cache [MB],GPU纹理缓存[MB]
GPU select,GPU选择
Apply HW Settings (resets scene),应用HW设置(重置场景)
Open Hardware Settings,打开硬件设置
low priority,低优先级
Post-render settings,渲染设置
Highlights white,白色高光
Exposure,曝光
Contrast shadows,对比阴影
Contrast highlights,对比高光
White balance,白平衡
RGB scale,RGB缩放
Vignetting,暗角
Midtone offset,中间值偏移
Hue,色调
Saturation,饱和度
Brighness,明亮
Contrast,对比
Output rangeA,输出rangeA
Output rangeB,输出rangeB
Clamp Min,最小修剪
Clamp Max,最大修剪
Gamma (display),Gamma(显示)
Material converter,材质转换器
Convert materials (only trivial),转换材质(简单)
CentiLeo Camera Params,CentiLeo相机参数
Override global settings,覆盖全局设置
Post Settings,传输设置
CentiLeo ID,CentiLeo ID
CENTILEO ID,CENTILEO ID
CentiLeo Environment Params,CentiLeo环境参数
Environment,环境
Multiplier,倍增
Gamma,伽马
Base,基础
Envmap Color,环境
Envmap Filename,环境贴图文件
Reset Cache,重置缓存
Brightness,亮度
Note: zero value makes light invisible for layer,注意:零值使光在图层上不可见
Shadow Catcher:,阴影捕捉
Camera:,相机:
Diffuse:,漫射:
Reflection:,反射:
Reflection 2:,反射 2:
Translucent:,透明度:
SSS:,SSS:
Transmission:,传输:
Overrides,覆盖
Other Sky objects:,其他天空对象:
Matte Shadow,阴影蒙版
CentiLeo Light Params,CentiLeo灯光参数
Light,灯光
Overall multiplier,总乘数
Shape radius,形状半径
Lighting angle,照明角度
Is portal,Is 门户
Normalize intensity,标准化强度
Contribute only to GI,仅对Gi造成影响
Direct / Indirect Light,直接/间接光
CentiLeo Object parameters,CentiLeo对象参数
Particle Settings,粒子设置
Reference Objects,引用对象
Seed,种子
Motion blur,运动模糊
Velocity Scale,速度缩放
Velocity X,速度X
Velocity Y,速度Y
Velocity Z,速度Z
Bitmap,位图
Name,名称
Projection,投射
Mapping,映射
Output,输出
Filename,文件名
image or bump,图片或凹凸
image,图像
bump map,凹凸贴图
normal map,法线贴图
Map black to,黑色映射到
Map white to,白色映射到
Filter scale,过滤缩放
Out of UVW,Out of UVW
Tiles U,平铺 U
W,W
Offset U,偏移 U
Distortion,变形
amount,数量
size,大小
Texel type,Texel类型
Nearest,最近的
Randomize offset,随机偏移
Crop Image,图像裁剪
Begin,开始
Begin U,开始 U
Begin V,开始 V
End U,结束 U
End V,结束 V
tiles,平铺
offset,偏移
rotation,旋转
Input UVW,输入UVW
texture tag,纹理标签
flat,平坦
flat side,平边
XYZ (3D),XYZ (3D)
cubic,立方体
triplanar,三平面
spatial,空间
Triplanar blend,三平面混合
tiling mode,平铺模式
repeat,重复
mirror,镜像
clamp black,修剪黑色
clamp white,修剪白色
Output Alpha,输出Alpha
Is normal map,法线贴图
Normal Map,法线贴图
Flip X (red),反转 X (红)
Swap X & Y,交换X和Y
Flip Y (green),反转 Y (绿)
Swap Y & Z,交换Y和Z
Flip Z (blue),反转 Z (蓝)
Swap Z & X,交换Z和X
Layer,层
Layer Base,基础层
Num Layers,Num Layers
Mix mode,混合模式
Normal,CR | 法线
Multiply,相乘
Screen,屏幕
Overlay,覆盖
Hard Light,强光
Soft Light,柔光
Dodge,色彩加深
Burn,燃烧
Darken,变暗
Lighten,变亮
Add,添加
Substract,相减
Difference,插值
Exclusion,排除
Luminance,亮度
Base Map,草图
Color Map,颜色映射
Mask 2,蒙版 2
Mask 3,蒙版 3
Mask 4,蒙版 4
Mask 5,蒙版 5
Mask 6,蒙版 6
Mask 7,蒙版 7
Color Correct,颜色校正
Output black,输出黑色
Output white,输出白色
Clamp Enabled,修剪启用
Input Map,输入贴图
tex,纹理
test,测试
Constant,常数
Scalar,分级
Vector,向量
Curve Map,曲线图
Input Texture,输入纹理
Input Min,最小输入
Input Max,最大输入
Dirt,污垢
Occluded,闭塞
Unoccluded,通畅
Sensitivity,灵敏度
Softness,柔软
Falloff,衰减
Curve power,功率曲线
0 deg,0 deg
90 deg,90 deg
Falloff type,衰减类型
Fresnel,菲涅尔
Flakes,薄片
Tiles,平铺
Offset,偏移
Orientation,方向
Density,密度
Flakes IDs (greyscale),片IDs(灰度)
Flakes Mask (black or white),薄片蒙版(黑色或白色)
Math,数学
A value,A值
B value,B值
Const,常量
A + B,A + B
A - B,A - B
A * B,A * B
A / B,A / B
"min(A, B)","min(A, B)"
"max(A, B)","max(A, B)"
"pow(A, B)","pow(A, B)"
Map A,映射A
Map B,映射B
MoGraph Info,MoGraph信息
Attribute,属性
ID,ID
ID Ratio,ID 比例
UVW,UVW
Noise,噪波
Noise Details,噪点细节
Noise type,噪类型
FBM,FBM
Ridged Multifractal,脊多重分形
Ronk,朗克
Cells,细胞
Voronoi Cells,泰森多边形法细胞
Voronoi F1,泰森多边形法F1
Voronoi F2,泰森多边形法F2
Voronoi F3,泰森多边形法F3
Voronoi F4,泰森多边形法F4
Voronoi F2-F1,泰森多边形法F2-F1
Woody,木质
amount y,y数量
amount z,z数量
Seedz,种子
Lacunarity,空隙
Omega,Omega
H,H
Gain,增益
Normalize,标准化
Clip enabled,启用修剪
Low clip,底部修剪
High clip,顶部修剪
Add value,添加值
Multiply by,乘以
Absolute value,绝对值
Post effect,Post效果
no effect,没有影响
distort+,失真+
marble,大理石
saw,Saw
Quantize enabled,启用数字转换
Quantize,数字转换
Post effect strenth,后效应强度
Rotation U,旋转U
triplanar sharpness,三平面清晰度
Particle Info,粒子的信息
Group ID,组ID
Velocity,速度
Speed,速度
Age,年龄
Life,生命周期
Mass,质量
Distance Travelled,运动距离
Temperature,色温
Fuel,燃料
Fire,火焰
Smoke,烟
Pattern,图案
Element size,元素的大小
Pattern type,图案类型
X waves,X波
Y waves,Y波
cylindrical rings,圆柱环
spherical rings,球形环
checker,检查器
Smoothing,平滑
sin,sin
UVW Projection,UVM投射
Param Maps,参数映射
Coordinates,坐标
UVW Mapping,UVW映射
UVW Tag Index,UVM标记值
Surface Side,表面
Invert,反转
Ramp,斜坡
Gradient,渐变
Step,步幅
Knot Maps,节点映射
Texture,纹理
Knot 1,节点 1
Knot 2,节点 2
Knot 3,节点 3
Knot 4,节点 4
Knot 5,节点 5
Knot 6,节点 6
Knot 7,节点 7
Knot 8,节点 8
Knot 9,节点 9
Knot 10,节点 10
Knot 11,节点 11
Knot 12,节点 12
Knot 13,节点 13
Knot 14,节点 14
Knot 15,节点 15
Knot 16,节点 16
Knot 17,节点 17
Knot 18,节点 18
Knot 19,节点 19
Knot 20,节点 20
Knot 21,节点 21
Knot 22,节点 22
Knot 23,节点 23
Knot 24,节点 24
Knot 25,节点 25
Knot 26,节点 26
Knot 27,节点 27
Knot 28,节点 28
Knot 29,节点 29
Knot 30,节点 30
Random,随机
Extra Seed,额外种子
Black & White,黑色和白色
Resolution,分辨率
Hue Begin,色调开始
Hue End,色调结束
Saturation Begin,饱和度开始
Saturation End,饱和度结束
Value Begin,值开始
Value End,结束值
Gamma Begin,Gamma开始
Gamma End,Gamma结束
Randomize by,随机
Output Color,输出颜色
Random Objects,随机的对象
Random Object parts,随机对象部分
Remap,重映射
Output Min,最小输出
Output Max,最大输出
Steps,步幅
Scratches,划痕
Thickness,厚度
Deep,深度
Triplanar,三平面
Map YZ,Map YZ
Map ZX,Map ZX
Map XY,Map XY
UVW Distortion,UVM扭曲
Amount,数量
UVW Transform,UVW变换
Pivot,锚点
Repetitions,重复
Rand offset,随机偏移
Decal,封装
Tiling mode,平铺模式
Extend,扩展
Repeat,重复
Mirror,镜像
Vertex Color,顶点的颜色
Vertex Map,顶点贴图
Surface Wire,表面线条
Size,尺寸
C++ SDK - Custom GUI String,C++ SDK - 自定义GUI字符串
