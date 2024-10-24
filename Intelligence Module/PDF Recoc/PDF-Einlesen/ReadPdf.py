# Import All
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
rootPath = "Angelegt :)"

# Extract Root Dir
if getattr(sys, 'frozen', False):  # Check if it is running under Pyinstaller
    # Running as EXE
    rootPath = os.path.dirname(sys.executable)
else:
    # Running under Python
    rootPath = os.path.dirname(os.path.abspath(__file__))

print(rootPath)

# Configs --------------------------
config = configparser.ConfigParser()
config.read(rootPath + '\\conf.ini')
# ----------------------------------

# Logger ------------------------------------
logger = logging.getLogger('rotating_logger')
logger.propagate = False
# Global Log Level
match config['general']['logLevel']:
    case 'DEBUG':
        logger.setLevel(logging.DEBUG)
    case 'INFO':
        logger.setLevel(logging.INFO)
# Max File Size 5 mb then rotate
handler = RotatingFileHandler(config['general']['logFile'], maxBytes=5*1024*1024, backupCount=3)
# Formatter of the Log -> Adds Time -> Level -> Message
formatter = logging.Formatter('%(asctime)s -  %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(handler)
# ------------------------------------------


# Init All
# Read Args----------
fileMode = argv[1]
# File Mode Single
if fileMode == 'single':    #
    filePath = argv[2]      # Name of the File to Convert, has to be found in the dir Folder
    rotation = argv[3]      # rr Counter and rl Clockwise
    usedPages = argv[4:]    # Which pages shoulb be used -> !They have to be sorted!
# File Mode Multi
if fileMode == 'multi':
    rotation = argv[2]      # rr Counter and rl Clockwise
    usedDir = argv[3]       # All Pdfs should bi in Folder in the Dir folder
    usedPdf = argv[4:]      # Names of all used Pdfs
    filePath = usedDir      # Correction that the Conversion Loop runs in Multi mode
# -------------------

# Paths and Directories ------------------------------------------------
logger.debug("Root Path: " + rootPath)
outputPath = rootPath + "\\" + config['general']['outputPath'] + "\\"
# Initalize Folders
if not os.path.exists(outputPath + filePath.split('.',1)[0]):
    os.makedirs(outputPath + filePath.split('.',1)[0]) 
    logger.debug("New Directory \'" + outputPath + filePath.split('.',1)[0] + "\' created!")
# Load Paths
tmpPath = config['general']['tmpPath']
dirPath = rootPath + f"\PlanPdf\\"
# ----------------------------------------------------------------------

# Initialyze Database --------------------------------------------------
# Load Paths
db_path = rootPath + "\\" + config['general']['outputPath'] + "\\" + filePath.split('.',1)[0] + "\TEXTSDB.fdb"
logger.debug(db_path)
api = config['db']['pathToDLL']
fdb.load_api(api)
# Users
db_User = "HeliosUser"
db_Password = "class"
# If none exists it should create a new Database
if not os.path.exists(db_path):
    # No Database Found
    try:
        con = fdb.create_database(f"CREATE DATABASE '{db_path}' user '{db_User}' password '{db_Password}'")
        con.close()
    except:
        logger.exception("Couldnt create database")
    logger.info(f"Database createt at: {db_path}")
else:
    # An Existing Database was found
    logger.info(f"Database already exists at: {db_path}")
# Db Connection
con = fdb.connect(dsn=db_path, user=db_User, password=db_Password, fb_library_name=api)
cur = con.cursor()
logger.info("Database Connection succesful!")
pytesseract.pytesseract.tesseract_cmd = config['tesseract']['pathToTesseract']
# ----------------------------------------------------------------------



# ---------------------------------------------------------------------------------------------------------------------
# Recocnise all texts in the image and store them in the Database, The texts are Coverd up with white rectangles
def TextRecocnition(image, binary, cur, rotation, i):
    # Use the AI to Extract all Texts
    data = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT)
    logger.debug("There were " + str(len(data)) + " words found!")

    # Alle erkannten Texte verarbeitet
    for j in range(len(data['text'])):
        if int(data['conf'][j]) > 20 and data['text'][j].strip() != "":
            # Rechteck über den Text Zeichnen
            x, y, w, h = data['left'][j], data['top'][j], data['width'][j], data['height'][j]
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), thickness=-1)

            # Erkannten Text in die Datenbank schreiben
            cur.execute("INSERT INTO Converted_" + str(i) + "(id, text, cordLeft, cordTop) VALUES (?, ?, ?, ?)", 
                        (j, data['text'][j], data['left'][j], data['top'][j]))
    return image
# ---------------------------------------------------------------------------------------------------------------------



# ---------------------------------------------------------------------------------------------------------------------
# Takes the read Images and Processes them
def ConversionLoop(pages):
    # Main Loop
    for i, page in enumerate(pages):
        # Save the page as a temporary image
        image_path = rootPath + "\\" + tmpPath + f"temp_page_{i}.png"
        page.save(image_path, "PNG")
        image = cv2.imread(image_path, 0)
        # For the Image Recognition software -> Brings the image in a binary format
        _, binary = cv2.threshold(image, 150,255, cv2.THRESH_BINARY_INV)

        # Table In der Datenbank für die Derzeitige Seite erstellen     (!IF NOT EXISTS funktioniert in der Datenbank nicht!)
        # Check if table exists before dropping it
        table_name = "CONVERTED_" + str(i)
        cur.execute(f"SELECT 1 FROM rdb$relations WHERE rdb$relation_name = '{table_name.upper()}'")
        
        # If the table exists, drop it
        if cur.fetchone():
            logger.debug("Table CONVERTED_" + str(i) + " already exists -> Dropped!")
            cur.execute(f"DROP TABLE {table_name}")
        
        # Create the new table
        cur.execute(f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                text VARCHAR(40),
                cordLeft INTEGER,
                cordTop INTEGER
            )
        """)
        logger.debug(f"New table CONVERTED_{str(i)} created!")
        con.commit()

        # Abfrage wie Rotation behandelt werden soll
        if(rotation == 'rr'):
            logger.debug("Rotation -> rr")
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        if(rotation == 'rl'):
            logger.debug("Rotation -> rl")
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        # Text Recognition
        # writes int database cur
        image = TextRecocnition(image,binary, cur, "nr", i)

        # Blurring und Thresholding
        blurred = cv2.GaussianBlur(image, (9,9), 0)

        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

        # Saves the Converted Images
        logger.info(f"Saved at: {outputPath}{filePath.split('.',1)[0]}\Converted{str(i)}.png") 
        cv2.imwrite(f"{outputPath}{filePath.split('.',1)[0]}/Converted{i}.png", thresh)
        cv2.imwrite(f"{outputPath}{filePath.split('.',1)[0]}/Blurred{i}.png", blurred)

        # If all needed pages are read break
        if(fileMode == "single"):
            if(len(usedPages) == 0):
                break



# Different File Modes ------------------------------------------------------------------------------------------------
# Single --------------------------------------------------------------------------------------------------------------
if fileMode == 'single':
    logger.info(f"Read Pdf {filePath} in file mode single!")
    logger.info("There will be  " + str(len(usedPages)) + " pages converted!")
    logger.debug(str(dirPath) + str(filePath))

    # Convert Pdf int .png
    logger.info("Read Pdf ... ... ...")
    temp = convert_from_path(
        str(dirPath) + str(filePath),
        300,
        poppler_path = config['Poppler']['pathToPoppler']
    )
    logger.info("Pdf succesfully read!")

    # Only used Pages will be processed
    pages = [temp[int(i)] for i in usedPages]
    # Start conversion
    ConversionLoop(pages)

    

# Multi ---------------------------------------------------------------------------------------------------------------
if fileMode == 'multi':
    logger.info("Read Pdfs in file mode multi!")

    # Convert Pdf into .png
    i = 0
    pages = []
    for pdf in usedPdf:
        temp = convert_from_path(
            str(dirPath) + str(usedDir) + "\\" + pdf,
            300,
            poppler_path = config['Poppler']['pathToPoppler']
        )

        # Load images into Array
        pages.append(temp[0])
   
    
    # Start conversion
    ConversionLoop(pages)