using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using IniParser;
using IniParser.Model;

namespace InterfaceBackend
{
    class Reader
    {
        private string _pathToPdf;
        private string _pathToPdfFolder;

        /// <summary>
        /// Pdf muss noch nicht in dem Dafür vorgesehenen Folder sein
        /// </summary>
        /// <param name="pathToPdf"></param>
        public Reader(string pathToPdf)
        {
            this._pathToPdf = pathToPdf;

            var parser = new FileIniDataParser();
            // IniData data = parser.ReadFile(AppDomain.CurrentDomain.BaseDirectory);
            IniData data = parser.ReadFile("D:\\Matura Project\\Repos\\Intelligence Module\\PDF Recoc\\conf.ini");

            Console.WriteLine(data["general"]["pdfRootPath"]);
        }

        public bool ReadPdf()
        {
            return true;
        }
    }
}
