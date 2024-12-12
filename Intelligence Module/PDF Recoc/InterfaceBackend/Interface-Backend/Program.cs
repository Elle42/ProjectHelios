using System;

namespace InterfaceBackend
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");

            // Console.WriteLine(AppDomain.CurrentDomain.BaseDirectory);
            int[] pages = new int[] { 1, 2, 3 };
            IB_Reader r = new IB_Reader("C:\\Users\\Elias.Mutter\\Documents\\Repos\\Pläne\\GIA\\Brandschutzpläne_06_2024.pdf", pages);

            

            Console.ReadLine();
        }
    }
}