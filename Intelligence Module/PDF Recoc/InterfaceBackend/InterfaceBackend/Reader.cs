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
            var parser = new FileIniDataParser();

            // Load´the right root path

#if DEBUG
            // Set the executable Path based on the curret mode of execution
            this._executableRootPath = Directory.GetParent(Environment.CurrentDirectory).Parent.Parent.Parent.FullName;
            Console.WriteLine("Debug " + _executableRootPath);

            // Read the conf file
            IniData conf = parser.ReadFile("D:\\Matura Project\\Repos\\Intelligence Module\\PDF Recoc\\conf.ini");
#else
            // Set the executable Path based on the curret mode of execution
            this._executableRootPath = AppDomain.CurrentDomain.BaseDirectory;
            Console.WriteLine("EXE " + _executableRootPath);

            // Read the conf file
            IniData data = parser.ReadFile(AppDomain.CurrentDomain.BaseDirectory);
#endif

            this._pathToPdf = pathToPdf;

            this._pathToPdfFolder = conf["general"]["pdfRootPath"];

            Console.WriteLine(conf["general"]["pdfRootPath"]);

            // Copy Pdf in the right Directories and add them to my working Dir
            try
            {
                File.Copy(_pathToPdf, Path.Combine(Directory.GetParent(_executableRootPath).FullName ,_pathToPdfFolder));

            }
            catch
            {
                throw new NotImplementedException();
            }
        }

        public bool ReadPdf(int[] pages)
        {
            throw new NotImplementedException();
        }

        public bool ReadPdf(string[] pages)
        {
            throw new NotImplementedException();
        }

        public Picture[] GetPictures()
        {
            throw new NotImplementedException();
        }
    }
}
