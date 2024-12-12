using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
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
        private Logger logger;

        public enum Rotation
        {
            NoRotation,
            RotationLeft,
            RotationRight
        }

        public enum FileMode
        {
            Single,
            Multi
        }

        /// <summary>
        /// Reads a Pdf and copys it into the working Directory of the Conversion Software
        /// </summary>
        /// <param name="pathToPdf">The full Path to the Pdf File wich should be copied as a string</param>
        /// <param name="pages">Specify which of th pages should be converted be adding aintger array</param>
        public IB_Reader(string pathToPdf, int[] pages, Rotation rotation)
        {
            var parser = new FileIniDataParser();

            logger = new Logger();

            // Load´the right root path

#if DEBUG
            // Set the executable Path based on the curret mode of execution
            this._executableRootPath = Directory.GetParent(Environment.CurrentDirectory).Parent.Parent.FullName;
            logger.Log(_executableRootPath, LogLevel.Debug);

            // Read the conf file
            IniData conf = parser.ReadFile(Directory.GetParent(_executableRootPath).FullName + "\\conf.ini");
#else
            // Set the executable Path based on the curret mode of execution
            this._executableRootPath = AppDomain.CurrentDomain.BaseDirectory;
            logger.Log(_executableRootPath, LogLevel.Debug);

            // Read the conf file
            IniData data = parser.ReadFile(AppDomain.CurrentDomain.BaseDirectory);
#endif

            this._pathToPdf = pathToPdf;

            this._pathToPdfFolder = conf["ReadPdf"]["pdfRootPath"];

            logger.Log(conf["ReadPdf"]["pdfRootPath"], LogLevel.Debug);

            // Copy Pdf in the right Directories and add them to my working Dir
            try
            {
                //Console.WriteLine("Return: " + Directory.GetParent(_executableRootPath).Parent.FullName);
                //Console.WriteLine("PathToPdf: " + _pathToPdf);
                //Console.WriteLine("Folder: " + Directory.GetParent(_executableRootPath).FullName + _pathToPdfFolder + "\\" + _pathToPdf.Split('\\').Last());
                File.Copy(_pathToPdf, Directory.GetParent(_executableRootPath).FullName + _pathToPdfFolder + "\\" + _pathToPdf.Split('\\').Last());
                logger.Log("Succesfully Copied File \"" + this._pathToPdf + "\"", LogLevel.Debug);
            }
            catch (UnauthorizedAccessException uaex)
            {
                logger.Log("You are not permitted to acces the specified Directory!", LogLevel.Error);
                logger.Log(uaex.Message, LogLevel.Error);
            }
            catch (IOException ex)
            {
                logger.Log("File already exists, overwriting it!", LogLevel.Warning);
            }
            catch (Exception ex)
            {
                logger.Log(ex.Message, LogLevel.Error);
            }

            logger.Log(Directory.GetParent(_executableRootPath).FullName + @"PDF-Einlesen", LogLevel.Debug);
            LaunchCommandLineApp(pathToPdf, pages, Rotation.NoRotation, Directory.GetParent(_executableRootPath).FullName + @"\PDF-Einlesen", FileMode.Single);
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

        /// <summary>
        /// Launch the Conversion Applikation
        /// </summary>
        void LaunchCommandLineApp(string pathToPdf, int[] pages, Rotation rotation, string pathToExeDir, FileMode fm)
        {
            string rotStr;
            switch (rotation)
            {
                case Rotation.RotationLeft:
                    rotStr = "rl";
                    break;
                case Rotation.RotationRight:
                    rotStr = "rr";
                    break;
                case Rotation.NoRotation:
                    rotStr = "nr";
                    break;
                default:
                    throw new NotImplementedException();
            }

            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.CreateNoWindow = false;
            startInfo.UseShellExecute = false;
            startInfo.FileName = pathToExeDir + "\\ReadPdf.exe";
            startInfo.WorkingDirectory = pathToExeDir;
            if (fm == FileMode.Single)
            {
                startInfo.Arguments = " --FileMode single --FilePath "
                    + pathToPdf.Split('\\')[pathToPdf.Split('\\').Length - 1]
                    + " --Rotation "
                    + rotStr
                    + " --UsedPages "
                    + string.Join(" ", pages);

                this.logger.Log("Starting Application with Arguments: " + " --FileMode single --FilePath "
                    + pathToPdf.Split('\\')[pathToPdf.Split('\\').Length - 1]
                    + " --Rotation "
                    + rotStr
                    + " --UsedPages "
                    + string.Join(" ", pages),
                    LogLevel.Debug);
            }


            startInfo.WindowStyle = ProcessWindowStyle.Hidden;


            // Start the Exe
            try
            {
                using (Process exeProcess = Process.Start(startInfo))
                {
                    exeProcess.WaitForExit();
                }
            }
            catch (Exception ex)
            {

                throw;
            }
        }
    }
}