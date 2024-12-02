from paddleocr import PaddleOCR
from fuzzywuzzy import fuzz
import openpyxl
import glob
import os
import cv2
import yaml
import logging

from utils import search_splitCol, search_splitRow


# 管理家族成员的名单
class MemberLibrary:
    def __init__(self, input_path="Names.xlsx"):
        # 加载姓名簿
        sheet = openpyxl.load_workbook(filename=input_path)['names']
        self.uid = [cell.value for cell in sheet['A']][1:]
        self.initial_names = [cell.value for cell in sheet['B']][1:]
        self.match_strings = [cell.value for cell in sheet['C']][1:]
        self.real_names = [cell.value for cell in sheet['D']][1:]
        self.totalNum = len(self.uid)

    def get_matchString(self, idx):
        return self.match_strings[idx]

    def get_realName(self, idx):
        return self.real_names[idx]
    
    def get_totalNumber(self):
        return self.totalNum


if __name__ == '__main__':
    logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
    logging.disable(logging.WARNING)  # 关闭WARNING日志的打印
    
    # 0. 初始化
    # 从YAML文件加载配置
    with open("config.yml", "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        data_path = config['ocr_path']['data_path']
        save_path = config['ocr_path']['save_path']
    # 对象初始化
    memberLib = MemberLibrary()
    ocr_ch = PaddleOCR(lang='ch',
                       det_model_dir='models\\whl\\det\\ch\\ch_PP-OCRv4_det_infer',
                       rec_model_dir='models\\whl\\rec\\ch\\ch_PP-OCRv4_rec_infer')
    ocr_en = PaddleOCR(lang='en',
                       cls_model_dir='models\\whl\\cls\\ch_ppocr_mobile_v2.0_cls_infer',
                       det_model_dir='models\\whl\\det\\en\\en_PP-OCRv3_det_infer',
                       rec_model_dir='models\\whl\\rec\\en\\en_PP-OCRv4_rec_infer')
    
    # 2. 图像识别
    all_results = []
    # img_path_list = ['C:\\Users\\Admin\\Desktop\\OCR_Ninja3\\samples\\sample_0010.jpg'] # 手动输入测试
    img_path_list = glob.glob(os.path.join(data_path, '*.jpg')) + glob.glob(os.path.join(data_path, '*.png'))
    for img_path in sorted(img_path_list):
        src = cv2.imread(img_path)

        # 2.1 图像分割
        # 2.1.1 纵向左右切分
        midLine = search_splitCol(src)
        src_left = src[:, :midLine, :]
        src_right = src[:, midLine:, :]
        # 2.1.2 横向切分
        splitRows = search_splitRow(src_right)

        # 2.2 检测名字
        out_names = ocr_ch.ocr(src_left, cls=False, det=True)[0]
        ocr_names = [i[1][0] for i in out_names]

        # 2.3 检测分数
        # ocr_names = []
        ocr_scores = []
        for i in range(len(splitRows)-1):
            src_right_i = src_right[splitRows[i]:splitRows[i+1], :, :]

            out_scores = ocr_en.ocr(src_right_i, cls=True, det=False, bin=True)[0]
            ocr_scores.append(out_scores[0][0])
        
        # 3. 文本匹配
        final_names = []
        final_i = []
        for string1 in ocr_names:
            # 字符串模糊匹配
            max_similarity = 0
            for i in range(memberLib.get_totalNumber()):
                string2 = memberLib.get_matchString(i)
                similarity = fuzz.ratio(string1, string2)
                if similarity > max_similarity:
                    temp_name = memberLib.get_realName(i)
                    temp_i = i
                    max_similarity = similarity
            final_names.append(temp_name)
            final_i.append(temp_i)

        # 4. 结果输出
        final_scores = ocr_scores + [0] * (6 - len(ocr_scores))
        all_results.append(list(zip(final_names, final_scores)))
        print(final_names)
        print(final_scores)

    # 5. 保存结果
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Results"
    ws.append(["Name", "Score"])
    for result in all_results:
        for name, score in result:
            ws.append([name, score])
    wb.save(save_path)
