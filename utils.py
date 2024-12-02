import cv2
import numpy as np


def search_splitCol(src):
    h,w,c = src.shape
    # 0. 将图像转化为二值图像
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)
    # 1. 计算纵向梯度
    grad_col = np.gradient(binary)[1]
    grad_col = np.sum(grad_col, axis=0)
    # 2. 搜索纵向梯度为0的列
    mask = grad_col == 0
    idx_0 = np.where(mask)[0]
    # 3. 将所有梯度为0的列连接成片
    idx_1 = np.where(np.diff(idx_0) != 1)[0]
    # 4. 寻找纵向梯度为0的最大间隔所在地
    idx_2 = np.argmax(np.diff(idx_1))
    # 5. 获得分割列的序号
    idx_2 = int(idx_2+1)
    final_col = int(idx_0[idx_1[idx_2]] - 0.025 * w)

    return final_col

def search_splitRow(src, max_intervals = 15):
    h,w,c = src.shape
    # 0. 将图像转化为二值图像
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)
    # 1. 计算横向梯度
    grad_row = np.gradient(binary)[0]
    grad_row = np.sum(grad_row, axis=1)
    # print(grad_col)
    # 2. 搜索横向梯度为0的行
    mask = grad_row == 0
    idx_0 = np.where(mask)[0]
    # 3. 将所有梯度为0的行连接成片
    idx_1 = np.where(np.diff(idx_0) != 1)[0]
    # 4. 寻找横向梯度为0的最大间隔所在地
    idx_2 = np.where(np.diff(idx_1) >= max_intervals)[0]
    # 5. 获得分割列的序号
    final_rows = [int((idx_0[idx_1[idx]] + idx_0[idx_1[idx+1]]) / 2) for idx in idx_2]
    final_rows = [0] + final_rows + [h] if len(final_rows) == 5 else [0] + final_rows + [int(final_rows[-1] + 0.18*h)]

    return final_rows
