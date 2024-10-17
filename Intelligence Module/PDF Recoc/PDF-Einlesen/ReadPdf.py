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


# Configs --------------------------
config = configparser.ConfigParser()
config.read('conf.ini')
# ----------------------------------


# Logger ------------------------------------
logger = logging.getLogger('rotating_logger')
logger.propagate = False
# Globales Log Level
match config['general']['logLevel']:
    case 'DEBUG':
        logger.setLevel(logging.DEBUG)
    case 'INFO':
        logger.setLevel(logging.INFO)
# Max File Size 5 mb dann rotaten
handler = RotatingFileHandler(config['general']['logFile'], maxBytes=5*1024*1024, backupCount=3)
# Formatirung des Logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
if fileMode == 'single':      #
    filePath = argv[2]      # Name von zu Konvertierenden File, muss sowiso im $dirPath$ Vorhanden sein
    rotation = argv[3]      # rr Gegen- und rl mit dem Uhrzeigersinn
    usedPages = argv[4:]    # Angabe welche Seiten der PDF Verarbeitet werden sollen, Angabe muss bereits in der Richtigen Reihenfolge sein
# -------------------


# Pfade und Ordnerstrucktur --------------------------------------------
rootPath = argv[0].rsplit('\\', 1)[0]
outputPath = config['general']['outputPath'] + "/"
# Initalize Folder
if not os.path.exists(outputPath + filePath.split('.',1)[0]):
    os.makedirs(outputPath + filePath.split('.',1)[0]) 
    logger.info('Directory ' + filePath.split('.',1)[0] + ' Created!')
# Pfade Laden
tmpPath = config['general']['tmpPath']
dirPath = rootPath + f"\PlanPdf\\"
# ----------------------------------------------------------------------



# Datenbank Initialisierung --------------------------------------------
# Pfade Laden
db_path = rootPath + "\\" + outputPath + "\\" + filePath.split('.',1)[0] + "\TEXTSDB.fdb"
api = config['db']['pathToDLL']
fdb.load_api(api)
#Users
db_User = "HeliosUser"
db_Password = "class"
# Wenn benoetigt soll die Datenbank erstellt werden
if not os.path.exists(db_path):
    # Datenbank existiert nicht
    try:
        con = fdb.create_database(f"CREATE DATABASE '{db_path}' user '{db_User}' password '{db_Password}'")
        con.close()
    except:
        logger.exception("DatenBank Kann Nicht erstellt werden")
    logger.info(f"Datenbank erstellt: {db_path}")
else:
    # Datenbank existiert bereits
    logger.info(f"Datenbank existiert bereits: {db_path}")
# Db Connection
con = fdb.connect(dsn=db_path, user=db_User, password=db_Password, fb_library_name=api)
cur = con.cursor()
logger.info("DB Verbindung wurde aufgebaut!")
pytesseract.pytesseract.tesseract_cmd = config['tesseract']['pathToTesseract']
# ----------------------------------------------------------------------



# ---------------------------------------------------------------------------------------------------------------------
# Texte im Bild erkennen, in einer datenbank mit den koordinaten abspeichern und Mit Rechtecken überdecken
def TextRecocnition(image, binary, cur, rotation, i):
    if rotation == "nr":
        # Mit KI Texte erkennen
        data = pytesseract.image_to_data(binary, output_type=pytesseract.Output.DICT)
        logger.debug("Es wurden " + str(len(data)) + "einzelne Woerter gefunden")

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



# Verschiedene File Modes Unterscheiden -------------------------------------------------------------------------------
if fileMode == 'single':
    logger.info("Pdf wird im FileMode Single aufgerufen")
    logger.info("Es werden insgesamt" + str(len(usedPages)) + " Seiten bearbeitet!")
    logger.debug(str(dirPath) + str(filePath))

    # Pdf Lesen
    pages = convert_from_path(
        str(dirPath) + str(filePath),
        300,
        poppler_path = config['Poppler']['pathToPoppler']
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
                logger.debug("Table CONVERTED_{i} exestiert bereits -> Table Wird gedropped")
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
            logger.debug("Neuer Table CONVERTED_{i} wurde erstellt!")
            con.commit()

            # Abfrage wie Rotation behandelt werden soll
            if(rotation == 'rr'):
                logger.debug("Rotation -> rr")
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            if(rotation == 'rl'):
                logger.debug("Rotation -> rl")
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)


            # Den Gesamten Text in der Derzeitigen Seite Lesen
            # In die DatenBank schreiben
            image = TextRecocnition(image,binary, cur, "nr", i)

            # Speichern der Convertierten IMGs
            logger.info(f"Gespeichert Unter: {outputPath}{filePath.split('.',1)[0]}/Converted{i}.png")
            if not os.path.exists(outputPath + filePath.split('.',1)[0]):
                logger.debug("Neues Verzeichnis \'" + outputPath + filePath.split('.',1)[0] + "\' erstellt")
                os.makedirs(outputPath + filePath.split('.',1)[0]) 
            cv2.imwrite(f"{outputPath}{filePath.split('.',1)[0]}/Converted{i}.png", image)

            # Wenn benötigten Seiten gelesen worden sind beenden
            if(len(usedPages) == 0):
                break
  