using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using InterfaceBackend;


namespace InterfaceFrontend
{
    /// <summary>
    /// Interaktionslogik für MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        
        private Point mouseClickPosition;
        private string currentMode = "None";
        private const int MaxImageWidth = 800; // Maximale Breite in Pixel
        private const int MaxImageHeight = 600; // Maximale Höhe in Pixel
        private IB_Canvas_Data imageDataDictionary;
        private int imageCounter = 0; // Zähler für Bild-IDs    
        private Image currentlySelectedImage;
        private Border currentlySelectedBorder;
        private Point imageOriginalPosition;

        public MainWindow()
        {
            InitializeComponent();
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            this.WindowStyle = WindowStyle.SingleBorderWindow;
            this.Topmost = true;
            this.WindowState = WindowState.Maximized;
        }



        private void BurgerMenuToggleButton_Click(object sender, RoutedEventArgs e)
        {
            if (SideMenu.Visibility == Visibility.Visible)
            {
                SideMenu.Visibility = Visibility.Collapsed;
                InfoCurrentImageBox.Visibility = Visibility.Collapsed;
                InfoCurrentImage.Visibility = Visibility.Collapsed;
                Background = Brushes.White;
            }
            
            else    
            {
                SideMenu.Visibility = Visibility.Visible;
                InfoCurrentImage.Visibility = Visibility.Visible;
                Background = Brushes.LightGray;
            }
        }

        private void InfoCurrentImage_Click(object sender, RoutedEventArgs e)
        {
            if(InfoCurrentImageBox.Visibility == Visibility.Visible)
            {
                InfoCurrentImageBox.Visibility = Visibility.Collapsed;
            }
            else
            {
                InfoCurrentImageBox.Visibility = Visibility.Visible;
            }
        }



        private void ImageSelectionComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            var selectedMode = (imageSelectionComboBox.SelectedItem as ComboBoxItem).Content.ToString();
            confirmButton.Visibility = selectedMode == "Multi" ? Visibility.Visible : Visibility.Collapsed;
            uploadButton.Visibility = selectedMode == "Single" ? Visibility.Visible : Visibility.Visible;
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

                if ((imageSelectionComboBox.SelectedItem as ComboBoxItem).Content.ToString() == "Single")
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

                // Skalierungsfaktor berechnen
                double scaleFactor = Math.Min(
                    MaxImageWidth / (double)bitmapImage.PixelWidth,
                    MaxImageHeight / (double)bitmapImage.PixelHeight);

                // Neues Bild erstellen
                Image newImage = new Image
                {
                    Source = bitmapImage,
                    Width = bitmapImage.PixelWidth * scaleFactor,
                    Height = bitmapImage.PixelHeight * scaleFactor
                };

                // Border für das Bild erstellen
                Border newBorder = new Border
                {
                    Width = newImage.Width,
                    Height = newImage.Height,
                    Child = newImage,
                    BorderBrush = Brushes.Transparent,
                    BorderThickness = new Thickness(1)
                };

                // Bild zentriert auf das Canvas platzieren
                double centerX = (imageCanvas.ActualWidth - newBorder.Width) / 2;
                double centerY = (imageCanvas.ActualHeight - newBorder.Height) / 2;

                Canvas.SetLeft(newBorder, centerX);
                Canvas.SetTop(newBorder, centerY);
                imageCanvas.Children.Add(newBorder);

                // Daten im Dictionary speichern
                imageDataDictionary = new IB_Canvas_Data
                {
                    
                };

                // Event-Handler für Interaktivität hinzufügen
                newBorder.MouseLeftButtonDown += Image_LeftButtonDown;
                newBorder.MouseMove += ImageCanvas_MouseMove;
                newBorder.MouseLeftButtonUp += Image_MouseLeftButtonUp;

                imageCounter++;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading image: {ex.Message}");
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
            //currentlySelectedImageData = imageDataList.Find(data => data.Id == imageId);

            //if (currentlySelectedImageData == null) return;

            //foreach (var data in imageDataList)
            //{
            //    if (data.ImageBorder != null)
            //        data.ImageBorder.BorderBrush = Brushes.Transparent;
            //}

            //currentlySelectedImageData.ImageBorder.BorderBrush = Brushes.Blue;
            //mouseClickPosition = e.GetPosition(imageCanvas);
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
            // Function for drawing to a bitmap
            throw new NotImplementedException();
        }

        // Löschfunktion
        private void EraseFromImage(MouseEventArgs e)
        {
            // Function for erasing from a bitmap
            throw new NotImplementedException();
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

                //currentlySelectedImageData.CurrentWidth = newWidth;
                //currentlySelectedImageData.CurrentHeight = newHeight;

            }
        }

        private void UpdateBorderSize()
        {
            throw new NotImplementedException();
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
      
        private void ShowImageInfo(int imageId)
        {
            throw new NotImplementedException();
        }
        private void ShowModeButtons()
        {
            MoveButton.Visibility = Visibility.Visible;
            ScaleButton.Visibility = Visibility.Visible;
            DrawButton.Visibility = Visibility.Visible;
            EraseButton.Visibility = Visibility.Visible;
        }

        private void InfoCurrentImage_Checked(object sender, RoutedEventArgs e)
        {

        }
    }
}
