from tkinter import Canvas, Tk, filedialog, Button, Frame, Text, Scrollbar, RIGHT, Y, LEFT, BOTH, TOP, BOTTOM, X
from PIL import Image, ImageTk, ImageDraw
import time
import mouse
from threading import Timer

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
    pass  # Falls nicht unter Windows, ignorieren
except Exception as e:
    print(f"Warnung: DPI Awareness konnte nicht gesetzt werden: {e}")


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


class BitmapEditor:
    def __init__(self, root):
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
        Button(self.side_frame, text="Canvas erstellen", command=self.create_canvas).pack(fill=X, pady=2)
        Button(self.side_frame, text="Nächste Canvas", command=self.next_canvas).pack(fill=X, pady=2)
        Button(self.side_frame, text="Vorherige Canvas", command=self.previous_canvas).pack(fill=X, pady=2)

        self.canvas_container = Frame(root)
        self.canvas_container.pack(side=LEFT, fill=BOTH, expand=True)

        # Initialisiere das erste Canvas
        self.create_canvas()

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
                print("Kein aktives Canvas vorhanden.")
        
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
            # Aktualisiere die Canvas-Darstellung
            tk_image = self.selected_image.get_source()
            current_canvas = self.get_current_canvas()
            if current_canvas:
                current_canvas.itemconfig(self.selected_image.get_canvas_id(), image=tk_image)

            # Speichere Referenz, um Garbage Collection zu vermeiden
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

if __name__ == "__main__":
    root = Tk()
    app = BitmapEditor(root)
    root.mainloop()