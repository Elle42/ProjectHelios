using System;

namespace InterfaceBackend
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");

            // Console.WriteLine(AppDomain.CurrentDomain.BaseDirectory);

            Reader r = new Reader("D:\\Matura Project\\Repos\\Pläne\\HTL\\Brandschutzplan 255C - 1.OG - Werkstättentrakt HTL.pdf");

            int[] pages = new int[] { 1, 2, 3 };

            Console.ReadLine();
        }
    }
}