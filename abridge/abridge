import cv2
import os

def vconcat_resize(img_list):

    w_min = min(img.shape[1] for img in img_list)
    resized = [cv2.resize(img,(w_min, int(img.shape[0] * w_min / img.shape[1])),interpolation = cv2.INTER_AREA) for img in img_list]     
    return cv2.vconcat(resized)  

def load_images(path):
    images = []
    for f in os.listdir(path):
        img = cv2.imread(os.path.join(path,f))
        images.append(img)
    return images

path = 'input/'
abridged = vconcat_resize(load_images(path))
cv2.imwrite('abridged.png', abridged)
