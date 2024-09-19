using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static System.Net.Mime.MediaTypeNames;
using System.Drawing;

namespace BuildingGen
{
    internal class GridRender
    {
        private TileMap tileMap;

        public GridRender(TileMap tileMap) 
        {
            this.tileMap = tileMap;
        }

        public void Render2Image()
        {
            int tileSize = 32;

            int mapWidth = tileMap.GetLength(1) * tileSize;
            int mapHeight = tileMap.GetLength(0) * tileSize;
            Bitmap mapImage = new Bitmap(mapWidth, mapHeight);

            string Grass = "Grass.png";
            string Water = "Water.png";

            Bitmap grassTile = (Bitmap)Image.FromFile(@"D:\Matura Project\Generator\WaveFunctionCollapse\WFCTest\WFCTest\Grass.png", true);
            Bitmap waterTile = (Bitmap)Image.FromFile(@"D:\Matura Project\Generator\WaveFunctionCollapse\WFCTest\WFCTest\Water.png", true);

            using (Graphics g = Graphics.FromImage(mapImage))
            {
                for (int y = 0; y < tileMap.GetLength(0); y++)
                {
                    for (int x = 0; x < tileMap.GetLength(1); x++)
                    {
                        int tileType = tileMap[y, x];

                        Bitmap tileImage = (tileType == 0) ? grassTile : waterTile;

                        // Draw the tile at the correct position
                        g.DrawImage(tileImage, x * tileSize, y * tileSize, tileSize, tileSize);
                    }
                }
            }

            // Save the rendered map as an image file
            mapImage.Save(@"D:\Matura Project\Generator\WaveFunctionCollapse\WFCTest\WFCTest\Output.png");

            Console.WriteLine("Tile map rendered and saved as tileMapOutput.png");
        }
    }
}
