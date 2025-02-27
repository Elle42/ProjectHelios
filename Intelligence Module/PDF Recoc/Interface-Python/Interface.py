from tkinter import Canvas, Tk, filedialog, Button, Frame, Text, Scrollbar, RIGHT, Y, LEFT, BOTH, TOP, BOTTOM, X, Toplevel, messagebox
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageGrab
from threading import Timer
import os
from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract
import fdb
import logging
import configparser
import sys
from sys import argv
from logging.handlers import RotatingFileHandler

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
    pass  # Falls nicht unter Windows, ignorieren
except Exception as e:
    print(f"Warnung: DPI Awareness konnte nicht gesetzt werden: {e}")

# ---------------------------------------------------------------------------
# IB_Canvas_Data Class
class IB_Canvas_Data:
    def __init__(self):
        self._images = []
        self._logger = []
        self._canvas = None

    def remove_image(self, image):
        if image in self._images:
            self._images.remove(image)
            return True
        return False

    def find_image(self, canvas_id):
        for image in self._images:
            if image.get_canvas_id() == canvas_id:
                return image
        return None

    def get_all_images(self):
        return self._images

    def add_image(self, ib_image):
        if ib_image is None:
            raise ValueError("Das Bild oder das UI-Element darf nicht null sein.")
        self._images.append(ib_image)

    def register_image(self, path):
        try:
            bitmap = Image.open(path)
            img = IB_Image(path, bitmap)

            # Ensure maximum size
            max_width, max_height = 800, 600
            scale_factor = min(max_width / img.get_width(), max_height / img.get_height(), 1.0)
            img.set_scale(scale_factor)

            new_width = int(img.get_width() * scale_factor)
            new_height = int(img.get_height() * scale_factor)
            img.set_width(new_width)
            img.set_height(new_height)

            img.set_bitmap(bitmap.resize((new_width, new_height)))
            self._images.append(img)
        except Exception as e:
            self.log(str(e), "Error")
            raise

    def save_canvas(self, canvas):
        self._canvas = canvas

    def log(self, message, level):
        self._logger.append((level, message))
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Image Class
class IB_Image:
    _id_counter = 0

    def __init__(self, path_to_img, bitmap):
        self._id = IB_Image._id_counter
        IB_Image._id_counter += 1
        self._path_to_img = path_to_img
        self._bitMap = bitmap
        self._original_bitmap = bitmap.copy()
        self._width = bitmap.width
        self._height = bitmap.height
        self._scale = 1.0
        self._cutout_x = 0
        self._cutout_y = 0
        self._pos = (0, 0)
        self._canvas_id = None
        self._draw_layer = Image.new("RGBA", bitmap.size, (255, 255, 255, 0))  # Transparente Ebene
        self._draw = ImageDraw.Draw(self._draw_layer)
     

    def get_id(self):
        return self._id

    def get_canvas_id(self):
        return self._canvas_id

    def set_canvas_id(self, canvas_id):
        self._canvas_id = canvas_id

    def get_width(self):
        return self._width

    def set_width(self, width):
        self._width = width

    def get_height(self):
        return self._height

    def set_height(self, height):
        self._height = height

    def get_scale(self):
        return self._scale

    def set_scale(self, scale):
        self._scale = scale

    def get_cutout_x(self):
        return self._cutout_x

    def set_cutout_x(self, cutout_x):
        self._cutout_x = cutout_x

    def get_cutout_y(self):
        return self._cutout_y

    def set_cutout_y(self, cutout_y):
        self._cutout_y = cutout_y

    def get_pos(self):
        return self._pos

    def set_pos(self, pos):
        self._pos = pos

    def get_path_image(self):
        return self._path_to_img

    def get_bitmap(self):
        return self._bitMap

    def set_bitmap(self, bitmap):
        self._bitMap = bitmap

    def get_source(self):
        return ImageTk.PhotoImage(self._bitMap)

    def get_draw_layer(self):
        return self._draw_layer

    def get_draw(self):
        return self._draw

    def apply_draw_layer(self):
        """Kombiniert die Zeichnungsebene mit dem aktuellen Bitmap."""
        # Zeichnungsebene an die Größe der Bitmap anpassen
        if self._bitMap.size != self._draw_layer.size:
            self._draw_layer = self._draw_layer.resize(self._bitMap.size, Image.LANCZOS)

        # Kombiniere die aktuelle Bitmap mit der Zeichnungsebene
        combined = Image.alpha_composite(self._bitMap.convert("RGBA"), self._draw_layer)
        self._bitMap = combined.convert("RGB")  # Ergebnis speichern

        # Zeichnungsebene zurücksetzen
        self._draw_layer = Image.new("RGBA", (self._bitMap.width, self._bitMap.height), (255, 255, 255, 0))
        self._draw = ImageDraw.Draw(self._draw_layer)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Custom Canvas Class
class CustomCanvas(Canvas):
    """Eine Klasse, die von Canvas erbt und zusätzliche Informationen speichert."""
    def __init__(self, parent, canvas_id):
        super().__init__(parent, bg="white")
        self.canvas_id = canvas_id
        self.images = []  # Liste für Bilder oder andere Inhalte, die auf dem Canvas gespeichert werden
        self.pack_forget()  # Standardmäßig wird das Canvas nicht angezeigt

    def add_image(self, image):
        """Fügt ein Bild zur Canvas hinzu."""
        self.images.append(image)

    def get_images(self):
        """Gibt alle Bilder zurück, die auf diesem Canvas gespeichert sind."""
        return self.images
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Editor
class BitmapEditor:
    editorLogger = 0

    def __init__(self, root):
        global editorLogger

        # Logging Handling
                # Root Path
        rootPath = "Initialized :)"

        # Extract Root Dir
        if getattr(sys, 'frozen', False):  # Check if it is running under PyInstaller
            # Running as an executable
            rootPath = os.path.dirname(sys.executable)
        else:
            # Running under Python
            rootPath = os.path.dirname(os.path.abspath(__file__))

        global config

        # Configurations --------------------------
        config = configparser.ConfigParser()
        config.read(rootPath.rsplit('\\', 1)[0] + '\\conf.ini')
        # ------------------------------------------

        # Logger setup ----------------------------
        editorLogger = logging.getLogger('rotating_editorLogger')
        editorLogger.propagate = False
        # Global log level based on configuration
        match config['Interface']['logLevel']:
            case 'DEBUG':
                editorLogger.setLevel(logging.DEBUG)
            case 'INFO':
                editorLogger.setLevel(logging.INFO)

        # Rotating log handler with max file size of 5 MB
        handler = RotatingFileHandler(rootPath.rsplit('\\', 1)[0] + config['Interface']['logFile'], maxBytes=5*1024*1024, backupCount=3)

        # Log format -> Time -> Level -> Message
        formatter = logging.Formatter('%(asctime)s -  %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Console handler for logging to stdout
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        editorLogger.addHandler(console_handler)
        editorLogger.addHandler(handler)
        # ------------------------------------------

        self.root = root
        self.root.title("Bitmap Editor")
        self.scale_timer = None 
        self.drawing = False
        self.last_x, self.last_y = None, None

        self.canvas_data = IB_Canvas_Data()
        self.current_tool = None
        self.selected_image = None
        self.image_refs = []  # To keep references to all loaded images

        self.canvases = []  # Liste aller Canvases
        self.current_canvas_id = None  # ID des aktuell angezeigten Canvas
        self.next_canvas_id = 1  # ID für das nächste Canvas

        # Main layout
        self.side_frame = Frame(root, width=300, bg="lightgray")
        self.side_frame.pack(side=LEFT, fill=Y)

        self.info_box = Text(self.side_frame, wrap="word", height=20, width=30)
        self.info_box.pack(fill=Y, padx=5, pady=5)

        self.button_frame = Frame(self.side_frame, bg="lightgray")
        self.button_frame.pack(side=BOTTOM, fill=X, pady=5)

        Button(self.button_frame, text="Open Image", command=self.open_image).pack(fill=X, pady=2)
        Button(self.button_frame, text="Move", command=self.activate_move).pack(fill=X, pady=2)
        Button(self.button_frame, text="Scale", command=self.activate_scale).pack(fill=X, pady=2)
        Button(self.button_frame, text="Draw", command=self.activate_draw).pack(fill=X, pady=2)
        Button(self.button_frame, text="Erase", command=self.activate_erase).pack(fill=X, pady=2)
        Button(self.button_frame, text="Load Pdf", command=self.load_from_Pdf).pack(fill=X, pady=2)
        Button(self.side_frame, text="Canvas erstellen", command=self.create_canvas).pack(fill=X, pady=2)
        Button(self.side_frame, text="Nächste Canvas", command=self.next_canvas).pack(fill=X, pady=2)
        Button(self.side_frame, text="Vorherige Canvas", command=self.previous_canvas).pack(fill=X, pady=2)
        Button(self.side_frame, text="Canvas Speichern", command=self.save_current_canvas).pack(fill=X, pady=2)
        Button(self.button_frame, text="Crop Image", command=self.start_cropping).pack(fill=X, pady=2)

        self.canvas_container = Frame(root)
        self.canvas_container.pack(side=LEFT, fill=BOTH, expand=True)

        # Initialisiere das erste Canvas
        self.create_canvas()
        editorLogger.debug("Canvas erstellt!")

        # Event bindings
        self.get_current_canvas().bind("<ButtonPress-1>", self.on_canvas_click)
        self.get_current_canvas().bind("<B1-Motion>", self.on_canvas_drag)
        self.get_current_canvas().bind("<ButtonRelease-1>", self.on_canvas_release)
        self.get_current_canvas().bind("<MouseWheel>", self.on_canvas_scroll)

    def get_current_canvas(self):
        """Gibt das aktuell aktive Canvas zurück."""
        for canvas in self.canvases:
            if canvas.canvas_id == self.current_canvas_id:
                return canvas
        return None

    def load_from_Pdf(self):
        myLoader = PdfLoader()
        myLoader.load_from_Pdf()

    def create_canvas(self):
        """Erstellt ein neues Canvas mit einer eindeutigen ID."""
        canvas = CustomCanvas(self.canvas_container, canvas_id=self.next_canvas_id)
        self.canvases.append(canvas)

        # Binde die Ereignisse an das neue Canvas
        self.bind_canvas_events(canvas)

        if self.current_canvas_id is None:  # Falls noch kein Canvas aktiv ist
            self.current_canvas_id = canvas.canvas_id
            canvas.pack(fill=BOTH, expand=True)

        self.next_canvas_id += 1

    def show_canvas(self, canvas_id):
        """Zeigt ein Canvas an und versteckt alle anderen."""
        for canvas in self.canvases:
            if canvas.canvas_id == canvas_id:
                canvas.pack(fill=BOTH, expand=True)
            else:
                canvas.pack_forget()
        self.selected_image = None  # Auswahl zurücksetzen
        self.current_canvas_id = canvas_id

    def next_canvas(self):
        """Wechselt zum nächsten Canvas in der Liste."""
        if not self.canvases:
            return

        current_index = next((i for i, c in enumerate(self.canvases) if c.canvas_id == self.current_canvas_id), None)
        if current_index is not None:
            next_index = (current_index + 1) % len(self.canvases)
            self.current_canvas_id = self.canvases[next_index].canvas_id
            self.show_canvas(self.current_canvas_id)

    def previous_canvas(self):
        """Wechselt zum vorherigen Canvas in der Liste."""
        if not self.canvases:
            return

        current_index = next((i for i, c in enumerate(self.canvases) if c.canvas_id == self.current_canvas_id), None)
        if current_index is not None:
            prev_index = (current_index - 1) % len(self.canvases)
            self.current_canvas_id = self.canvases[prev_index].canvas_id
            self.show_canvas(self.current_canvas_id)

    def bind_canvas_events(self, canvas):
        """Bindet Ereignisse an ein Canvas."""
        canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        canvas.bind("<B1-Motion>", self.on_canvas_drag)
        canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        canvas.bind("<MouseWheel>", self.on_canvas_scroll)

    
    def save_current_canvas(self):
        """Aktiviert den Speichermodus: Benutzer kann einen Bereich auswählen, der gespeichert werden soll."""
        current_canvas = self.get_current_canvas()
        if not current_canvas:
            print("Kein Canvas vorhanden, das gespeichert werden kann.")
            return

        # Aktivieren des Speichermodus: Binde Auswahl-Ereignisse an das Canvas
        self.saving_mode = True
        self.save_rectangle = None
        current_canvas.bind("<ButtonPress-1>", self.on_save_start)
        current_canvas.bind("<B1-Motion>", self.on_save_drag)
        current_canvas.bind("<ButtonRelease-1>", self.on_save_end)
        editorLogger.debug("Speichermodus aktiviert. Ziehe ein Rechteck, um den zu speichernden Bereich auszuwählen.")

    def on_save_start(self, event):
        self.save_start_x, self.save_start_y = event.x, event.y
        current_canvas = self.get_current_canvas()
        if self.save_rectangle:
            current_canvas.delete(self.save_rectangle)
        self.save_rectangle = current_canvas.create_rectangle(self.save_start_x, self.save_start_y, event.x, event.y, outline="blue", width=2)

    def on_save_drag(self, event):
        current_canvas = self.get_current_canvas()
        current_canvas.coords(self.save_rectangle, self.save_start_x, self.save_start_y, event.x, event.y)

    def on_save_end(self, event):
        current_canvas = self.get_current_canvas()
        # Bestimme die Endkoordinaten
        x1, y1, x2, y2 = self.save_start_x, self.save_start_y, event.x, event.y
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # Berechne die absoluten Bildschirmkoordinaten des ausgewählten Bereichs
        canvas_rootx = current_canvas.winfo_rootx()
        canvas_rooty = current_canvas.winfo_rooty()
        abs_x1 = canvas_rootx + x1
        abs_y1 = canvas_rooty + y1
        abs_x2 = canvas_rootx + x2
        abs_y2 = canvas_rooty + y2

        # Öffne den Speicherdialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".bmp",
            filetypes=[("Bitmap Image", "*.bmp"), ("All Files", "*.*")]
        )
        if file_path:
            saved_image = ImageGrab.grab(bbox=(abs_x1, abs_y1, abs_x2, abs_y2))
            saved_image.save(file_path, "BMP")
            editorLogger.debug("Bereich gespeichert in: " + file_path)
        else:
            editorLogger.debug("Speichern abgebrochen.")

        # Entferne die Auswahl und stelle die ursprünglichen Bindings wieder her
        current_canvas.delete(self.save_rectangle)
        current_canvas.unbind("<ButtonPress-1>")
        current_canvas.unbind("<B1-Motion>")
        current_canvas.unbind("<ButtonRelease-1>")
        current_canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        current_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        current_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.saving_mode = False

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image and Bitmap Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            # Bild in der Canvas-Datenstruktur registrieren
            self.canvas_data.register_image(file_path)
            image = self.canvas_data.get_all_images()[-1]

            # Erstelle Canvas-Element
            tk_image = image.get_source()
            current_canvas = self.get_current_canvas()  # Aktuelles Canvas ermitteln
            if current_canvas is not None:
                img_id = current_canvas.create_image(400, 300, image=tk_image, anchor="center")
                image.apply_draw_layer()
                current_canvas.add_image(image)

                # Speichere Referenzen
                self.image_refs.append(tk_image)
                image.set_canvas_id(img_id)
                image.set_pos((400, 300))

                # Aktualisiere Info-Box
                self.update_info_box(image)
            else:
                editorLogger.debug("Kein Canvas zum speichern vorhanden!")

    def start_cropping(self):
        if not self.selected_image:
            messagebox.showerror("Fehler", "Kein Bild ausgewählt!")
            return
        
        current_canvas = self.get_current_canvas()
        self.crop_rectangle = None
        current_canvas.bind("<ButtonPress-1>", self.on_crop_start)
        current_canvas.bind("<B1-Motion>", self.on_crop_drag)
        current_canvas.bind("<ButtonRelease-1>", self.on_crop_end)

    def on_crop_start(self, event):
        self.start_x, self.start_y = event.x, event.y
        current_canvas = self.get_current_canvas()
        if self.crop_rectangle:
            current_canvas.delete(self.crop_rectangle)
        self.crop_rectangle = current_canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=2)

    def on_crop_drag(self, event):
        current_canvas = self.get_current_canvas()
        current_canvas.coords(self.crop_rectangle, self.start_x, self.start_y, event.x, event.y)

    def on_crop_end(self, event):
        # Erhalte die Canvas-Koordinaten des Crop-Rechtecks
        x1, y1, x2, y2 = self.start_x, self.start_y, event.x, event.y
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # Ermittle die Position und Größe des Bildes (das mittig auf dem Canvas gezeichnet wurde)
        img_pos = self.selected_image.get_pos()      # Mittlere Position (x, y)
        img_width = self.selected_image.get_width()
        img_height = self.selected_image.get_height()
        top_left_x = img_pos[0] - img_width // 2
        top_left_y = img_pos[1] - img_height // 2

        # Berechne die relativen Crop-Koordinaten (bezogen auf das Bild)
        rel_x1 = x1 - top_left_x
        rel_y1 = y1 - top_left_y
        rel_x2 = x2 - top_left_x
        rel_y2 = y2 - top_left_y

        # Begrenze die Koordinaten auf die Bildgrenzen
        rel_x1 = max(0, rel_x1)
        rel_y1 = max(0, rel_y1)
        rel_x2 = min(img_width, rel_x2)
        rel_y2 = min(img_height, rel_y2)

        # Führe das Cropping am aktuellen Bitmap durch
        cropped_bitmap = self.selected_image.get_bitmap().crop((rel_x1, rel_y1, rel_x2, rel_y2))
        self.selected_image.set_bitmap(cropped_bitmap)
        # Wichtiger Schritt: Aktualisiere auch das Original-Bitmap, damit spätere Skalierungen
        # auf dem beschnittenen Bild basieren.
        self.selected_image._original_bitmap = cropped_bitmap.copy()
        self.selected_image.set_width(cropped_bitmap.width)
        self.selected_image.set_height(cropped_bitmap.height)

        self.update_canvas_image()
        current_canvas = self.get_current_canvas()
        current_canvas.delete(self.crop_rectangle)
        current_canvas.unbind("<ButtonPress-1>")
        current_canvas.unbind("<B1-Motion>")
        current_canvas.unbind("<ButtonRelease-1>")
        current_canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        current_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        current_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
    def activate_move(self):
        self.current_tool = "move"

    def activate_scale(self):
        self.current_tool = "scale"

    def activate_draw(self):
        self.current_tool = "draw"

    def activate_erase(self):
        self.current_tool = "erase"

    def on_canvas_click(self, event):
        current_canvas = self.get_current_canvas()
        if not current_canvas:
            return

        # Finde das Bild, das unter dem Mauszeiger liegt
        clicked_image = None
        for image in reversed(self.canvas_data.get_all_images()):  # Prüfe die Bilder in umgekehrter Reihenfolge
            img_x, img_y = image.get_pos()
            img_width, img_height = image.get_width(), image.get_height()

            # Überprüfen, ob der Klick innerhalb der Bildgrenzen liegt
            if img_x - img_width // 2 <= event.x <= img_x + img_width // 2 and \
            img_y - img_height // 2 <= event.y <= img_y + img_height // 2:
                clicked_image = image
                break

        if clicked_image:
            self.selected_image = clicked_image
            self.update_info_box(self.selected_image)

        # Für Zeichen- und Löschwerkzeuge: Initiale Position speichern
        if self.current_tool in ["draw", "erase"] and self.selected_image:
            self.drawing = True
            self.last_x, self.last_y = event.x, event.y


    def on_canvas_drag(self, event):
        if self.current_tool == "move" and self.selected_image:
            dx = event.x - self.selected_image.get_pos()[0]
            dy = event.y - self.selected_image.get_pos()[1]

            # Bewege das Bild auf der Canvas
            current_canvas = self.get_current_canvas()
            if current_canvas:
                current_canvas.move(self.selected_image.get_canvas_id(), dx, dy)
     
            # Aktualisiere die Position des Bildes
            self.selected_image.set_pos((event.x, event.y))

            # Wende Zeichnungsebene an und aktualisiere Canvas
            
            self.update_canvas_image()

            # Aktualisiere Info-Box
            self.update_info_box(self.selected_image)

        if self.drawing and self.selected_image:
            # Zeichnungsebene holen
            draw_layer = self.selected_image.get_draw()

            # Berechne relative Position im Bild
            img_x = int((event.x - self.selected_image.get_pos()[0]) + self.selected_image.get_width() / 2)
            img_y = int(event.y - self.selected_image.get_pos()[1] + self.selected_image.get_height() / 2)
            last_img_x = int(self.last_x - self.selected_image.get_pos()[0] + self.selected_image.get_width() / 2)
            last_img_y = int(self.last_y - self.selected_image.get_pos()[1] + self.selected_image.get_height() / 2)

            # Zeichnen oder Löschen auf der Ebene
            if self.current_tool == "draw":
                draw_layer.line((last_img_x, last_img_y, img_x, img_y), fill="black", width=3)
            elif self.current_tool == "erase":
                draw_layer.line((last_img_x, last_img_y, img_x, img_y), fill="white", width=10)

            # Aktualisiere Canvas-Darstellung
            
            self.update_canvas_image()

            # Speichern der neuen Mausposition
            self.last_x, self.last_y = event.x, event.y
        self.selected_image.apply_draw_layer()


    def on_canvas_release(self, event):
        if self.current_tool in ["draw", "erase"]:
            self.drawing = False
            self.last_x, self.last_y = None, None
        elif self.current_tool == "move" and self.selected_image:
            self.update_info_box(self.selected_image)

    def on_canvas_scroll(self, event):
        if self.current_tool == "scale" and self.selected_image:
            current_canvas = self.get_current_canvas()
            if current_canvas:
                scale_factor = 1.1 if event.delta > 0 else 0.9

                # Starte den Timer neu
                if self.scale_timer:
                    self.scale_timer.cancel()
                self.scale_timer = Timer(0.1, self.perform_scaling, args=[scale_factor])
                self.scale_timer.start()

    def perform_scaling(self, scale_factor):
        if self.selected_image:
            # Wende die aktuelle Zeichnungsebene an, bevor das Bild skaliert wird
            

            # Holen des Original-Bitmaps und der aktuellen Skalierung
            original_bitmap = self.selected_image._original_bitmap
            current_scale = self.selected_image.get_scale()

            new_width = int(original_bitmap.width * current_scale * scale_factor)
            new_height = int(original_bitmap.height * current_scale * scale_factor)

            if new_width > 20 and new_height > 20:
                # Skalieren des Original-Bitmaps
                scaled_bitmap = original_bitmap.resize((new_width, new_height), Image.LANCZOS)

                # Aktualisieren der Bitmap und Metadaten
                self.selected_image.set_bitmap(scaled_bitmap.convert("RGB"))  # RGB-Format speichern
                self.selected_image.set_width(new_width)
                self.selected_image.set_height(new_height)
                self.selected_image.set_scale(current_scale * scale_factor)

                # Canvas aktualisieren
                tk_image = self.selected_image.get_source()
                current_canvas = self.get_current_canvas()
                if current_canvas:
                    current_canvas.itemconfig(self.selected_image.get_canvas_id(), image=tk_image)

                self.image_refs.append(tk_image)
                self.update_info_box(self.selected_image)
        self.selected_image.apply_draw_layer()



    def update_canvas_image(self):
        if self.selected_image:
            tk_image = ImageTk.PhotoImage(self.selected_image.get_bitmap())
            current_canvas = self.get_current_canvas()
            current_canvas.itemconfig(self.selected_image.get_canvas_id(), image=tk_image)
            self.image_refs.append(tk_image)


    def update_info_box(self, image):
        self.info_box.delete(1.0, "end")
        info = (
            f"ID: {image.get_id()}\n"
            f"Position: {image.get_pos()}\n"
            f"Width: {image.get_width()}\n"
            f"Height: {image.get_height()}\n"
            f"Scale: {image.get_scale()}\n"
            f"Path: {image.get_path_image()}\n"
        )
        self.info_box.insert("end", info)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------
# Pdf Loader
class PdfLoader:

    config = 0
    logger = 0
    rootPath = 0
    cur = 0
    con = 0
    outputPath = 0
    tmpPath = 0

    def __init__(self):
        global config
        global logger
        global rootPath
        global cur
        global con
        global outputPath
        global tmpPath

        # Root Path
        rootPath = "Initialized :)"

        # Extract Root Dir
        if getattr(sys, 'frozen', False):  # Check if it is running under PyInstaller
            # Running as an executable
            rootPath = os.path.dirname(sys.executable)
        else:
            # Running under Python
            rootPath = os.path.dirname(os.path.abspath(__file__))

        global config

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


        # Paths and Directories -------------------------------------------------
        logger.debug("Root Path: " + rootPath)
        outputPath = rootPath + "\\" + config['ReadPdf']['outputPath'] + "\\"

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
                            name VARCHAR(40), 
                            currentPage INTEGER
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


        # Pytesseract ----------------------------------------------------------
        if rootPath.rsplit('\\', 1)[0] + config['tesseract']['pathToTesseract'] not in os.environ["PATH"]:
            os.environ["PATH"] = rootPath.rsplit('\\', 1)[0] + config['tesseract']['pathToTesseract'] + os.pathsep + os.environ["PATH"]

        pytesseract.pytesseract.tesseract_cmd = rootPath.rsplit('\\', 1)[0] + config['tesseract']['pathToTesseract']

        # Pdf Loader -----------------------------------------------------------
        self.pages = []
        self.pageIndices = []
        self.pdf_pages = []
        self.current_page_index = 0
        pass

    # ---------------------------------------------------------------------------------------------------------------------
    # Recognize all texts in the image and store them in the database, texts are covered with white rectangles
    def TextRecocnition(self, image, binary, cur, rotation, id):
        global logger

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
    def ConversionLoop(self, pages, rotation, name, planId):
        global logger
        global config
        global cur
        global con
        global outputPath

        pageId = 0

        # Prepare the Database for a new Pdf
        fire_plan_name = name

        con.commit()

        # Falls keine PlanId vorhanden ist benutze eine neue
        if planId == 0:
            # Insert new Fire Plan into the database
            cur.execute("INSERT INTO FIRE_PLANS (name) VALUES (?) RETURNING planId", (fire_plan_name,))

            # Fetch the generated planId
            planId = cur.fetchone()[0]

            # Log the inserted planId
            logger.info(f"Inserted new Fire Plan with generated planId: {planId}")
            con.commit()

        # Main conversion loop
        for i, page in enumerate(pages):
            cur.execute("INSERT INTO PAGES (planId) VALUES (?) RETURNING pageId", (planId,))
            pageId = cur.fetchone()[0]

            # Save the page as a temporary image
            image_path = rootPath + "\\" + tmpPath + f"temp_page_{planId}_{pageId}.png"
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
            image = self.TextRecocnition(image, binary, cur, "nr", pageId)

            # Apply Gaussian blur and thresholding
            blurred = cv2.GaussianBlur(image, (3,3), 0)
            _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

            # Save the processed images
            if not os.path.exists(f"{outputPath}{name}"):
                os.makedirs(f"{outputPath}{name}")
                logger.debug(f"Created Directory: " + outputPath + name)
            cv2.imwrite(f"{outputPath}{name}\Converted{planId}_{pageId}.png", thresh)
            # cv2.imwrite(f"{outputPath}{name}\Blurred{planId}_{pageId}.png", blurred)
            logger.info(f"Image saved at: " + outputPath + name + "\Converted{planId}_{pageId}.png")

    def load_from_Pdf(self):
        # Create the top-level window
        toplevel = Toplevel()
        toplevel.title('Load PDF')
        toplevel.geometry('800x700')

        name = 0

        # Screen in wich the user Selects th PDF File
        def select_pdf():
            file_path = filedialog.askopenfilename(
                title="Select PDF File",
                filetypes=[("PDF Files", "*.pdf")]
            )
            if file_path:
                display_pdf(file_path)
                toplevel.focus_set()

        # Function to get the Pdf Pages
        def display_pdf(file_path):
            global name

            try:
                # Add Poppler to the system PATH only if it's not already there
                if rootPath.rsplit('\\', 1)[0] + config['Poppler']['pathToPoppler'] not in os.environ["PATH"]:
                    os.environ["PATH"] = rootPath.rsplit('\\', 1)[0] + config['Poppler']['pathToPoppler'] + os.pathsep + os.environ["PATH"]

                # Converte the pages using poppler
                self.pdf_pages = convert_from_path(file_path, poppler_path=rootPath.rsplit('\\', 1)[0] + config['Poppler']['pathToPoppler'])

                # name of the Pdf
                name = os.path.splitext(os.path.basename(file_path))[0]

                self.current_page_index = 0
                display_image(self.current_page_index)

            except Exception as e:
                # Konvertierung Fehlgeschlagen
                editorLogger.error(f"Konvertierung der Pdfs fehlgeschlagen: {e}")

        # Function to display the images of the current pdf page in the window
        def display_image(page_index):
            if 0 <= page_index < len(self.pdf_pages):
                page_image = self.pdf_pages[page_index]
                img = page_image.resize((400, 600))
                img_tk = ImageTk.PhotoImage(img)
                canvas.itemconfig(image_on_canvas, image=img_tk)
                canvas.image = img_tk
                current_page_label.config(text=f"Page {page_index + 1} / {len(self.pdf_pages)}")

        # Function loading the Next Page
        def next_page():
            if self.current_page_index < len(self.pdf_pages) - 1:
                self.current_page_index += 1
                display_image(self.current_page_index)
            
            # Logic to disable the save button if the current page has been saved already
            if(self.current_page_index in self.pageIndices):
                save_button.config(state=tk.DISABLED)
            else:
                save_button.config(state=tk.NORMAL)

        # Function loading the previous page
        def prev_page():
            if self.current_page_index > 0:
                self.current_page_index -= 1
                display_image(self.current_page_index)

            # Logic to disable the save button if the current page has been saved already
            if(self.current_page_index in self.pageIndices):
                save_button.config(state=tk.DISABLED)
            else:
                save_button.config(state=tk.NORMAL)

        # Saving the current page
        def save_page():
            if 0 <= self.current_page_index < len(self.pdf_pages):
                self.pages.append(self.pdf_pages[self.current_page_index])
                self.pageIndices.append(self.current_page_index)

                # Disablieng the Save button because it has just beed saved
                save_button.config(state=tk.DISABLED)

        # Starting the conversio process
        def start_conversion(planId):
            global name
            messagebox.showinfo("Tst", f"Current length of page array {len(self.pages)}!")
            self.ConversionLoop(self.pages, "nr", name, planId)
            toplevel.destroy()

        def get_existing_plans():
            global cur
            global con
            cur.execute("SELECT planId, name FROM FIRE_PLANS")
            plans = {row[1]: row[0] for row in cur.fetchall()}
            return plans

        def add_new_plan(newPlanName, listbox):
            global cur
            cur.execute("SELECT COUNT(*) FROM FIRE_PLANS WHERE name = ?", (newPlanName,))
            if cur.fetchone()[0] > 0:
                logger.error("Ein Plan mit diesem Namen existiert bereits, Aktion Abgebrochen!")
                messagebox.showwarning("Warning", "A plan with this name already exists.")
                return

            # Insert new plan
            cur.execute("INSERT INTO FIRE_PLANS (name, currentPage) VALUES (?, ?)", (newPlanName,0))
            con.commit()

            # Update listbox
            listbox.insert(tk.END, newPlanName)
            messagebox.showinfo("Success", f"Plan '{newPlanName}' created.")

        def on_plan_selected(event, plans_dict):
            global name
            selected_index = event.widget.curselection()
            if selected_index:
                selected_name = event.widget.get(selected_index[0])  
                name = selected_name
                plan_id = plans_dict[selected_name]  
                start_conversion(plan_id)  

        def PlanAuswahl():
            topLevel = tk.Toplevel()
            topLevel.title("Plan Selection")
            topLevel.geometry("400x300")

            # Fetch existing plans
            plans = get_existing_plans()

            # Listbox to display plans
            listbox = tk.Listbox(topLevel, height=10)
            listbox.pack(pady=10, fill=tk.BOTH, expand=True)

            for plan in plans:
                listbox.insert(tk.END, plan, )

            # Binding a event to detect user inputs
            listbox.bind("<<ListboxSelect>>", lambda event: on_plan_selected(event, plans))

            # Entry and button for new plan
            entry = tk.Entry(topLevel)
            entry.pack(pady=5)

            add_button = tk.Button(topLevel, text="Create New Plan", command=lambda: add_new_plan(entry.get(), listbox))
            add_button.pack()

            root.mainloop()

        # GUI components
        select_btn = tk.Button(toplevel, text="Select PDF", command=select_pdf)
        select_btn.pack()

        canvas = tk.Canvas(toplevel, width=400, height=600)
        canvas.pack()
        image_on_canvas = canvas.create_image(0, 0, anchor='nw')

        navigation_frame = tk.Frame(toplevel)
        navigation_frame.pack()

        prev_button = tk.Button(navigation_frame, text="<< Previous", command=prev_page)
        prev_button.grid(row=0, column=0)

        current_page_label = tk.Label(navigation_frame, text="Page")
        current_page_label.grid(row=0, column=1)

        next_button = tk.Button(navigation_frame, text="Next >>", command=next_page)
        next_button.grid(row=0, column=2)

        save_button = tk.Button(navigation_frame, text="Save Page", command=save_page)
        save_button.grid(row=0, column=3)

        startConversion_button = tk.Button(navigation_frame, text="Start Conversion", command=PlanAuswahl)
        startConversion_button.grid(row=0, column=4)

        toplevel.focus_set()

        



# ---------------------------------------------------------------------------
# ##### Main #####
if __name__ == "__main__":
    root = Tk()
    app = BitmapEditor(root)
    root.mainloop()
# ---------------------------------------------------------------------------