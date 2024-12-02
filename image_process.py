import cv2
import os
import yaml

# 全局变量，用于鼠标交互
roi = []

# 鼠标事件回调函数
def click_and_crop(event, x, y, flags, param):
    global image, roi
    image2 = image.copy()

    if event == cv2.EVENT_LBUTTONDOWN:         #左键点击
        roi = [(x,y)]
        cv2.circle(image2, roi[0], 10, (0,255,0), 3)
        cv2.imshow('Select ROI', image2)
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):               #按住左键拖曳
        cv2.rectangle(image2, roi[0], (x,y), (0,0,255), 3)
        cv2.imshow('Select ROI', image2)
    elif event == cv2.EVENT_LBUTTONUP:         #左键释放
        roi.append((x,y))
        cv2.rectangle(image2, roi[0], roi[1], (0,255,0), 3) 
        cv2.imshow('Select ROI', image2)

# 主函数
def main(image_folder, output_folder):
    global image

    # 检查输出文件夹是否存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 选择一个图片来定义裁剪区域
    example_image_path = None
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            example_image_path = os.path.join(image_folder, filename)
            break

    if not example_image_path:
        print("未找到图片，请检查文件夹路径！")
        return

    # 加载示例图片
    image = cv2.imread(example_image_path)
    print(f"正在处理示例图片: {example_image_path}")
    print('-------------------------------------------------')
    print("按回车键(Enter)进行确认, 在确认前可以重复进行框选")
    print('-------------------------------------------------')
    cv2.namedWindow("Select ROI")
    cv2.setMouseCallback("Select ROI", click_and_crop)
    cv2.imshow('Select ROI', image)
    cv2.waitKey(0)

    # 批量裁剪图片
    x1, y1 = roi[0]
    x2, y2 = roi[1]
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, filename)
            image = cv2.imread(image_path)

            # 裁剪区域
            cropped = image[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
            
            # 保存裁剪结果
            output_path = os.path.join(output_folder, f"cropped_{filename}")
            cv2.imwrite(output_path, cropped)
            print(f"已裁剪并保存图片: {output_path}")

    print("所有图片裁剪完成！")


if __name__ == "__main__":
    # 设置参数
    with open("config.yml", "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        image_folder1 = config['process_path']['image_folder'] # 替换为你的图片文件夹路径
        output_folder = config['process_path']['output_folder'] # 替换为裁剪后的图片保存路径

    main(image_folder1, output_folder)
