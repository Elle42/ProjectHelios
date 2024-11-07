using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace InterfaceBackend
{
    /// <summary>
    /// Canvas Contains all Pictures Currently on Screen and contains the information of their position orientation and scaling
    /// </summary>
    class Canvas
    {
        private Picture[] pictures;
        
    }

    /// <summary>
    /// Picture Contains the Reference to the used Png and all the infos for this specific image
    /// </summary>
    class Picture
    {
        private string _pathToImg;
        private string _pathToDb;
        private int _width;
        private int _height;
        private float _scale;
        private int _cutoutX;
        private int _cutoutY;

        Picture(string pathToOmg, string pathToDb, int width, int height, float scale)
        {
            this._pathToImg = pathToOmg;
            this._pathToDb = pathToDb;
            this._width = width;
            this._height = height;
            this._scale = scale;
        }

        Picture(string pathToOmg, string pathToDb, int width, int height, float scale, int cutoutX, int cutoutY)
        {
            this._pathToImg = pathToOmg;
            this._pathToDb = pathToDb;
            this._width = width;
            this._height = height;
            this._scale = scale;
            this._cutoutX = cutoutX;
            this._cutoutY = cutoutY;
        }
    }
}
