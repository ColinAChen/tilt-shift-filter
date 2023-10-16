import cv2
import numpy as np
import os
'''
Simulate tilt shift toy effect

Keep center (or subject) sharp
Progressively blur pixels in columns farther from the center



'''



'''
Smarter would be doing this effect based on depth

lines are super obvious, what can we do about this?
Smaller kernelstep, more buckets

Specify center/center region

Gaussian blur doesn't match lens blur
Can we use a non square kernel?

Non linear bucket size or kernel step as we go away from center

pixels near the edges of buckets are missing some pixels when getting blurred. Crop the bucket + blur region, then blur, then add only the bucket back to the final image






'''
imagePath = 'images/'
tiltPath = 'imagesTilt'




def showImage(image, title='image'):
    cv2.imshow(title,image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


'''
Blur image based on a row's distance from the center. 
Pixels in the same row will be blured the same amount. Rows farther from the center will be blurred more.

Arguments:
    image (numpy array as image) : image to be tilt shifted
    center (int) : center row, default will be the center row of the image

Returns:
    tiltShiftImage (numpy array as image) : simulated tilt shift image
'''
def tiltShift(image, center=None):
    kernelStep = 2

    rows, cols, channels = image.shape
    #print(image.shape)
    if center is None:
        center = int(rows/2)
    
    # calculate number of rows per bucket
    # total number of buckets = buckets * 2 + 1 (1 for center)
    # rows per buckets = total rows / total buckets
    buckets = 100
    rowBuckets = int((rows / ((buckets * 2) + 1)) / 2) # total number of buckets: buckets * 2 + 1

    middle = image[center-rowBuckets:center+rowBuckets,:]
    
    # iterate from center until we reach an edge in both directions
    outImage = np.zeros(image.shape)
    outImage[center-rowBuckets:center+rowBuckets,:] = middle
    #showImage(middle)

    # iterate towards 0
    midRow = center - (2*rowBuckets)
    startRow = max(0,midRow-rowBuckets)
    endRow = midRow + rowBuckets
    kernel = (5,5)

    # crop the image by bucket + kernel size so that each pixel that gets blurred is sampled from the full kernel
    # at some point, put this one into the loop with the same bounds checking. For now, I am assuming the middle will not be an edge
    blurImage = cv2.GaussianBlur(image[startRow-kernel[0]:endRow+kernel[0],:], kernel,0)
    outImage[startRow:endRow,:] = blurImage[kernel[0]:kernel[0]+(2*rowBuckets),:]
    while (endRow > 0):
        print(startRow)
        # find the middle row of the current bucket
        midRow = midRow - (2*rowBuckets)
        startRow = max(0,midRow-rowBuckets)
        endRow = midRow + rowBuckets
        if endRow < 0:
            break
        
        # increase the kernel size
        kernel = (kernel[0] + kernelStep, kernel[0] + kernelStep)
        #print(kernel)
        #showImage(image[startRow:endRow,:])
        startCrop = max(0, startRow-kernel[0])
        endCrop = endRow + kernel[0]
        startDiff = startRow-startCrop
        blurImage = cv2.GaussianBlur(image[startCrop:endCrop,:], kernel ,0)
        outImage[startRow:endRow,:] = blurImage[startDiff:len(blurImage)-kernel[0],:]


    # iterate towards end
    midRow = center + (2*rowBuckets)
    startRow = midRow - rowBuckets
    endRow = min(midRow+rowBuckets, rows)
    #print(endRow)
    kernel = (5,5)
    blurImage = cv2.GaussianBlur(image[startRow:endRow,:], kernel,0)
    outImage[startRow:endRow,:] = blurImage
    while (endRow < rows):
        midRow = midRow + (2*rowBuckets)
        startRow = midRow - rowBuckets
        endRow = min(midRow+rowBuckets, rows)
        #print(endRow)
        if endRow > rows:
            break

        kernel = (kernel[0] + kernelStep, kernel[0] + kernelStep)

        blurImage = cv2.GaussianBlur(image[startRow:endRow,:], kernel ,0)
        outImage[startRow:endRow,:] = blurImage

    # decide on number of blur buckets

    # break image into blur buckets

    # blur each bucket based on distance from center

    # reassemble the blurred images

    return outImage

def getCenter(image):
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)
    # keep looping until the 'q' key is pressed
    while True:
        # display the image and wait for a keypress
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF
        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            image = clone.copy()
        # if the 'c' key is pressed, break from the loop
        elif key == ord("c"):
            break
    # if there are two reference points, then crop the region of interest
    # from teh image and display it
    if len(refPt) == 2:
        roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
        cv2.imshow("ROI", roi)
        cv2.waitKey(0)
    # close all open windows
    cv2.destroyAllWindows()

    return roi
def main():

    if not os.path.isdir(tiltPath):
        os.mkdir(tiltPath)
    for path in os.listdir(imagePath):
        readPath = os.path.join(imagePath, path)
        print(readPath)
        image = cv2.imread(readPath)

        tiltImage = tiltShift(image)
        writePath = os.path.join(tiltPath, path)
        cv2.imwrite(writePath, tiltImage)

        
if __name__=='__main__':
    main()