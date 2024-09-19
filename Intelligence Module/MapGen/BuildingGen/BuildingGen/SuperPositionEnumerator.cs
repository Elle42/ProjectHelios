using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BuildingGen
{
    internal class SuperPositionEnumerator : IEnumerator
    {
        private SuperPosition superPosition;
        private int index = -1;
        public SuperPositionEnumerator(SuperPosition supPos)
        { 
            this.superPosition = supPos;
        }

        object IEnumerator.Current
        {
            get { return this.superPosition.GetPosibility(index); }
        }

        bool IEnumerator.MoveNext()
        {
            return ++this.index < this.superPosition.GetLength();
        }

        void IEnumerator.Reset()
        {
            this.index = -1;
        }
    }
}
