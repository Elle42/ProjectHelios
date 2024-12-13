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
            // IB_Reader r = new IB_Reader("D:\\Matura Project\\Repos\\Pläne\\GIA\\Brandschutzpläne_06_2024.pdf", pages, IB_Reader.Rotation.NoRotation);

            string[] paths = new string[]
            {
                "D:\\Matura Project\\Repos\\Pläne\\GIA\\BSP_BUERO_EG.pdf",
                "D:\\Matura Project\\Repos\\Pläne\\GIA\\BSP_BUERO_OG.pdf",
                "D:\\Matura Project\\Repos\\Pläne\\GIA\\BSP_LAGER.pdf"
            };

            IB_Reader r2 = new IB_Reader(@"GIA", paths, IB_Reader.Rotation.NoRotation);

            Console.ReadLine();
        }
    }
}