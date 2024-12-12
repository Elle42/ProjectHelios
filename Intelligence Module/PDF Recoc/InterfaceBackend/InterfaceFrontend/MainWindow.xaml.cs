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
    /// 



    //BLABALABKAPAN
    public partial class MainWindow : Window
    {
        private Point mouseClickPosition;
        private string currentMode = "None";
        private const int MaxImageWidth = 800;
        private const int MaxImageHeight = 600;

        private int imageCounter = 0;
        private readonly Dictionary<int, IB_Canvas_Data> imageDataDictionary = new Dictionary<int, IB_Canvas_Data>();
        private readonly List<IB_Image> uploadedImages = new List<IB_Image>();
        private readonly List<Border> imageBorders = new List<Border>();

        private Image currentlySelectedImage;
        private Border currentlySelectedBorder;

        public MainWindow()
        {
            InitializeComponent();
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            WindowStyle = WindowStyle.SingleBorderWindow;
            Topmost = true;
            WindowState = WindowState.Maximized;
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
            if (InfoCurrentImageBox.Visibility == Visibility.Visible)
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
            var selectedMode = (imageSelectionComboBox.SelectedItem as ComboBoxItem)?.Content?.ToString();
            confirmButton.Visibility = selectedMode == "Multi" ? Visibility.Visible : Visibility.Collapsed;
            uploadButton.Visibility = Visibility.Visible;
        }

        private void uploadButton_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog { Multiselect = true };

            if (openFileDialog.ShowDialog() == true)
            {
                foreach (var fileName in openFileDialog.FileNames)
                {
                    LoadImage(fileName);
                }

                if ((imageSelectionComboBox.SelectedItem as ComboBoxItem)?.Content?.ToString() == "Single")
                {
                    ConfirmUploadForSingle();
                }
            }
        }

        private void LoadImage(string filePath)
        {
            try
            {
                // Erstelle und füge das Bild über IB_Canvas_Data hinzu
                IB_Canvas_Data canvasData = new IB_Canvas_Data();
                bool imageAdded = canvasData.AddImage(filePath);

                if (imageAdded)
                {
                    // Optional: Wenn du auch ein Bitmap davon im UI-Canvas hinzufügen möchtest:
                    IB_Image image = canvasData.FindImage(canvasData.GetAllImages().Length - 1); // Das zuletzt hinzugefügte Bild
                    BitmapImage bitmapImage = new BitmapImage(new Uri(image.GetPathImage(image)));

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
                }
                else
                {
                    Console.WriteLine("Bild konnte nicht hinzugefügt werden.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error uploading image: {ex.Message}");
            }
        }


        private void CenterElementOnCanvas(UIElement element)
        {
            double centerX = (imageCanvas.ActualWidth - ((FrameworkElement)element).Width) / 2;
            double centerY = (imageCanvas.ActualHeight - ((FrameworkElement)element).Height) / 2;

            Canvas.SetLeft(element, centerX);
            Canvas.SetTop(element, centerY);
        }

        private void ConfirmUploadForSingle()
        {
            uploadButton.Visibility = Visibility.Collapsed;
            ShowModeButtons();
        }

        private void ConfirmButton_Click(object sender, RoutedEventArgs e)
        {
            uploadButton.Visibility = Visibility.Collapsed;
            ShowModeButtons();
        }

        private void Image_LeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (sender is Border border)
            {
                currentlySelectedBorder = border;
                currentlySelectedImage = border.Child as Image;
                mouseClickPosition = e.GetPosition(imageCanvas);
            }
        }

        private void Image_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            Mouse.Capture(null);
        }

        private void ImageCanvas_MouseMove(object sender, MouseEventArgs e)
        {
            if (currentlySelectedImage != null && e.LeftButton == MouseButtonState.Pressed)
            {
                if (currentMode == "Move")
                {
                    MoveImage(e);
                }
            }
        }

        private void MoveImage(MouseEventArgs e)
        {
            var currentMousePosition = e.GetPosition(imageCanvas);
            double offsetX = currentMousePosition.X - mouseClickPosition.X;
            double offsetY = currentMousePosition.Y - mouseClickPosition.Y;

            Canvas.SetLeft(currentlySelectedBorder, Canvas.GetLeft(currentlySelectedBorder) + offsetX);
            Canvas.SetTop(currentlySelectedBorder, Canvas.GetTop(currentlySelectedBorder) + offsetY);

            mouseClickPosition = currentMousePosition;
        }

        private void Image_MouseWheel(object sender, MouseWheelEventArgs e)
        {
            if (currentlySelectedImage == null || currentMode != "Scale") return;

            double scaleFactor = e.Delta > 0 ? 1.05 : 0.95;
            var transform = currentlySelectedImage.RenderTransform as ScaleTransform ?? new ScaleTransform(1, 1);
            currentlySelectedImage.RenderTransform = transform;

            transform.ScaleX *= scaleFactor;
            transform.ScaleY *= scaleFactor;
        }

        private void DrawButton_Click(object sender, RoutedEventArgs e) => SetMode("Draw");
        private void EraseButton_Click(object sender, RoutedEventArgs e) => SetMode("Erase");
        private void ScaleButton_Click(object sender, RoutedEventArgs e) => SetMode("Scale");
        private void ImageMove_Click(object sender, RoutedEventArgs e) => SetMode("Move");

        private void SetMode(string mode)
        {
            currentMode = mode;
            Console.WriteLine($"Mode switched to {mode}");
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
