# Import All
from pdf2image import convert_from_path
import cv2
import numpy as np
import os
import pytesseract
import fdb
import logging
import configparser
from sys import argv
from PIL import Image
from logging.handlers import RotatingFileHandler

# Configs
config = configparser.ConfigParser()
config.read('conf.ini')

# Logger
# Custom Logger
logger = logging.getLogger('rotating_logger')
logger.propagate = False
# Globales Log Level
match config['general']['logLevel']:
    case 'DEBUG':
        logger.setLevel(logging.DEBUG)
    case 'INFO':
        logger.setLevel(logging.INFO)

# Max File Size 5 mb dann rotaten
handler = RotatingFileHandler('PdfEinlese.log', maxBytes=5*1024*1024, backupCount=3)

# Formatirung des Logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(handler)

# Init All
# Read Args
filePath = argv[1]      # Name von zu Konvertierenden File, muss sowiso im $dirPath$ Vorhanden sein
fileMode = argv[2]      # Single bleibt fürn Anfang Standard
rotation = argv[3]      # rr Gegen- und rl mit dem Uhrzeigersinn
usedPages = argv[4:]    # Angabe welche Seiten der PDF Verarbeitet werden sollen, Angabe muss bereits in der Richtigen Reihenfolge sein


# Pfad der Anwendung
rootPath = argv[0].rsplit('\\', 1)[0]

# Initalize Folder
if not os.path.exists("Converted/" + filePath.split('.',1)[0]):
    os.makedirs("Converted/" + filePath.split('.',1)[0]) 
    logger.info('Directory ' + filePath.split('.',1)[0] + ' Created!')

# Pfade Laden
tmpPath = config['general']['tmpPath']
dirPath = rootPath + f"\PlanPdf\\"
db_path = rootPath + f"\Converted\\" + filePath.split('.',1)[0] + "\TEXTSDB.fdb"
api = config['db']['PathToDLL']
fdb.load_api(api)

#Users
db_User = "HeliosUser"
db_Password = "class"

if not os.path.exists(db_path):
    # Create the database if it doesn't exist
    con = fdb.create_database(f"create database '{db_path}' user '{db_User}' password '{db_Password}'")
    con.close()
    logger.info(f"Database created at {db_path}")
else:
    logger.info(f"Database already exists at {db_path}")


# Db Connection
con = fdb.connect(dsn=db_path, user=db_User, password=db_Password, fb_library_name=api)
cur = con.cursor()
logger.info("DB Verbindung wurde aufgebeaut!")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Texte im Bild erkennen, in einer datenbank mit den koordinaten abspeichern und Mit Rechtecken überdecken
def TextRecocnition(image, binary, cur, rotation, i):
    if rotation == "nr":
        # Mit KI Texte erkennen
        data = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT)

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

# Verschiedene File Modes Unterscheiden
if fileMode == 'single':
    logger.info("Pdf wird im FileMode Single aufgerufen")
    logger.info("Es werden insgesamt" + str(len(usedPages)) + " Seiten bearbeitet!")
    logger.debug(str(dirPath) + str(filePath))

    # Pdf Lesen
    pages = convert_from_path(
        str(dirPath) + str(filePath),
        300,
        poppler_path=r'C:\Program Files\poppler-24.07.0\Library\bin'
    )
    logger.info("PDF wurde gelesen!")

    # Main Loop
    for i, page in enumerate(pages):
        if(i == int(usedPages[0])):
            usedPages.pop(0)
            # Seite Als Bild zwischenspeichern
            image_path = tmpPath + f"temp_page_{i}.png"
            page.save(image_path, "PNG")
            image = cv2.imread(image_path, 0)

            # Das Erzeugte Temp in ein Binär Format bringen damit die text erkennung leichter funktioniert
            _, binary = cv2.threshold(image, 150,255, cv2.THRESH_BINARY_INV)

            # Table In der Datenbank für die Derzeitige Seite erstellen     (!IF NOT EXISTS funktioniert in der Datenbank nicht!)
            # Check if table exists before dropping it
            table_name = "CONVERTED_" + str(i)
            cur.execute(f"SELECT 1 FROM rdb$relations WHERE rdb$relation_name = '{table_name.upper()}'")
            
            # If the table exists, drop it
            if cur.fetchone():
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
            con.commit()

            # Abfrage wie Rotation behandelt werden soll
            if(rotation == 'rr'):
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            if(rotation == 'rl'):
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)


            # Den Gesamten Text in der Derzeitigen Seite Lesen
            # In die DatenBank schreiben
            image = TextRecocnition(image,binary, cur, "nr", i)

            # Speichern der Convertierten IMGs
            logger.info(f"Gespeichert Unter: Converted/{filePath.split('.',1)[0]}/Converted{i}.png")
            if not os.path.exists("Converted/" + filePath.split('.',1)[0]):
                os.makedirs("Converted/" + filePath.split('.',1)[0]) 
            cv2.imwrite(f"Converted/{filePath.split('.',1)[0]}/Converted{i}.png", image)

            # Wenn benötigten Seiten gelesen worden sind beenden
            if(len(usedPages) == 0):
                break
  