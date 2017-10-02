#!/anaconda/bin/python
# -*- coding: utf-8 -*-

import sys
if sys.platform == 'darwin':
    import matplotlib as mpl
    mpl.use('TkAgg')
    
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import tkinter
from tkinter import *
from tkinter import font
import tkinter.filedialog as tkfd

import scipy.misc
from scipy import ndimage
import os
import glob
import json
from collections import defaultdict
import numpy as np
import cv2
import webbrowser

from PIL import ImageTk, Image


root = tkinter.Tk()
root.title(u"Cell Cropper v1.0")
root.geometry("650x440")

font = font.Font(family="TakaoExGothic", size=12)

def setdirectory(event):
    
    global directory_path, EditBox_0
    
    directory_path = tkfd.askdirectory()
    EditBox_0.insert(tkinter.END, directory_path)


def data_import(event):
    
    global directory_path, EditBox_0
    global X
    
    directory_path = str(EditBox_0.get())
    
    path = str(directory_path) + "/" + "*"  
    filenames = glob.glob(path)

    processed_image_count = 0
    useful_image_count = 0

    X = []
    
    img_f = scipy.misc.imread(filenames[0])
    height, width, chan = img_f.shape
    

    for filename in filenames:
        processed_image_count += 1
        img = scipy.misc.imread(filename)
        assert chan == 3
        img = scipy.misc.imresize(img, size=(height, width), interp='bilinear')
        X.append(img)
        useful_image_count += 1
        
    print("総数 %d, 読み込みに成功した画像 %d" % (processed_image_count, useful_image_count))
    print("画像縦 %d px, 画像幅 %d px" % (height, width))

    X = np.array(X).astype(np.float32)


def pre_check(event):
    
    global Val1, EditBox_1, EditBox_2, EditBox_3
    global X, binimg
    
    pic = int(EditBox_1.get()) - 1
    binimg_thred = float(EditBox_2.get())
    chs = int(EditBox_3.get())
    

    img = X[pic].astype(np.uint8)
    

    img_chs = cv2.split(img)
    img_preprocessed = cv2.GaussianBlur(img_chs[chs],(5,5),0)
    if Val1.get()==False:
        binimg = (img_preprocessed < np.percentile(img_preprocessed, binimg_thred))
        binimg = binimg.astype(np.uint8)
    else:
        binimg = (img_preprocessed > np.percentile(img_preprocessed, binimg_thred))
        binimg = binimg.astype(np.uint8)

    
    fig = plt.figure(figsize=(12, 12))
    
    ax = fig.add_subplot(2, 1, 1)
    ax.imshow(img)
    ax = fig.add_subplot(2, 1, 2)
    ax.imshow(binimg)
    
    plt.show() 
    

def cell_crop_test(event):
    
    global Val1, EditBox_1, EditBox_2, EditBox_3, EditBox_4, EditBox_5, EditBox_6
    global X, cells_test, binimg
    
    pic = int(EditBox_1.get()) - 1
    binimg_thred = float(EditBox_2.get())
    chs = int(EditBox_3.get())
    
    min_area = int(EditBox_4.get())
    scale_v = int(EditBox_5.get())//2
    scale_h = int(EditBox_6.get())//2
    
    cells_test = np.empty((0, scale_v*2, scale_h*2, 3))
    
    img = X[pic].astype(np.uint8)
    
    img_, contours, _ = cv2.findContours(binimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    arr=[]
    
    start=np.empty((0,2))
    start=np.append(start,np.array([[0, 0]]),axis=0)
    
    for j in contours:
        if cv2.contourArea(j)<min_area:
            continue
        x_=0
        y_=0
        for k in j:
            x_ += k[0][0]
            y_ += k[0][1]
        arr.append([x_/len(j), y_/len(j)])
    arr = np.array(arr)
    
    for j in range(len(arr)):
    
        if (arr[j][1] < scale_v) or (arr[j][1] > img.shape[0]-scale_v) or (arr[j][0] < scale_h) or (arr[j][0] > img.shape[1]-scale_h):
            continue 
        
        top = int(arr[j][1])-scale_v
        bottom = int(arr[j][1])+scale_v
    
        left = int(arr[j][0])-scale_h
        right = int(arr[j][0])+scale_h
    
        if left < 0:
            left = 0
            right = scale_h*2
        if right > img.shape[1]:
            right = img.shape[1]
            left = img.shape[1]-scale_h*2
    
        if top < 0:
            top = 0
            bottom = scale_v*2
        if bottom > img.shape[0]:
            bottom = img.shape[0]
            top = img.shape[0]-scale_v*2      
                
        img_crop = np.array(img[top:bottom,left:right]).reshape(scale_v*2, scale_h*2, 3).astype(np.uint8)
        img_chs = cv2.split(img_crop)
        img_preprocessed = cv2.GaussianBlur(img_chs[chs],(5,5),0)
            
        if Val1.get()==False:
            binimg_crop = (img_preprocessed < np.percentile(img_preprocessed, binimg_thred))
            binimg_crop = binimg_crop.astype(np.uint8)
        else:
            binimg_crop = (img_preprocessed > np.percentile(img_preprocessed, binimg_thred))
            binimg_crop = binimg_crop.astype(np.uint8)

        img_, contours, _ = cv2.findContours(binimg_crop, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            
        contourArea = []
            
        for j in contours:
            contourArea.append(cv2.contourArea(j))
        contourArea_sum = sum(contourArea)
        if contourArea_sum<min_area:
            continue
    
        cells_test = np.append(cells_test,np.array(img[top:bottom,left:right]).reshape(1,scale_v*2, scale_h*2, 3),axis=0)
        
        if cells_test.shape[0]==10:
            break
    
    fig = plt.figure(figsize=(12, 12))

    photo_num = cells_test.shape[0]
    if photo_num>2000:
        photo_num = 2000
    
    for i in range(photo_num):
        
        ax_cell = fig.add_subplot(5, 10, i + 1, xticks=[], yticks=[])
        ax_cell.imshow(cells_test[i].reshape((scale_v*2, scale_h*2, 3)).astype(np.uint8))

    plt.show()
       
    
    
def cell_crop(event):
    
    global Val1, EditBox_1, EditBox_2, EditBox_3, EditBox_4, EditBox_5, EditBox_6
    global X, cells
    
    pic = int(EditBox_1.get()) - 1
    binimg_thred = float(EditBox_2.get())
    chs = int(EditBox_3.get())
    
    min_area = int(EditBox_4.get())
    scale_v = int(EditBox_5.get())//2
    scale_h = int(EditBox_6.get())//2
    
    cells = np.empty((0, scale_v*2, scale_h*2, 3))
    
    for i in range(X.shape[0]):
        img = X[i].astype(np.uint8)
        img_chs = cv2.split(img)
        img_preprocessed = cv2.GaussianBlur(img_chs[chs],(5,5),0)
        if Val1.get()==False:
            binimg = (img_preprocessed < np.percentile(img_preprocessed, binimg_thred))
            binimg = binimg.astype(np.uint8)
        else:
            binimg = (img_preprocessed > np.percentile(img_preprocessed, binimg_thred))
            binimg = binimg.astype(np.uint8)

        img_, contours, _ = cv2.findContours(binimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        arr=[]
    
        start=np.empty((0,2))
        start=np.append(start,np.array([[0, 0]]),axis=0)
    
        for j in contours:
            if cv2.contourArea(j)<min_area:
                continue
            x_=0
            y_=0
            for k in j:
                x_ += k[0][0]
                y_ += k[0][1]
            arr.append([x_/len(j), y_/len(j)])
        arr = np.array(arr)
    
    
        for j in range(len(arr)):
    
            if (arr[j][1] < scale_v) or (arr[j][1] > img.shape[0]-scale_v) or (arr[j][0] < scale_h) or (arr[j][0] > img.shape[1]-scale_h):
                continue 
        
            top = int(arr[j][1])-scale_v
            bottom = int(arr[j][1])+scale_v
    
            left = int(arr[j][0])-scale_h
            right = int(arr[j][0])+scale_h
    
            if left < 0:
                left = 0
                right = scale_h*2
            if right > img.shape[1]:
                right = img.shape[1]
                left = img.shape[1]-scale_h*2
    
            if top < 0:
                top = 0
                bottom = scale_v*2
            if bottom > img.shape[0]:
                bottom = img.shape[0]
                top = img.shape[0]-scale_v*2      
                
            img_crop = np.array(img[top:bottom,left:right]).reshape(scale_v*2, scale_h*2, 3).astype(np.uint8)
            img_chs = cv2.split(img_crop)
            img_preprocessed = cv2.GaussianBlur(img_chs[chs],(5,5),0)
            
            if Val1.get()==False:
                binimg_crop = (img_preprocessed < np.percentile(img_preprocessed, binimg_thred))
                binimg_crop = binimg_crop.astype(np.uint8)
            else:
                binimg_crop = (img_preprocessed > np.percentile(img_preprocessed, binimg_thred))
                binimg_crop = binimg_crop.astype(np.uint8)

            img_, contours, _ = cv2.findContours(binimg_crop, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            
            contourArea = []
            
            for j in contours:
                contourArea.append(cv2.contourArea(j))
            contourArea_sum = sum(contourArea)
            if contourArea_sum<min_area:
                continue
    
            cells = np.append(cells,np.array(img[top:bottom,left:right]).reshape(1,scale_v*2, scale_h*2, 3),axis=0)

    print("切り出した画像数:", cells.shape[0])
    
    fig = plt.figure(figsize=(12, 12))

    photo_num = cells.shape[0]
    if photo_num>1000:
        photo_num = 1000

    for i in range(photo_num):
        
        ax_cell = fig.add_subplot(40, 25, i + 1, xticks=[], yticks=[])
        ax_cell.imshow(cells[i].reshape((scale_v*2, scale_h*2, 3)).astype(np.uint8))

    plt.show()
    

def save_cropped_pics(event):
    
    global cells, EditBox_7
    
    npy_name = str(EditBox_7.get()) + ".npy"
    np.save(npy_name, cells)
    

Static_1 = tkinter.Label(text=u'ディレクトリパス', font=font)
Static_1.grid(column=0,row=0,sticky=tkinter.W, padx=20)

Button_0 = tkinter.Button(text=u'1.ディレクトリを選択', width=30, font=font)
Button_0.bind("<Button-1>",setdirectory) 
Button_0.grid(column=1,row=0)

EditBox_0 = tkinter.Entry(width=75, font=font)
EditBox_0.grid(column=0,row=1,columnspan=2)

Button_1 = tkinter.Button(text=u'2.画像の読み込みを開始する', width=30, font=font)
Button_1.bind("<Button-1>",data_import) 
Button_1.grid(column=1,row=2)

Static_0 = tkinter.Label(text=u'')
Static_0.grid(column=0,row=3,sticky=tkinter.W, padx=20)

Static_2 = tkinter.Label(text=u'チェックに使用する画像ナンバー', font=font)
Static_2.grid(column=0,row=4,sticky=tkinter.W, padx=20)

EditBox_1 = tkinter.Entry(width=5, font=font)
EditBox_1.insert(tkinter.END, 1)
EditBox_1.grid(column=1,row=4)

Static_3 = tkinter.Label(text=u'二値化に用いる域値(%)', font=font)
Static_3.grid(column=0,row=5,sticky=tkinter.W, padx=20)

EditBox_2 = tkinter.Entry(width=5, font=font)
EditBox_2.insert(tkinter.END, 5)
EditBox_2.grid(column=1,row=5)

Static_4 = tkinter.Label(text=u'二値化に用いるチャンネル(0:赤,1:緑,2:青)', font=font)
Static_4.grid(column=0,row=6,sticky=tkinter.W, padx=20)

EditBox_3 = tkinter.Entry(width=5, font=font)
EditBox_3.insert(tkinter.END, 0)
EditBox_3.grid(column=1,row=6)


Val1 = tkinter.BooleanVar()
Val1.set(False)
CheckBox1 = tkinter.Checkbutton(text=u"免疫染色画像を使用", variable=Val1, font=font)
CheckBox1.grid(column=1,row=7)
    
Button_2 = tkinter.Button(text=u'3.二値化画像を確認する', width=30, font=font)
Button_2.bind("<Button-1>",pre_check) 
Button_2.grid(column=1,row=8)

Static_00 = tkinter.Label(text=u'')
Static_00.grid(column=0,row=9,sticky=tkinter.W, padx=20)

Static_5 = tkinter.Label(text=u'細胞と認識する最小面積', font=font)
Static_5.grid(column=0,row=10,sticky=tkinter.W, padx=20)

EditBox_4 = tkinter.Entry(width=5, font=font)
EditBox_4.insert(tkinter.END, 50)
EditBox_4.grid(column=1,row=10)

Static_6 = tkinter.Label(text=u'切り出す画像の幅(px)', font=font)
Static_6.grid(column=0,row=11,sticky=tkinter.W, padx=20)

EditBox_5 = tkinter.Entry(width=5, font=font)
EditBox_5.insert(tkinter.END, 50)
EditBox_5.grid(column=1,row=11)

Static_7 = tkinter.Label(text=u'切り出す画像の高さ(px)', font=font)
Static_7.grid(column=0,row=12,sticky=tkinter.W, padx=20)

EditBox_6 = tkinter.Entry(width=5, font=font)
EditBox_6.insert(tkinter.END, 50)
EditBox_6.grid(column=1,row=12)

Button_3 = tkinter.Button(text=u'4.画像の切り抜きを試す(10枚)', width=30, font=font)
Button_3.bind("<Button-1>",cell_crop_test) 
Button_3.grid(column=1,row=13)

Button_4 = tkinter.Button(text=u'5.画像の切り抜きを開始する', width=30, font=font)
Button_4.bind("<Button-1>",cell_crop) 
Button_4.grid(column=1,row=14)

Static_000 = tkinter.Label(text=u'')
Static_000.grid(column=0,row=15,sticky=tkinter.W, padx=20)

Static_8 = tkinter.Label(text=u'ファイルの名前', font=font)
Static_8.grid(column=0,row=16,sticky=tkinter.W, padx=20)

EditBox_7 = tkinter.Entry(width=30, font=font)
EditBox_7.insert(tkinter.END, "result")
EditBox_7.grid(column=1,row=16)

Button_4 = tkinter.Button(text=u'6.切り抜いた結果を保存する', width=30, font=font)
Button_4.bind("<Button-1>",save_cropped_pics) 
Button_4.grid(column=1,row=17)


root.mainloop()
