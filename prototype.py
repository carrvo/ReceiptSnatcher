import pytesseract
import cv2
import imutils
original = cv2.imread('Test receipt.pdf')#'example-receipt.jpg')
image = original.copy()
image = imutils.resize(image, width=500)
ratio = original.shape[1] / float(image.shape[1])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5,), 0)
edged = cv2.Canny(blurred, 75, 200)
#cv2.imshow("original", original)
#cv2.imshow("edged", edged)
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
sorted_cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
for c in sorted_cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
            receiptCnt = approx
            break

from imutils.perspective import four_point_transform
receipt = four_point_transform(original, receiptCnt.reshape(4, 2) * ratio)
#cv2.imshow("Receipt Transform", imutils.resize(receipt, width=500))
options = "--psm 4"
print(pytesseract.image_to_string(cv2.cvtColor(receipt, cv2.COLOR_BGR2RGB), config=options))
import tesserocr
api = tesserocr.PyTessBaseAPI()
api.SetImageBytes(receipt.tobytes(), receipt.shape[1], receipt.shape[0], 1, receipt.shape[1])
print('api.GetUTF8Text()')
print('cv2.imencode')
print('cv2.dilate')
print('cv2.erode')
print('Imgproc.morphologyEx(src, dst, Imgproc.MORPH_TOPHAT, kernel);')
print('HoughLines(image, lines, rho, theta, threshold)')
print('equalizeHist(src, dst)')

#Test receipt.pdf

