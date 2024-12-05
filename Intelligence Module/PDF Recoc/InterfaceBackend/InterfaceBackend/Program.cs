using System;

namespace InterfaceBackend
{
    internal class Program
    {
        static void Main(string[] args)
        {

            // Console.WriteLine(AppDomain.CurrentDomain.BaseDirectory);
            int[] pages = new int[] { 1, 2, 3 };
            IB_Reader r = new IB_Reader(@"C:\Users\mutte\Desktop\MFH-RF1-Brandschutzplan.pdf", pages, IB_Reader.Rotation.NoRotation);

            

            Console.ReadLine();
        }
    }
}