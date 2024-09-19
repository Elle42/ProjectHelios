using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BuildingGen
{
    internal class RuleSet
    {
        private List<TileRules> _RuleSet;

        enum Dir
        {
            Top = 1,
            Right = 2,
            Bottom = 3,
            Left = 4
        }

        public RuleSet()
        { 
            _RuleSet= new List<TileRules>();
            _RuleSet.Append(new TileRules(0, new int[]{1,2}, new int[] { 1, 2 }, new int[] { 1, 2 }, new int[] { 1, 2 }));
            _RuleSet.Append(new TileRules(1, new int[]{1,2,3}, new int[] { 1, 2 ,3}, new int[] { 1, 2 ,3}, new int[] { 1, 2 ,3}));
            _RuleSet.Append(new TileRules(2, new int[]{2,3}, new int[] {2 ,3}, new int[] {2 ,3}, new int[] {2 ,3}));
        }

        public int[] GetRules(int id, int dir)
        {
            switch(dir)
            {
                case (int)Dir.Top:
                    return _RuleSet[id].TopWL;
                case (int)Dir.Right:
                    return _RuleSet[id].RightWL;
                case (int)Dir.Left: 
                    return _RuleSet[id].LeftWL;
                case (int)Dir.Bottom:
                    return _RuleSet[id].BottomWL;
                default:
                    return new int[]{ };
            }
        }
    }

    public class TileRules
    {
        public TileRules(int id, int[] top, int[] bot, int[] left, int[] right)
        {
            Id = id;
            TopWL = top;
            BottomWL = bot;
            LeftWL = left;
            RightWL = right;
        }



        int Id;
        public int[] TopWL { get; }
        public int[] BottomWL { get; }
        public int[] RightWL { get; }
        public int[] LeftWL { get; }
    }
}
