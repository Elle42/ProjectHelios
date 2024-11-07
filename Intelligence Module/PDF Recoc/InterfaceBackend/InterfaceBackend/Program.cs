using System;

namespace InterfaceBackend
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");

            // Console.WriteLine(AppDomain.CurrentDomain.BaseDirectory);

            Reader r = new Reader("test");

            Console.ReadLine();
        }
    }
}