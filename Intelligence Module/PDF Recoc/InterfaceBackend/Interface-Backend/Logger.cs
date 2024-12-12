using IniParser.Model;
using IniParser;
using System;
using System.IO;
using System.Text;
using System.Linq;

public class Logger
{
    private readonly string _logFilePath;
    private readonly long _maxFileSize = 5 * 1024 * 1024; // 5MB
    private readonly object _lock = new object();
    private string _rootPath;
    private IniData _conf;
    public Logger()
    {
        var parser = new FileIniDataParser();
        
        // Load´the right root path

#if DEBUG
        // Set the executable Path based on the curret mode of execution
        this._rootPath = Directory.GetParent(Environment.CurrentDirectory).Parent.Parent.Parent.FullName;
        Console.WriteLine("Debug " + _rootPath);

        // Read the conf file
        this._conf = parser.ReadFile(Directory.GetParent(_rootPath).FullName + "\\conf.ini");
#else
            // Set the executable Path based on the curret mode of execution
            this._rootPath = AppDomain.CurrentDomain.BaseDirectory;
            Console.WriteLine("EXE " + _rootPath);

            // Read the conf file
            this._conf = parser.ReadFile(AppDomain.CurrentDomain.BaseDirectory);
#endif
        this._logFilePath = Directory.GetParent(this._rootPath).FullName + this._conf["Interface"]["logFile"];
    }

    public void Log(string message, LogLevel level)
    {
        lock (_lock)
        {
            string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            string logMessage = $"{timestamp} [{level}] {message}";

            // Write log message to file
            File.AppendAllText(_logFilePath, logMessage + Environment.NewLine);

            // Write to Console
            Console.WriteLine(logMessage);

            // Check file size and trim if necessary
            CheckFileSize();
        }
    }

    private void CheckFileSize()
    {
        FileInfo fileInfo = new FileInfo(_logFilePath);

        if (fileInfo.Exists && fileInfo.Length > _maxFileSize)
        {
            TrimLogFile();
        }
    }

    private void TrimLogFile()
    {
        // Read all lines from the file
        string[] allLines = File.ReadAllLines(_logFilePath);

        // Calculate the number of lines to keep (keep latest entries)
        int linesToKeep = allLines.Length / 2; // Keep the latest half of the file

        // Write the latest lines back to the file
        File.WriteAllLines(_logFilePath, allLines.Skip(linesToKeep));
    }
}

public enum LogLevel
{
    Info,
    Warning,
    Error,
    Debug
}
