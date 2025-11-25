import serial
import numpy as np
import time
import matplotlib.pyplot as plt
# According to the pre-programmed Arduino settings
N_SAMPLES = 1024

# Open the serial port
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
# Give the Arduino time to respond
time.sleep(1)
# Clear the serial port buffer
ser.flushInput()
time.sleep(1)
# Tell the Arduino to start sampling
# The first value is set to 4 for faster sampling
ser.write(bytes([4, 2]))
# The first value is set to 250 for beat
#ser.write(bytes([250, 2]))
time.sleep(1)
# Read data sample from Arduino ADC
data = ser.read(N_SAMPLES)
# Close the serial port
ser.close()
# convert data to an array of integers(0~255)
values = np.frombuffer(data, dtype=np.uint8)
# Convert to a 0-5V voltage
voltages = (values / 255.0 * 5.0)
# Subtract the DC offset to analyse the AC signal
voltages_ac = voltages- np.mean(voltages)

# Perform FFT analysis
# The sample rate of the Arduino after receiving bytes([4, 2])
FS = 100000.0
# This value is for beat
# FS = 2000

fft_raw = np.fft.rfft(voltages)
fft_amplitude = np.abs(fft_raw)
# Calculate frequency axis
fft_freqs = np.fft.rfftfreq(N_SAMPLES, 1.0/FS)

#Draw the time domain signal
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
t = np.arange(N_SAMPLES) / FS
plt.plot(t, voltages)
plt.title("Time Domain Signal")
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.grid(True)

#Draw the frequency domain signal
plt.subplot(1, 2, 2)
plt.plot(fft_freqs, fft_amplitude)
plt.title("FFT Spectrum")
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.xlim(0,15000)
plt.grid(True)

plt.tight_layout()
plot_filename = "fft_A.png"
plt.show()
plt.savefig(plot_filename)
