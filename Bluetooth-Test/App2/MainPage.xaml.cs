using Plugin.BLE;
using Plugin.BLE.Abstractions.Contracts;
using Plugin.BLE.Abstractions.EventArgs;
using System;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Maui.Controls;

namespace App2
{
    public partial class MainPage : ContentPage
    {
        private IAdapter _adapter;
        private IDevice _device;
        private IService _service;
        private ICharacteristic _characteristic;

        public MainPage()
        {
            InitializeComponent();
            InitBLE();
        }

        private async void InitBLE()
        {
            var ble = CrossBluetoothLE.Current;
            _adapter = CrossBluetoothLE.Current.Adapter;

            _adapter.DeviceDiscovered += DeviceDiscovered;
            await _adapter.StartScanningForDevicesAsync();
        }

        private void DeviceDiscovered(object sender, DeviceEventArgs e)
        {
            if (e.Device.Name == "ESP32_LED_Control")
            {
                _device = e.Device;
                _adapter.StopScanningForDevicesAsync();
                ConnectToDevice();
            }
        }

        private async void ConnectToDevice()
        {
            try
            {
                Console.WriteLine("Connecting to device...");
                await _adapter.ConnectToDeviceAsync(_device);

                Console.WriteLine("Device connected. Discovering services...");
                var services = await _device.GetServicesAsync();
                _service = services.FirstOrDefault(s => s.Id == Guid.Parse("0000ffb0-0000-1000-8000-00805f9b34fb"));

                if (_service != null)
                {
                    Console.WriteLine("Service found. Discovering characteristics...");
                    var characteristics = await _service.GetCharacteristicsAsync();
                    _characteristic = characteristics.FirstOrDefault(c => c.Id == Guid.Parse("0000ffb1-0000-1000-8000-00805f9b34fb"));

                    if (_characteristic == null)
                    {
                        Console.WriteLine("Characteristic not found.");
                    }
                }
                else
                {
                    Console.WriteLine("Service not found.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }

        private async void OnSendOnClicked(object sender, EventArgs e)
        {
            if (_characteristic != null)
            {
                try
                {
                    await _characteristic.WriteAsync(Encoding.UTF8.GetBytes("ON"));
                    Console.WriteLine("Sent ON command.");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error sending ON command: {ex.Message}");
                }
            }
            else
            {
                Console.WriteLine("Characteristic is not available.");
            }
        }

        private async void OnSendOffClicked(object sender, EventArgs e)
        {
            if (_characteristic != null)
            {
                try
                {
                    await _characteristic.WriteAsync(Encoding.UTF8.GetBytes("OFF"));
                    Console.WriteLine("Sent OFF command.");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error sending OFF command: {ex.Message}");
                }
            }
            else
            {
                Console.WriteLine("Characteristic is not available.");
            }
        }
    }
}
