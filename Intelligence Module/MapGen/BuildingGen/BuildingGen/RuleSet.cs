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

        public RuleSet()
        { 
            _RuleSet= new List<TileRules>();
            _RuleSet.Append(new TileRules(1, new int[]{1,2}, new int[] { 1, 2 }, new int[] { 1, 2 }, new int[] { 1, 2 }));
            _RuleSet.Append(new TileRules(2, new int[]{1,2,3}, new int[] { 1, 2 ,3}, new int[] { 1, 2 ,3}, new int[] { 1, 2 ,3}));
            _RuleSet.Append(new TileRules(3, new int[]{2,3}, new int[] {2 ,3}, new int[] {2 ,3}, new int[] {2 ,3}));
        }

        public TileRules GetRules(int id)
        {
            return _RuleSet[id];
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
        int[] TopWL;
        int[] BottomWL;
        int[] RightWL;
        int[] LeftWL;
    }
}
