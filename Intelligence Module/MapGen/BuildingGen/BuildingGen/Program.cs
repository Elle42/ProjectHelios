using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BuildingGen
{
    internal class Program
    {
        static void Main(string[] args)
        {
            LinkedList<Posibility> list = new LinkedList<Posibility>();
            list.AddLast(new Posibility { tileId = 0, weight = 3});
            list.AddLast(new Posibility { tileId = 1, weight = 1});
            list.AddLast(new Posibility { tileId = 2, weight = 2});

            SuperPosition supPosTemp = new SuperPosition(list);

            TileMap tileMap = new TileMap(10,10,supPosTemp);;

            tileMap.ConsoleLogTiles();

            Console.WriteLine();
            Console.WriteLine("----------------------------------------");
            Console.WriteLine();

            tileMap.CollapseTile2D(3,3);

            tileMap.ConsoleLogTiles();

            Console.WriteLine();
            Console.WriteLine("----------------------------------------");
            Console.WriteLine();

            tileMap.Propagation(3,3,3);

            tileMap.ConsoleLogTiles();

            Console.ReadLine();
        }
    }
}
