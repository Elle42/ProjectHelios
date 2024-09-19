using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Maui.Controls;

namespace App_WLAN
{
    public partial class MainPage : ContentPage
    {
        private HttpClient _httpClient;
        private string esp32IpAddress = "http://10.13.254.170"; // IP-Adresse des ESP32

        public MainPage()
        {
            InitializeComponent();
            _httpClient = new HttpClient();
        }

        private async void OnSendOnClicked(object sender, EventArgs e)
        {
            try
            {
                var response = await _httpClient.GetAsync($"{esp32IpAddress}/LED=ON");
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Sent ON command.");
                }
                else
                {
                    Console.WriteLine($"Failed to send ON command: {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error sending ON command: {ex.Message}");
            }
        }

        private async void OnSendOffClicked(object sender, EventArgs e)
        {
            try
            {
                var response = await _httpClient.GetAsync($"{esp32IpAddress}/LED=OFF");
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Sent OFF command.");
                }
                else
                {
                    Console.WriteLine($"Failed to send OFF command: {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error sending OFF command: {ex.Message}");
            }
        }
    }
}
