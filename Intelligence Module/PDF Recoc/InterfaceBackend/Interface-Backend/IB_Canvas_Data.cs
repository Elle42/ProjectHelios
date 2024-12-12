using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using System.Windows.Media;
using System.Windows.Media.Imaging;


namespace InterfaceBackend
{
    /// <summary>
    /// Canvas Contains all Pictures Currently on Screen and contains the information of their position orientation and scaling
    /// </summary>
    public class IB_Canvas_Data
    {
        private IB_Image[] _images;
        private Logger _logger;


        IB_Canvas_Data(IB_Image[] images)
        {
            _images = images;
            _logger = new Logger();
        }

        public bool RemoveImage(IB_Image image)
        {
            // not implemented
            return false;
        }

        public IB_Image FindImage(int id)
        {
            return null;
        }

        public IB_Image[] GetAllImages()
        {
            return _images;
        }

        /// <summary>
        /// Register A new Bitmap into The Canvas
        /// </summary>
        /// <param name="path"></param>
        public void RegisterImage(string path)
        {
            try
            {
                // Load the bitmap from the specified file path
                using (Bitmap bitmap = new Bitmap(path))
                {
                    IB_Image img = new IB_Image(path, bitmap);
                    _images.Append(img);
                }
            }
            catch (Exception ex)
            {
                _logger.Log(ex.Message, LogLevel.Error);
                throw;
            }
        }

    }

    /// <summary>
    /// Picture Contains the Reference to the used Png and all the infos for this specific image
    /// </summary>
    public class IB_Image
    {

        private int _id;
        private Point _pos;
        private string _pathToImg;
        private string _pathToDb;
        private int _width;
        private int _height;
        private float _scale;
        private int _cutoutX;
        private int _cutoutY;
        private Bitmap _bitMap;

        private Logger _logger;

        public IB_Image(string pathToImg, Bitmap bitmap)
        {
            this._pathToImg = pathToImg;
            this._bitMap = bitmap;
            this._width = bitmap.Width;
            this._height = bitmap.Height;
        }

        public string GetPathImage()
        {
            return this._pathToImg;
        }

        public Bitmap GetBitmap()
        {
            return this._bitMap;
        }

        public ImageSource GetSource()
        {
            using (var memory = new System.IO.MemoryStream())
            {
                // Speichert die Bitmap als PNG in den MemoryStream
                _bitMap.Save(memory, System.Drawing.Imaging.ImageFormat.Png);
                memory.Position = 0;

                // Erstelle ein BitmapImage aus dem MemoryStream
                var bitmapImage = new BitmapImage();
                bitmapImage.BeginInit();
                bitmapImage.StreamSource = memory;
                bitmapImage.CacheOption = BitmapCacheOption.OnLoad;
                bitmapImage.EndInit();

                return bitmapImage;
            }
        }
    }
}
