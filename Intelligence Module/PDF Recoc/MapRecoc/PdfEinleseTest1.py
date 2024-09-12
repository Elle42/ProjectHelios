from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Init All
pages = convert_from_path(
    "TestFiles/MFH-RF1-Brandschutzplan.pdf",
    300,
    poppler_path=r"C:\Program Files\poppler-24.07.0\Library\bin",
) 
for i, page in enumerate(pages):
    # Temp IMG
    image_path = f"temp_page_{i}.png"
    page.save(image_path, "PNG")
    # OCV
    image = cv2.imread(image_path, 0)  # 0 means load in grayscale

    # Door Detect
    # template = cv2.imread('TestFiles/Door.png')
    # w, h = template.shape[:-1]

    # res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    # threshold = .8
    # loc = np.where(res >= threshold)
    # for pt in zip(*loc[::-1]):  # Switch columns and rows
    #     cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    # cv2.imwrite('result.png', image)

    # Text Detect
    binary = cv2.threshold(image, 150,255, cv2.THRESH_BINARY_INV)

    #kernel = np.ones((1, 1), np.uint8)
    #cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    for j in range(len(data['text'])):
    # Filter out empty strings or low-confidence detections
        if int(data['conf'][j]) > 20 and data['text'][j].strip() != "":
            # Extract the word's bounding box coordinates

            x, y, w, h = data['left'][j], data['top'][j], data['width'][j], data['height'][j]
        
            # Draw a rectangle around each detected word
            cv2.rectangle(image, (x, y), (x + w, y + h), 255, -1)
    
    cv2.imwrite(f"TestImages/FilteredText{i}.png", image)
    #----------------------

    # Edge Detect
    blurred = cv2.GaussianBlur(image, (3,3), 0)

    _, thresh = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY)
    cv2.imwrite(f"TestImages/Threshold{i}.png", thresh)

    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
    # Lines Detec
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=0
    )
    # Init
    walls = np.zeros_like(image)
    # Filter + Draw
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Draw
            cv2.line(
                walls, (x1, y1), (x2, y2), 255, 2
            )  # 255 is white, 2 is the thickness
    # Save
    cv2.imwrite(f"TestImages/walls_only_{i}.png", walls)
