#coding:utf-8

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

img =   # 填空，读取图片1.jpg
gray_image =   # 填空，图片彩色图转灰度图

fig, ax = plt.subplots(1, 2, figsize=(16, 8))
fig.tight_layout()

ax[0].imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
ax[0].set_title("Original")

ax[1].imshow(cv.cvtColor(gray_image, cv.COLOR_BGR2RGB))
ax[1].set_title("Grayscale")
plt.show()
