using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.IO;
using System.Drawing;
using Point = System.Windows.Point;
using Image = System.Windows.Controls.Image;
using Brushes = System.Windows.Media.Brushes;
using static System.Net.Mime.MediaTypeNames;

namespace Interface
{
    public partial class MainWindow : Window
    {
        private List<ImageData> imageDataList = new List<ImageData>();
        private ImageData currentlySelectedImageData;
        private Point mouseClickPosition;
        private string currentMode = "None";
        private const double MinImageSize = 50; // Minimale Bildgröße
        private const int MaxImageWidth = 800; // Maximale Breite in Pixel
        private const int MaxImageHeight = 600; // Maximale Höhe in Pixel

        private int imageCounter = 0; // Zähler für Bild-IDs
        private Dictionary<int, ImageData> imageDataDictionary = new Dictionary<int, ImageData>();
        private List<Image> uploadedImages = new List<Image>();
        private List<Border> imageBorders = new List<Border>();
        private List<Bitmap> uploadedBitmaps = new List<Bitmap>(); // Liste der Bitmaps
        private Image currentlySelectedImage;
        private Border currentlySelectedBorder;
        private Bitmap selectedBitmap;
        private Point imageOriginalPosition;





        public MainWindow()
        {
            InitializeComponent();
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            this.WindowStyle = WindowStyle.None;
            this.Topmost = true;
            this.WindowState = WindowState.Maximized;
        }

        private void ImageSelectionComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var selectedMode = (imageSelectionComboBox.SelectedItem as ComboBoxItem).Content.ToString();
            confirmButton.Visibility = selectedMode == "Multi" ? Visibility.Visible : Visibility.Collapsed;
            uploadButton.Visibility = selectedMode == "Single" && imageDataList.Count > 0 ? Visibility.Collapsed : Visibility.Visible;
        }

        private void uploadButton_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Multiselect = true
            };

            if (openFileDialog.ShowDialog() == true)
            {
                foreach (var fileName in openFileDialog.FileNames)
                {
                    LoadImage(fileName);
                }

                if ((imageSelectionComboBox.SelectedItem as ComboBoxItem).Content.ToString() == "Single" && imageDataList.Count > 0)
                {
                    ConfirmUploadForSingle();
                }
            }
        }

        private void LoadImage(string filePath)
        {
            try
            {
                BitmapImage bitmapImage = new BitmapImage(new Uri(filePath));
                Console.WriteLine($"Loaded image: {filePath} with size: {bitmapImage.PixelWidth}x{bitmapImage.PixelHeight}");

                // Berechnung des Skalierungsfaktors
                double scaleFactor = 1.0;

                if (bitmapImage.PixelWidth > MaxImageWidth || bitmapImage.PixelHeight > MaxImageHeight)
                {
                    scaleFactor = Math.Min(MaxImageWidth / (double)bitmapImage.PixelWidth, MaxImageHeight / (double)bitmapImage.PixelHeight);
                }

                // Erstelle das Image-Element
                Image newImage = new Image
                {
                    Source = bitmapImage,
                    Width = bitmapImage.PixelWidth * scaleFactor,
                    Height = bitmapImage.PixelHeight * scaleFactor
                };

                // Erstelle den Border
                Border newBorder = new Border
                {
                    Width = newImage.Width,
                    Height = newImage.Height,
                    Child = newImage,
                    BorderBrush = Brushes.Transparent,
                    BorderThickness = new Thickness(1)
                };

                // Zentriere das Bild auf dem Canvas
                double centerX = (imageCanvas.ActualWidth - newBorder.Width) / 2;
                double centerY = (imageCanvas.ActualHeight - newBorder.Height) / 2;

                Canvas.SetLeft(newBorder, centerX);
                Canvas.SetTop(newBorder, centerY);
                imageCanvas.Children.Add(newBorder); // Füge den Border zum Canvas hinzu

                Console.WriteLine("Image added to canvas.");

                // Erstelle und speichere die ImageData
                ImageData imageData = new ImageData
                {
                    Id = imageCounter++,
                    FilePath = filePath,
                    OriginalWidth = bitmapImage.PixelWidth,
                    OriginalHeight = bitmapImage.PixelHeight,
                    OriginalX = centerX,
                    OriginalY = centerY,
                    CurrentWidth = newImage.Width,
                    CurrentHeight = newImage.Height,
                    CurrentX = centerX,
                    CurrentY = centerY,
                    ImageBorder = newBorder // Setze die Border
                };

                imageDataList.Add(imageData); // Füge die Bilddaten zur Liste hinzu
                imageDataDictionary[imageData.Id] = imageData; // Füge zur Dictionary hinzu
                newImage.Tag = imageData.Id; // Setze die ID als Tag des Bildes

                // Event-Handler für Interaktivität an Border anhängen
                newBorder.MouseLeftButtonDown += Image_LeftButtonDown;
                newBorder.MouseMove += ImageCanvas_MouseMove;
                newBorder.MouseLeftButtonUp += Image_MouseLeftButtonUp;
                newBorder.MouseWheel += Image_MouseWheel;

                newImage.MouseWheel += Image_MouseWheel; // Event-Handler hinzufügen

            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error uploading image: {ex.Message}");
            }
        }

        private void ConfirmUploadForSingle()
        {
            uploadButton.Visibility = Visibility.Collapsed;
            ShowModeButtons();
        }

        private void ConfirmButton_Click(object sender, RoutedEventArgs e)
        {
            if ((imageSelectionComboBox.SelectedItem as ComboBoxItem).Content.ToString() == "Multi")
            {
                uploadButton.Visibility = Visibility.Collapsed;
                ShowModeButtons();
            }
        }

        private void Image_LeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (sender == null || e == null)
            {
                Console.WriteLine("Sender oder Event ist null.");
                return;
            }

            // Überprüfen, ob der Sender ein Border ist
            var border = sender as Border;
            if (border == null)
            {
                Console.WriteLine("Das angeklickte Element ist kein Border.");
                return;
            }

            // Das Kind des Borders ist das Image
            var image = border.Child as Image;
            if (image == null)
            {
                Console.WriteLine("Das Border hat kein Image als Kind.");
                return;
            }

            // Setze das aktuell ausgewählte Bild und Border
            currentlySelectedImage = image;
            currentlySelectedBorder = border;

            int imageId = (int)image.Tag;
            ShowImageInfo(imageId);
            currentlySelectedImageData = imageDataList.Find(data => data.Id == imageId);

            if (currentlySelectedImageData == null) return;

            foreach (var data in imageDataList)
            {
                if (data.ImageBorder != null)
                    data.ImageBorder.BorderBrush = Brushes.Transparent;
            }

            currentlySelectedImageData.ImageBorder.BorderBrush = Brushes.Blue;
            mouseClickPosition = e.GetPosition(imageCanvas);
        }



        private void Image_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            Mouse.Capture(null);
            
        }

        private void ImageCanvas_MouseMove(object sender, MouseEventArgs e)
        {
            if (currentlySelectedImage != null && e.LeftButton == MouseButtonState.Pressed)
            {
                try
                {
                    Point currentMousePosition = e.GetPosition(imageCanvas);

                    if (currentMode == "Move")
                    {
                        MoveImage(currentlySelectedImage, e);
                    }
                    else if (currentMode == "Draw")
                    {
                        DrawOnImage(e);
                    }
                    else if (currentMode == "Erase")
                    {
                        EraseFromImage(e);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in MouseMove: {ex.Message}");
                }
            }
        }

        private void MoveImage(object sender, MouseEventArgs e)
        {
            if (currentlySelectedImage != null && e.LeftButton == MouseButtonState.Pressed)
            {
                Point currentMousePosition = e.GetPosition(imageCanvas);
                double offsetX = currentMousePosition.X - mouseClickPosition.X;
                double offsetY = currentMousePosition.Y - mouseClickPosition.Y;

                // Setze die Position des Borders
                Canvas.SetLeft(currentlySelectedBorder, Canvas.GetLeft(currentlySelectedBorder) + offsetX);
                Canvas.SetTop(currentlySelectedBorder, Canvas.GetTop(currentlySelectedBorder) + offsetY);

                // Setze die Position des Bildes entsprechend
                Canvas.SetLeft(currentlySelectedImage, Canvas.GetLeft(currentlySelectedBorder));
                Canvas.SetTop(currentlySelectedImage, Canvas.GetTop(currentlySelectedBorder));

                mouseClickPosition = currentMousePosition;

                
            }
        }



        // Zeichenfunktion
        private void DrawOnImage(MouseEventArgs e)
        {
            if (currentlySelectedImage != null && selectedBitmap != null)
            {
                Point position = e.GetPosition(imageCanvas);
                int x = (int)position.X;
                int y = (int)position.Y;

                try
                {
                    using (Graphics g = Graphics.FromImage(selectedBitmap))
                    {
                        g.FillRectangle(new SolidBrush(System.Drawing.Color.Black), x, y, 1, 1);
                    }

                    UpdateImage();
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in DrawOnImage: {ex.Message}");
                }
            }
        }

        // Löschfunktion
        private void EraseFromImage(MouseEventArgs e)
        {
            if (currentlySelectedImage != null && selectedBitmap != null)
            {
                Point position = e.GetPosition(imageCanvas);
                int x = (int)position.X;
                int y = (int)position.Y;

                try
                {
                    using (Graphics g = Graphics.FromImage(selectedBitmap))
                    {
                        g.FillRectangle(new SolidBrush(System.Drawing.Color.Transparent), x, y, 1, 1);
                    }

                    UpdateImage();
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in EraseFromImage: {ex.Message}");
                }
            }
        }

        // Bild aktualisieren
        private void UpdateImage()
        {
            if (currentlySelectedImage != null && selectedBitmap != null)
            {
                try
                {
                    BitmapSource bitmapSource = System.Windows.Interop.Imaging.CreateBitmapSourceFromHBitmap(
                        selectedBitmap.GetHbitmap(),
                        IntPtr.Zero,
                        Int32Rect.Empty,
                        BitmapSizeOptions.FromEmptyOptions());

                    currentlySelectedImage.Source = bitmapSource;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in UpdateImage: {ex.Message}");
                }
            }
        }


        private void Image_MouseWheel(object sender, MouseWheelEventArgs e)
        {
            if (currentlySelectedImage != null && currentMode == "Scale")
            {
                double scaleFactor = e.Delta > 0 ? 1.05 : 0.95;

                // Bestimme die aktuelle Position des Bildes im Canvas
                double currentLeft = Canvas.GetLeft(currentlySelectedBorder);
                double currentTop = Canvas.GetTop(currentlySelectedBorder);

                // Berechne das Zentrum des Bildes vor der Skalierung
                double centerX = currentLeft + currentlySelectedBorder.Width / 2;
                double centerY = currentTop + currentlySelectedBorder.Height / 2;

                // Hole den aktuellen Transform (ScaleTransform) oder erstelle einen neuen
                var transform = currentlySelectedImage.RenderTransform as ScaleTransform;
                if (transform == null)
                {
                    transform = new ScaleTransform(1, 1);
                    currentlySelectedImage.RenderTransform = transform;
                }

                // Wende die Skalierung an
                transform.ScaleX *= scaleFactor;
                transform.ScaleY *= scaleFactor;

                // Berechne die neuen Dimensionen der Border nach der Skalierung
                double newWidth = currentlySelectedImage.ActualWidth * transform.ScaleX;
                double newHeight = currentlySelectedImage.ActualHeight * transform.ScaleY;

                // Setze die neue Größe der Border
                currentlySelectedBorder.Width = newWidth;
                currentlySelectedBorder.Height = newHeight;

                // Berechne die neue Position der Border, um das Zentrum beizubehalten
                double newLeft = centerX - (newWidth / 2);
                double newTop = centerY - (newHeight / 2);

                // Setze die neue Position der Border im Canvas
                Canvas.SetLeft(currentlySelectedBorder, newLeft);
                Canvas.SetTop(currentlySelectedBorder, newTop);

                currentlySelectedImageData.CurrentWidth = newWidth;
                currentlySelectedImageData.CurrentHeight = newHeight;

            }
        }

        private void UpdateBorderSize()
        {
            if (currentlySelectedImage != null && currentlySelectedBorder != null)
            {
                // Hole die aktuellen Abmessungen des Bildes
                var transform = currentlySelectedImage.RenderTransform as ScaleTransform;
                double scaleX = transform?.ScaleX ?? 1;
                double scaleY = transform?.ScaleY ?? 1;

                // Berechne die neuen Breiten und Höhen unter Berücksichtigung des Zooms
                double scaledWidth = currentlySelectedImage.ActualWidth * scaleX;
                double scaledHeight = currentlySelectedImage.ActualHeight * scaleY;

                // Setze die Größe der Border direkt an die Größe des Bildes an
                currentlySelectedBorder.Width = Math.Max(scaledWidth, MinImageSize);
                currentlySelectedBorder.Height = Math.Max(scaledHeight, MinImageSize);

                // Setze die Position der Border, um mit dem Bild übereinzustimmen
                Canvas.SetLeft(currentlySelectedBorder, Canvas.GetLeft(currentlySelectedImage));
                Canvas.SetTop(currentlySelectedBorder, Canvas.GetTop(currentlySelectedImage));
            }
        }



        private void DrawButton_Click(object sender, RoutedEventArgs e)
        {
            currentMode = "Draw";
            ResetMouseCapture(); // Freigabe der Maus
            Console.WriteLine("Mode switched to Draw");
        }

        private void EraseButton_Click(object sender, RoutedEventArgs e)
        {
            currentMode = "Erase";
            ResetMouseCapture(); // Freigabe der Maus
            Console.WriteLine("Mode switched to Erase");
        }

        private void ScaleButton_Click(object sender, RoutedEventArgs e)
        {
            currentMode = "Scale";
            ResetMouseCapture(); // Freigabe der Maus
            Console.WriteLine("Mode switched to Scale");
        }

        private void ImageMove_Click(object sender, RoutedEventArgs e)
        {
            currentMode = "Move";
            ResetMouseCapture(); // Freigabe der Maus
            Console.WriteLine("Mode switched to Move");
        }

        private void ResetMouseCapture()
        {
            if (currentlySelectedImage != null)
            {
                Mouse.Capture(null); // Maus von der aktuellen Auswahl freigeben
                currentlySelectedImage = null; // Zustand zurücksetzen
                currentlySelectedBorder = null; // Zustand zurücksetzen
            }
        }
        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }
        private void ShowImageInfo(int imageId)
        {
            // Überprüfen, ob das ImageData-Objekt existiert
            if (imageDataDictionary.ContainsKey(imageId))
            {
                ImageData imageData = imageDataDictionary[imageId];
                ImageInfoBox.Text = $"Bild-ID: {imageData.Id}\n" +
                                    $"Dateipfad: {imageData.FilePath}\n" +
                                    $"Ursprüngliche Größe: {imageData.OriginalWidth} x {imageData.OriginalHeight}\n" +
                                    $"Ursprüngliche Position: ({imageData.OriginalX}, {imageData.OriginalY})\n" +
                                    $"Aktuelle Größe: {imageData.CurrentWidth} x {imageData.CurrentHeight}\n" +
                                    $"Aktuelle Position: ({imageData.CurrentX}, {imageData.CurrentY})";
            }
            else
            {
                ImageInfoBox.Text = "Kein Bild ausgewählt.";
            }
        }
        private void ShowModeButtons()
        {
            MoveButton.Visibility = Visibility.Visible;
            ScaleButton.Visibility = Visibility.Visible;
            DrawButton.Visibility = Visibility.Visible;
            EraseButton.Visibility = Visibility.Visible;
        }
    }
}
