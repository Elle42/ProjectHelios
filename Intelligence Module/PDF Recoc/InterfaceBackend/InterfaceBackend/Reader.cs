using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using IniParser;
using IniParser.Model;
using Serilog;
using Serilog.Sinks.File;
using Serilog.Sinks.SystemConsole;

namespace InterfaceBackend
{
    class IB_Reader
    {
        private string _pathToPdf;
        private string _pathToPdfFolder;
        private string _executableRootPath;

        /// <summary>
        /// Reads a Pdf and copys it into the working Directory of the Conversion Software
        /// </summary>
        /// <param name="pathToPdf"></param>
        /// <param name="pages"></param>
        public IB_Reader(string pathToPdf, int[] pages)
        {
            var parser = new FileIniDataParser();

            // Load´the right root path

#if DEBUG
            // Set the executable Path based on the curret mode of execution
            this._executableRootPath = Directory.GetParent(Environment.CurrentDirectory).Parent.Parent.Parent.FullName;
            Console.WriteLine("Debug " + _executableRootPath);

            // Read the conf file
            IniData conf = parser.ReadFile(Directory.GetParent(_executableRootPath).FullName + "\\conf.ini");
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
                Console.WriteLine("Return: " + Directory.GetParent(_executableRootPath).Parent.FullName);
                Console.WriteLine("PathToPdf: " + _pathToPdf);
                Console.WriteLine("Folder: " + Directory.GetParent(_executableRootPath).FullName + _pathToPdfFolder + "\\" + _pathToPdf.Split('\\').Last());
                File.Copy(_pathToPdf, Directory.GetParent(_executableRootPath).FullName + _pathToPdfFolder + "\\" + _pathToPdf.Split('\\').Last());

            }
            catch (UnauthorizedAccessException uaex)
            {
                Console.WriteLine("you are not permitted to acces the specified Directory!");
                Console.WriteLine(uaex.Message);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        public bool ReadPdf()
        {
            throw new NotImplementedException();
        }

        public bool ReadPdf(string[] pages)
        {
            throw new NotImplementedException();
        }

        public IB_Image[] GetImages()
        {
            throw new NotImplementedException();
        }
    }
}
