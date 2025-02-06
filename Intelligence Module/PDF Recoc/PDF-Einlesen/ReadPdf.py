# Imports
import argparse
from pdf2image import convert_from_path
import cv2
import numpy as np
import os
import pytesseract
import fdb
import logging
import configparser
import sys
from sys import argv
from PIL import Image
from logging.handlers import RotatingFileHandler


# Root Path
rootPath = "Initialized :)"

# Extract Root Dir
if getattr(sys, 'frozen', False):  # Check if it is running under PyInstaller
    # Running as an executable
    rootPath = os.path.dirname(sys.executable)
else:
    # Running under Python
    rootPath = os.path.dirname(os.path.abspath(__file__))

# Configurations --------------------------
config = configparser.ConfigParser()
config.read(rootPath.rsplit('\\', 1)[0] + '\\conf.ini')
# ------------------------------------------

# Logger setup ----------------------------
logger = logging.getLogger('rotating_logger')
logger.propagate = False
# Global log level based on configuration
match config['ReadPdf']['logLevel']:
    case 'DEBUG':
        logger.setLevel(logging.DEBUG)
    case 'INFO':
        logger.setLevel(logging.INFO)

# Rotating log handler with max file size of 5 MB
handler = RotatingFileHandler(rootPath.rsplit('\\', 1)[0] + config['ReadPdf']['logFile'], maxBytes=5*1024*1024, backupCount=3)

# Log format -> Time -> Level -> Message
formatter = logging.Formatter('%(asctime)s -  %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Console handler for logging to stdout
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(handler)
# ------------------------------------------


# Initialize Variables
# Read arguments----------
argParser = argparse.ArgumentParser(prog='ReadPdf', description='Reads the specified PDF File and Convertes it to images without the Text and creates a database where it stores these texts')
argParser.add_argument("--FileMode", "-fM")
argParser.add_argument("--FilePath", "-fP")
argParser.add_argument("--Rotation", "-r")
argParser.add_argument("--UsedPages", "-uPa", nargs='+')
argParser.add_argument("--UsedDir", "-uD")
argParser.add_argument("--UsedPdf", "-uPd", nargs='+')
argParser.add_argument("--UpdateExisting", "-uE", action='store_true')

args = argParser.parse_args()

fileMode = args.FileMode

# File mode: Single
if fileMode == 'single':    
    filePath = args.FilePath      # Path to the PDF file to convert
    rotation = args.Rotation      # Rotation direction: rr for clockwise, rl for counter-clockwise
    usedPages = args.UsedPages    # Pages to process
    usedPages.sort()
# File mode: Multi
if fileMode == 'multi':
    rotation = args.Rotation      # Rotation direction: rr for clockwise, rl for counter-clockwise
    usedDir = args.UsedDir        # Directory containing the PDFs to convert
    usedPdf = args.UsedPdf        # List of PDF file names
    filePath = usedDir            # Ensures the conversion loop runs correctly in multi mode
# ------------------------

# Paths and Directories -------------------------------------------------
logger.debug("Root Path: " + rootPath)
outputPath = rootPath + "\\" + config['ReadPdf']['outputPath'] + "\\"

# Initialize folders if they don't exist
if not os.path.exists(outputPath + filePath.split('.',1)[0]):
    os.makedirs(outputPath + filePath.split('.',1)[0]) 
    logger.debug(f"New directory '{outputPath + filePath.split('.', 1)[0]}' created!")

# Load additional paths
tmpPath = config['ReadPdf']['tmpPath']
dirPath = rootPath.rsplit('\\', 1)[0] + config['ReadPdf']['pdfRootPath'] + "\\"
# ----------------------------------------------------------------------


# Initialize Database --------------------------------------------------
# Define database path
planId = 1
db_path = rootPath.rsplit('\\', 1)[0] + "\TEXTSDB.fdb"
logger.debug(db_path)
api = rootPath.rsplit('\\', 1)[0] + config['db']['pathToDLL']
fdb.load_api(api)

# Database credentials
db_User = "HeliosUser"
db_Password = "class"

# Create a new database if one does not exist
if not os.path.exists(db_path):
    # No database found, attempt creation
    try:
        con = fdb.create_database(f"CREATE DATABASE '{db_path}' user '{db_User}' password '{db_Password}'")
        con.close()
    except:
        logger.exception("Could not create database")
    logger.info(f"Database created at: {db_path}")

    # Connect to the database
    try:
        con = fdb.connect(dsn=db_path, user=db_User, password=db_Password, fb_library_name=api)
        cur = con.cursor()
    except:
        logger.exception("Database connection failed!")
    logger.info("Database connection successful!")

    # Initalise tables in the new Database
    cur.execute(f"""CREATE TABLE FIRE_PLANS (
                    planId INTEGER PRIMARY KEY,
                    name VARCHAR(40)
                    );    
    """)
    cur.execute(f"""CREATE TABLE PAGES (
                    pageId INTEGER PRIMARY KEY,
                    planId INTEGER,
                    FOREIGN KEY (planId) REFERENCES FIRE_PLANS(planId)
                    );
    """)
    cur.execute(f"""CREATE TABLE CONVERTED_TEXTS (
                    id INTEGER PRIMARY KEY,
                    text VARCHAR(40),
                    cordLeft INTEGER,
                    cordTop INTEGER,
	                pageId INTEGER,
	                FOREIGN KEY (pageId) REFERENCES PAGES(pageId)
                    );
    """)
    con.commit()
    cur.execute(f"""CREATE GENERATOR GEN_CONVERTED_TEXTS_ID;""")
    cur.execute("""CREATE TRIGGER TRG_CONVERTED_TEXTS_BI FOR CONVERTED_TEXTS
                    ACTIVE BEFORE INSERT POSITION 0
                    AS
                    BEGIN
                        IF (NEW.ID IS NULL) THEN
                            NEW.ID = GEN_ID(GEN_CONVERTED_TEXTS_ID, 1);
                    END;
    """)
    cur.execute(f"""CREATE GENERATOR GEN_PAGE_ID;""")
    cur.execute(f"""CREATE TRIGGER TRG_PAGES_BI FOR PAGES
                    ACTIVE BEFORE INSERT POSITION 0
                    AS
                    BEGIN
                        IF (NEW.PAGEID IS NULL) THEN
                            NEW.PAGEID = GEN_ID(GEN_PAGE_ID, 1);
                    END;
    """)
    cur.execute(f"""CREATE GENERATOR GEN_PLAN_ID;""")
    cur.execute(f"""CREATE TRIGGER TRG_FIRE_PLANS_BI FOR FIRE_PLANS
                    ACTIVE BEFORE INSERT POSITION 0
                    AS
                    BEGIN
                        IF (NEW.PLANID IS NULL) THEN
                    NEW.PLANID = GEN_ID(GEN_PLAN_ID, 1);
                    END;
    """)
    con.commit()
    
else:
    # Existing database found
    logger.info(f"Database already exists at: {db_path}")

    # Connect to the database
    try:
        con = fdb.connect(dsn=db_path, user=db_User, password=db_Password, fb_library_name=api)
        cur = con.cursor()
    except:
        logger.exception("Database connection failed!")
    logger.info("Database connection successful!")

# Prepare the Database for a new Pdf
if args.UpdateExisting:
    logger.error("Not yet implemented")
else:
    fire_plan_name = filePath.split('.',1)[0]

    con.commit()
    # Insert new Fire Plan into the database
    cur.execute("INSERT INTO FIRE_PLANS (name) VALUES (?) RETURNING planId", (fire_plan_name,))

    # Fetch the generated planId
    planId = cur.fetchone()[0]
        
    # Log the inserted planId
    logger.info(f"Inserted new Fire Plan with generated planId: {planId}")
    con.commit()



# Pytesseract
pytesseract.pytesseract.tesseract_cmd = config['tesseract']['pathToTesseract']
# ---------------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------
# Recognize all texts in the image and store them in the database, texts are covered with white rectangles
def TextRecocnition(image, binary, cur, rotation, id):
    # Use Tesseract to extract all text
    data = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT)
    logger.debug(f"{len(data)} words detected!")

    # Process all detected texts
    for j in range(len(data['text'])):
        if int(data['conf'][j]) > 20 and data['text'][j].strip() != "":
            # Draw a white rectangle over the text
            x, y, w, h = data['left'][j], data['top'][j], data['width'][j], data['height'][j]
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), thickness=-1)

            # Write the recognized text into the database
            cur.execute("INSERT INTO CONVERTED_TEXTS (text, cordLeft, cordTop, pageId) VALUES (?, ?, ?, ?)", (data['text'][j], data['left'][j], data['top'][j], id))
    return image
# ---------------------------------------------------------------------------------------------------------------------



# ---------------------------------------------------------------------------------------------------------------------
# Takes the read images and processes them
def ConversionLoop(pages):
    pageId = 0

    # Main conversion loop
    for i, page in enumerate(pages):
        global planId
        cur.execute("INSERT INTO PAGES (planId) VALUES (?) RETURNING pageId", (planId,))
        pageId = cur.fetchone()[0]

        # Save the page as a temporary image
        image_path = rootPath + "\\" + tmpPath + f"temp_page_{i}.png"
        page.save(image_path, "PNG")
        image = cv2.imread(image_path, 0)

        # Convert the image to binary for text recognition
        _, binary = cv2.threshold(image, 150,255, cv2.THRESH_BINARY_INV)

        # Handle rotation as specified
        if(rotation == 'rl'):
            logger.debug("Rotating image 90 degrees counterclockwise")
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        if(rotation == 'rr'):
            logger.debug("Rotating image 90 degrees clockwise")
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        # Text recognition
        image = TextRecocnition(image,binary, cur, "nr", pageId)

        # Apply Gaussian blur and thresholding
        blurred = cv2.GaussianBlur(image, (9,9), 0)
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

        # Save the processed images
        logger.info(f"Image saved at: {outputPath}{filePath.split('.',1)[0]}/Converted{i}.png") 
        cv2.imwrite(f"{outputPath}{filePath.split('.',1)[0]}/Converted{i}.png", thresh)
        cv2.imwrite(f"{outputPath}{filePath.split('.',1)[0]}/Blurred{i}.png", blurred)

        # Stop processing after the required pages in single mode
        if(fileMode == "single"):
            if(len(usedPages) == 0):
                break

# File Modes ----------------------------------------------------------------------------------------------------------
# Single mode ---------------------------------------------------------------------------------------------------------
if fileMode == 'single':
    logger.info(f"Reading PDF {filePath} in single file mode")
    logger.info(f"Converting {len(usedPages)} pages!")
    logger.debug(f"Directory path: {dirPath + filePath}")

    # Convert PDF to PNG
    logger.info("Reading PDF ...")
    temp = convert_from_path(
        str(dirPath) + str(filePath),
        300,
        poppler_path = config['Poppler']['pathToPoppler']
    )
    logger.info("PDF successfully read!")

    # Process only the specified pages
    pages = [temp[int(i)] for i in usedPages]
    # Start the conversion process
    ConversionLoop(pages)

    

# Multi ---------------------------------------------------------------------------------------------------------------
if fileMode == 'multi':
    logger.info("Reading PDFs in multi-file mode")

    # Convert PDFs to PNG
    i = 0
    pages = []
    for pdf in usedPdf:
        temp = convert_from_path(
            str(dirPath) + str(usedDir) + "\\" + pdf,
            300,
            poppler_path = config['Poppler']['pathToPoppler']
        )

        # Load first page of each PDF into the array
        pages.append(temp[0])
   
    # Start the conversion process
    ConversionLoop(pages)

con.commit()