using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Point = System.Windows.Point;
using Image = System.Windows.Controls.Image;
using Brushes = System.Windows.Media.Brushes;

namespace Interface
{
    public class ImageData
    {
        public Image Image { get; set; }
        public Point OriginalPosition { get; set; }
        public double OriginalScale { get; set; } = 1.0;
        public Point CurrentPosition { get; set; }
        public double CurrentScale { get; set; } = 1.0;
        public Border ImageBorder { get; set; }

        public int Id { get; set; }
        public string FilePath { get; set; }
        public double OriginalWidth { get; set; }
        public double OriginalHeight { get; set; }
        public double OriginalX { get; set; }
        public double OriginalY { get; set; }
        public double CurrentWidth { get; set; }
        public double CurrentHeight { get; set; }
        public double CurrentX { get; set; }
        public double CurrentY { get; set; }


        public ImageData(int id, Image image, Point originalPosition, Border imageBorder)
        {
            Id = id;
            Image = image;
            OriginalPosition = originalPosition;
            CurrentPosition = originalPosition;
            ImageBorder = imageBorder;
        }

        public ImageData() { }
    }
}
