using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
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
        private string _MultiDir;               // Only Needed in file Mode Multi
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
            LaunchCommandLineAppSingle(pathToPdf, pages, Rotation.NoRotation, Directory.GetParent(_executableRootPath).FullName + @"\PDF-Einlesen");
        }


        /// <summary>
        /// Reads a Pdf and copys it into the working Directory of the Conversion Software
        /// </summary>
        /// <param name="pages">Specify which pages should be converted</param>
        public IB_Reader(string Dir, string[] pages, Rotation rotation)
        {
            this._MultiDir = Dir;
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

            this._pathToPdfFolder = conf["ReadPdf"]["pdfRootPath"];

            logger.Log(conf["ReadPdf"]["pdfRootPath"], LogLevel.Debug);

            // Copy Pdf in the right Directories and add them to my working Dir
            try
            {
                foreach (string page in pages)
                {
                    File.Copy(page, Directory.GetParent(_executableRootPath).FullName + _pathToPdfFolder + "\\" + _MultiDir + "\\" + page.Split('\\').Last());
                    logger.Log("Succesfully Copied File \"" + page + "\"", LogLevel.Debug);
                }
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
            LaunchCommandLineAppMulti(_MultiDir, pages.Select(page => page.Split('\\').LastOrDefault()).ToArray(), Rotation.NoRotation, Directory.GetParent(_executableRootPath).FullName + @"\PDF-Einlesen");
        }


        /// <summary>
        /// Returns the images of the Canvas
        /// </summary>
        /// <returns></returns>
        /// <exception cref="NotImplementedException"></exception>
        public IB_Image[] GetImages()
        {
            throw new NotImplementedException();
        }


        /// <summary>
        /// Launch the Conversion Applikation in the File mode Single
        /// </summary>
        /// <param name="pathToPdf">Path to the Pdf File which should be converted</param>
        /// <param name="pages">what pages should be Converted. (Just the Pages youz need without header Pages etc.)</param>
        /// <param name="rotation">Specify how rotation should be handled</param>
        /// <param name="pathToExeDir">The Path to the Executable File</param>
        private void LaunchCommandLineAppSingle(string pathToPdf, int[] pages, Rotation rotation, string pathToExeDir)
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

            startInfo.Arguments = " --FileMode single --FilePath "
                + pathToPdf.Split('\\')[pathToPdf.Split('\\').Length - 1]
                + " --Rotation "
                + rotStr
                + " --UsedPages "
                + string.Join(" ", pages);

            this.logger.Log("Starting the Application with Arguments: " + " --FileMode single --FilePath "
                + pathToPdf.Split('\\')[pathToPdf.Split('\\').Length - 1]
                + " --Rotation "
                + rotStr
                + " --UsedPages "
                + string.Join(" ", pages),
                LogLevel.Debug);

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
                logger.Log(ex.Message, LogLevel.Error);
                throw;
            }

            logger.Log("Conversion Abgeschlossen!", LogLevel.Info);
        }


        /// <summary>
        /// Launch the Conversion Applikation in the File mode Multi
        /// </summary>
        /// <param name="dir">The Dir in Wich the Pdf Files are in</param>
        /// <param name="pathToFiles">The name of the pdf Files, automatically looks in the "dir" directory</param>
        /// <param name="rotation">Specify how rotation should be handled</param>
        /// <param name="pathToExeDir">The Path to the Executable File</param>
        private void LaunchCommandLineAppMulti(string dir, string[] pathToFiles, Rotation rotation, string pathToExeDir)
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

            string arguments = " --FileMode multi "
                + " --Rotation "
                + rotStr
                + " --UsedDir "
                + dir
                + " --UsedPdf";
            foreach (string path in pathToFiles)
            {
                arguments += (" " + path);
            }

            startInfo.Arguments = arguments;

            this.logger.Log(arguments ,LogLevel.Debug);

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
                logger.Log(ex.Message, LogLevel.Error);
                throw;
            }

            logger.Log("Conversion Abgeschlossen!", LogLevel.Info);
        }
    }
}