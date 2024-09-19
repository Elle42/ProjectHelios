using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BuildingGen
{
    internal class RandGen
    {
        Random Randomr;

        public RandGen(int seed) 
        { 
            Randomr = new Random(seed);
        }

        public int RandTop(int top)
        {
            return Randomr.Next(top);
        }

        public int RandMinTop(int min, int top)
        {
            return Randomr.Next(min, top);
        }
    }
}
