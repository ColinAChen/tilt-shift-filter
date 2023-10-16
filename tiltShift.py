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

displayScale = 2.5


def showImage(image, title='image', resize=False):
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
def tiltShift(image, center=None, topRow=None, bottomRow=None):
    print(topRow)
    print(bottomRow)
    if topRow is not None:
        topRow = int(topRow * displayScale)
    if bottomRow is not None:
        bottomRow = int(bottomRow * displayScale)
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

    if topRow is None:
        topRow = center
    if bottomRow is None:
        bottomRow = center

    middle = image[topRow-rowBuckets:bottomRow+rowBuckets,:]

    
    # iterate from center until we reach an edge in both directions
    outImage = np.zeros(image.shape)
    outImage[topRow-rowBuckets:bottomRow+rowBuckets,:] = middle
    #showImage(middle)

    # iterate towards 0
    midRow = topRow - (2*rowBuckets)
    startRow = max(0,midRow-rowBuckets)
    endRow = midRow + rowBuckets
    kernel = (5,5)

    # crop the image by bucket + kernel size so that each pixel that gets blurred is sampled from the full kernel
    # at some point, put this one into the loop with the same bounds checking. For now, I am assuming the middle will not be an edge
    blurImage = cv2.GaussianBlur(image[startRow-kernel[0]:endRow+kernel[0],:], kernel,0)
    outImage[startRow:endRow,:] = blurImage[kernel[0]:kernel[0]+(2*rowBuckets),:]
    while (endRow > 0):
        #print(startRow)
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

        # all this noise to handle the last bucket which might not have the same nnumber of rows
        startCrop = max(0, startRow-kernel[0])
        endCrop = endRow + kernel[0]
        startDiff = startRow-startCrop
        blurImage = cv2.GaussianBlur(image[startCrop:endCrop,:], kernel ,0)
        outImage[startRow:endRow,:] = blurImage[startDiff:len(blurImage)-kernel[0],:]


    # iterate towards end
    midRow = bottomRow + (2*rowBuckets)
    startRow = midRow - rowBuckets
    endRow = min(midRow+rowBuckets, rows)
    #print(endRow)
    kernel = (5,5)
    blurImage = cv2.GaussianBlur(image[startRow-kernel[0]:endRow+kernel[0],:], kernel,0)
    outImage[startRow:endRow,:] = blurImage[kernel[0]:kernel[0]+(2*rowBuckets),:]
    while (endRow < rows):
        midRow = midRow + (2*rowBuckets)
        startRow = midRow - rowBuckets
        endRow = min(midRow+rowBuckets, rows)
        #print(endRow)
        if endRow > rows:
            break

        kernel = (kernel[0] + kernelStep, kernel[0] + kernelStep)

        startCrop = startRow-kernel[0]
        endCrop = min(endRow+kernel[0],rows)
        endDiff = endCrop - endRow
        blurImage = cv2.GaussianBlur(image[startCrop:endCrop,:], kernel ,0)
        outImage[startRow:endRow,:] = blurImage[kernel[0]:len(blurImage) - endDiff,:]

    # decide on number of blur buckets

    # break image into blur buckets

    # blur each bucket based on distance from center

    # reassemble the blurred images

    return outImage

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not

topRow = None
bottomRow = None


def getCenter(image):
    refPt = []
    cropping = False


    
    rows, cols, channels = image.shape
    resize = (int(cols/displayScale), int(rows/displayScale))
    resizeImage = cv2.resize(image, resize)
    displayImage = resizeImage.copy()

    def click_and_crop(event, x, y, flags, param):
        global topRow, bottomRow
        # grab references to the global variables
        #global refPt, cropping
        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being
        # performed
        if event == cv2.EVENT_MOUSEMOVE:
            resizeImage = displayImage.copy()
            #print((x,y))
            cv2.line(resizeImage, (0,y), (cols,y), (255,0,0))
            #topRow = y
        if event == cv2.EVENT_LBUTTONDOWN:
            #refPt = [(x, y)]
            
            topRow = y
            print('set top row',(x,y))
            #cropping = True
        # check to see if the left mouse button was released
        if event == cv2.EVENT_RBUTTONDOWN:
            bottomRow = y
            print('set bottom row',(x,y))
        # elif event == cv2.EVENT_LBUTTONUP:
        #     # record the ending (x, y) coordinates and indicate that
        #     # the cropping operation is finished
        #     refPt.append((x, y))
        #     cropping = False
        #     # draw a rectangle around the region of interest
        #     cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
        #     cv2.imshow("image", image)

    
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)
    # keep looping until the 'q' key is pressed
    while True:
        # display the image and wait for a keypress
        cv2.imshow("image", resizeImage)
        key = cv2.waitKey(1) & 0xFF
        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            image = clone.copy()
        # if the 'c' key is pressed, break from the loop
        elif key == ord("c"):
            break
    #return topRow, bottomRow
def main():

    if not os.path.isdir(tiltPath):
        os.mkdir(tiltPath)
    for path in os.listdir(imagePath):
        readPath = os.path.join(imagePath, path)
        print(readPath)
        image = cv2.imread(readPath)
        getCenter(image)

        tiltImage = tiltShift(image, topRow=topRow, bottomRow=bottomRow)
        writePath = os.path.join(tiltPath, path)
        cv2.imwrite(writePath, tiltImage)

        
if __name__=='__main__':
    main()