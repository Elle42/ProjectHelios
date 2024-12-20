﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;

namespace InterfaceBackend
{
    /// <summary>
    /// Canvas Contains all Pictures Currently on Screen and contains the information of their position orientation and scaling
    /// </summary>
    public class IB_Canvas_Data
    {
        private IB_Image[] _images;
        
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


        IB_Image(Point pos, string pathToImg, string pathToDb, int width, int height, float scale)
        {
            this._pos = pos;
            this._pathToImg = pathToImg;
            this._pathToDb = pathToDb;
            this._width = width;
            this._height = height;
            this._scale = scale;
        }

        IB_Image(Point pos, string pathToImg, string pathToDb, int width, int height, float scale, int cutoutX, int cutoutY)
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
    }
}
