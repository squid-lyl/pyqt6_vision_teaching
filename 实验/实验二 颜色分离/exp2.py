#coding:utf-8

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
img = cv.imread('2.jpg') # 读取2.jpg

b, g, r = # 填空，使用split函数对图片img进行通道分离


# 展示结果
fig, ax = plt.subplots(1, 3, figsize=(16, 8))
fig.tight_layout()

ax[0].imshow(cv.cvtColor(r, cv.COLOR_BGR2RGB))
ax[0].set_title("Red")

ax[1].imshow(cv.cvtColor(g, cv.COLOR_BGR2RGB))
ax[1].set_title("Green")

ax[2].imshow(cv.cvtColor(b, cv.COLOR_BGR2RGB))
ax[2].set_title("Blue")



plt.show()