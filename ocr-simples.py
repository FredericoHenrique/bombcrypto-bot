import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\Tesseract.exe"

# Lendo arquivo gerado
img = cv2.imread(r"D:\Estudos\UDEMY\GIT\bombcrypto-bot\targets\saldo1.png")
cv2.imshow("res",img)

cv2.waitKey(0)
cv2.destroyAllWindows()

# Print resultado
# print(pytesseract.image_to_string(img))