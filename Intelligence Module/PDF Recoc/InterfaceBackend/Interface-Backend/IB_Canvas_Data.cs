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
        public IB_Image[] _images;

        public bool AddImage(string filepath)
        {
            // not implemented
            return false;
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

        public IB_Image(int id, string pathToImg, Bitmap bitmap)
        {
            this._id = id;
            this._pathToImg = pathToImg;
            this._bitMap = bitmap;
        }

        public IB_Image(Point pos, string pathToImg, string pathToDb, int width, int height, float scale)
        {
            this._pos = pos;
            this._pathToImg = pathToImg;
            this._pathToDb = pathToDb;
            this._width = width;
            this._height = height;
            this._scale = scale;
        }

        public IB_Image(Point pos, string pathToImg, string pathToDb, int width, int height, float scale, int cutoutX, int cutoutY)
        {
            this._pos = pos;
            this._pathToImg = pathToImg;
            this._pathToDb = pathToDb;
            this._width = width;
            this._height = height;
            this._scale = scale;
            this._cutoutX = cutoutX;
            this._cutoutY = cutoutY;
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
            if (_bitMap != null)
            {
                using (var memoryStream = new System.IO.MemoryStream())
                {
                    _bitMap.Save(memoryStream, System.Drawing.Imaging.ImageFormat.Png);
                    memoryStream.Seek(0, System.IO.SeekOrigin.Begin);

                    var bitmapImage = new BitmapImage();
                    bitmapImage.BeginInit();
                    bitmapImage.StreamSource = memoryStream;
                    bitmapImage.CacheOption = BitmapCacheOption.OnLoad;
                    bitmapImage.EndInit();

                    return bitmapImage;
                }
            }

            // Optional: Rückgabewert, falls kein Bitmap verfügbar ist
            return null;
        }

    }
}
