import cv2
import numpy as np
import os

def slice(img, f, x):

    arr = np.array(cv2.bitwise_not(img))
    height, width = arr.shape
    max_intensity = np.max(arr)
    threshold = max_intensity * 0.01

    start = 0
    cutoff = False
    slice_count = 0

    full_page = np.count_nonzero(np.sum(arr,axis=1) > width * threshold) == 0

    if full_page :
    
        cv2.imwrite(f'slices/{f}.{x}',img)
    
    else:
    
        for i in range(height):            
            
            row_sum = np.sum(arr[i])          
            
            if row_sum == 0 and not cutoff: # start of slice         
                start = i            
            
            elif row_sum > width * threshold and not cutoff: # contents of slice            
                cutoff = True            
            
            elif (row_sum == 0 or i == height - 1) and cutoff: # end of slice            
                trim = np.where(np.sum(arr[start:i],axis=0) > height * threshold)
                cv2.imwrite(f'slices/{f}_{slice_count}.{x}',image[start:i-1,trim[0][0]:trim[0][-1]+1])                
                slice_count += 1                
                start = i
                cutoff = False

path = 'pages/'

for f in os.listdir(path):
    image = cv2.imread(os.path.join(path,f))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fname, ext = f.split('.')
    slice(gray, fname, ext)
