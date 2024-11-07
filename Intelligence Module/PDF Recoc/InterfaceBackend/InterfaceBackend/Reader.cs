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
        private string _executableRootPath;

        /// <summary>
        /// Reads a Pdf and copys it into the working Directory of the Conversion Software
        /// </summary>
        /// <param name="pathToPdf"></param>
        public Reader(string pathToPdf)
        {
#if DEBUG
            this._executableRootPath = Directory.GetParent(Environment.CurrentDirectory).Parent.Parent.FullName;
            Console.WriteLine("Debug " + _executableRootPath);
#else
            this._executableRootPath = AppDomain.CurrentDomain.BaseDirectory;
            Console.WriteLine("EXE " + _executableRootPath);
#endif

            this._pathToPdf = pathToPdf;

            var parser = new FileIniDataParser();
            // IniData data = parser.ReadFile(AppDomain.CurrentDomain.BaseDirectory);    <------ Wenn das Projekt gebaut wird muss es so verwendet werden
            IniData data = parser.ReadFile("D:\\Matura Project\\Repos\\Intelligence Module\\PDF Recoc\\conf.ini");

            this._pathToPdfFolder = data["general"]["pdfRootPath"];

        }

        public bool ReadPdf()
        {
            return true;
        }
    }
}
