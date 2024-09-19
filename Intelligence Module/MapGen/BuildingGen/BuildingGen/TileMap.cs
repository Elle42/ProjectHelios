using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;

namespace BuildingGen
{
    class TileMap
    {
        public const int MAXPOSIBLE = 3;

        private int height;
        private int width;
        private List<Tile> Map;
        public TileMap(int width, int height, SuperPosition superPosTemplate) 
        { 
            Map = new List<Tile>(width * height);

            int i = 0;

            for(i = 0; i < width * height; i++)
            {
                Map.Add( new Tile(superPosTemplate));
            }
            Console.WriteLine( i.ToString() + " Elements");

            this.height = height;
            this.width = width;
        }

        public int GetLength()
        {
            return Map.Count;
        }

        public Tile GetTile2D(int x, int y)
        {
            return Map[(x*y) + x];
        }

        public int CollapseTile2D(int x, int y)
        {
            return Map[(width * y) + x].Collapse();
        }

        // ----------------------------------------------------------------------------------
        // Propagation
        // ----------------------------------------------------------------------------------
        public bool Propagation(int x, int y, int depth)
        {

            if(depth > 0)
            {
                if(x > 0)
                {
                    PropLeft(x, y);
                    if(!Propagation(x-1,y,depth-1))
                    {
                        return false;
                    }
                }
                if (x < width - 1)
                {
                    PropRight(x, y);
                    if (!Propagation(x + 1, y, depth - 1))
                    {
                        return false;
                    }
                }
                if (y < height - 1)
                {
                    PropUp(x, y);
                    if (!Propagation(x, y + 1, depth - 1))
                    {
                        return false;
                    }
                }
                if (y > 0)
                {
                    PropDown(x, y);
                    if (!Propagation(x, y - 1, depth - 1))
                    {
                        return false;
                    }
                }
                return true;
            }
            else 
            {
                return true;
            }
        }

        private bool PropRight(int x, int y)
        {
            int[] temp = new int[MAXPOSIBLE];
            temp = this.GetTile2D(x + 1, y).GetSuperPosition().GetPosibilityIds();
            if (temp.Length == 0)
            {
                return false;
            }
            else
            {
                this.GetTile2D(x - 1, y).GetSuperPosition().ComparePosibilityIds(temp);
                return true;
            }
        }
        private bool PropLeft(int x, int y)
        {
            int[] temp = new int[MAXPOSIBLE];
            temp = this.GetTile2D(x - 1, y).GetSuperPosition().GetPosibilityIds();
            if (temp.Length == 0)
            {
                return false;
            }
            else
            {
                this.GetTile2D(x - 1, y).GetSuperPosition().ComparePosibilityIds(temp);
                return true;
            }
        }
        private bool PropUp(int x, int y)
        {
            int[] temp = new int[MAXPOSIBLE];
            temp = this.GetTile2D(x, y-1).GetSuperPosition().GetPosibilityIds();
            if (temp.Length == 0)
            {
                return false;
            }
            else
            {
                this.GetTile2D(x, y + 1).GetSuperPosition().ComparePosibilityIds(temp);
                return true;
            }
        }
        private bool PropDown(int x, int y)
        {
            int[] temp = new int[MAXPOSIBLE];
            temp = this.GetTile2D(x, y + 1).GetSuperPosition().GetPosibilityIds();
            if (temp.Length == 0)
            {
                return false;
            }
            else
            {
                this.GetTile2D(x, y + 1).GetSuperPosition().ComparePosibilityIds(temp);
                return true;
            }
        }

        // ----------------------------------------------------------------------------------

        public void ConsoleLogTiles()
        {
            int row = 0;
            int col = 0;
            foreach(Tile t in Map)
            {
                
                if(col == 10)
                {
                    col = 0;
                    row++;
                    Console.WriteLine();
                }
                foreach (Posibility p in t.GetSuperPosition())
                {
                    Console.Write(p.tileId + " ");
                }
                Console.Write(@" | ");
                col++;
            }
        }
    }
    class Tile
    {
        private int entropy;
        private SuperPosition superPosition;
        private bool Collapsed;

        public Tile(SuperPosition superPositionTemplate)
        {
            superPosition = new SuperPosition(superPositionTemplate.GetPosibilities());

            entropy = 0;
            Collapsed = false;
        }

        public bool IsCollapsed()
        {
            return Collapsed;
        }

        public SuperPosition GetSuperPosition()
        {
            return superPosition;
        }

        public int Collapse()
        {
            Random rn = new Random(DateTime.Now.Millisecond);
            int WeightSum = 0;

            foreach(Posibility p in superPosition)
            {
                WeightSum += p.weight;
            }

            int Collapsed = rn.Next(WeightSum);
            Console.WriteLine("Random => " + Collapsed);

            for(int i = 0; i < superPosition.GetLength(); i++)
            {
                if(superPosition.GetPosibility(i).weight >= Collapsed)
                {
                    superPosition.Collapse(i);
                    this.Collapsed = true;
                    return 1;
                }
                else
                {
                    Collapsed -= superPosition.GetPosibility(i).weight;
                }
            }

            return 0;
        }
    }

    class SuperPosition : IEnumerable
    {
        private LinkedList<Posibility> _Posibilities;


        public SuperPosition(LinkedList<Posibility> posibilities)
        {
            this._Posibilities = new LinkedList<Posibility>();
            foreach(Posibility p in posibilities)
            {
                this._Posibilities.AddLast(p);
            }
        }

        public IEnumerator GetEnumerator()
        {
            return new SuperPositionEnumerator(this);
        }

        public Posibility GetPosibility(int i)
        { 
            return this._Posibilities.ElementAt(i);
        }

        public LinkedList<Posibility> GetPosibilities()
        {
            return this._Posibilities;
        }

        public int[] GetPosibilityIds()
        {
            int[] temp = new int[TileMap.MAXPOSIBLE];
            foreach(Posibility p in _Posibilities)
            {
                temp.Append(p.tileId);
            }

            return temp;
        }

        public void ComparePosibilityIds(int[] posibilityIds)
        {
            var node = _Posibilities.First;
            while (node != null)
            {
                var nextNode = node.Next;
                if (!posibilityIds.Contains(node.Value.tileId))
                {
                    _Posibilities.Remove(node);
                }
                node = nextNode;
            }
        }

        public int GetLength()
        {
            return this._Posibilities.Count;
        }

        public void Collapse(int id)
        {
            Posibility temp = _Posibilities.ElementAt(id);
            _Posibilities.Clear();
            _Posibilities.AddFirst(temp);
        }

        public override string ToString()
        {
            return base.ToString();
        }
    }

    struct Posibility
    {
        public int weight { get; set; }
        public int tileId { get; set; }
    }
}
