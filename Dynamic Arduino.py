import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
# Auto peak search
from scipy.signal import find_peaks

N_SAMPLES = 1024
SAMPLING_RATE = 100000
# This value is for beat
# SAMPLING_RATE = 2000

# X-axis: Frequency (Hz)
freqs = np.fft.rfftfreq(N_SAMPLES, d=1.0 / SAMPLING_RATE)

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
time.sleep(1)
ser.flushInput()
time.sleep(1)

fig = plt.figure(figsize=(16, 6))
# Left diagram: Time domain
ax1 = fig.add_subplot(1, 2, 1)
ax1.set_title("Time Domain Signal")
# Use sampling points as the X-axis
ax1.set_xlabel("Sample Point")
ax1.set_ylabel("Voltage (V)")
ax1.set_ylim(0, 5)
ax1.set_xlim(0, N_SAMPLES)
ax1.grid(True)
line1, = ax1.plot([], [], 'g-', lw=1)

# Right figure: Frequency domain
ax2 = fig.add_subplot(1, 2, 2)
ax2.set_title("FFT Spectrum (with Peaks)")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Amplitude")
ax2.set_xlim(0, 500)
ax2.set_ylim(0, 1500)
ax2.grid(True)
line2, = ax2.plot([], [], 'r-', lw=1)

# Text used to display the peak frequency
peak_text = ax2.text(0.75, 0.8, '', transform=ax2.transAxes, fontsize=10,
                     bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))

# Acquire new data, process it and update the plot
def updatePlot(i):
    ser.flushInput()
    ser.write(bytes([4, 2]))
    # The first value is set to 250 for beat
    # ser.write(bytes([250, 2]))
    data_bytes = ser.read(N_SAMPLES)
    values = np.frombuffer(data_bytes, dtype=np.uint8)
    voltages = (values / 255.0 * 5.0)
    voltages_ac = voltages - np.mean(voltages)

    fft_raw = np.fft.rfft(voltages_ac)
    fft_amplitude = np.abs(fft_raw)
    # Update drawing data
    line1.set_data(np.arange(N_SAMPLES), voltages)
    line2.set_data(freqs, fft_amplitude)

    # Dynamic adjustment of the Y-axis
    if len(fft_amplitude[:]) > 0:
        ax2.set_ylim(0, np.max(fft_amplitude[1:]) * 1.2)

    # Identify all peaks with a prominence exceeding 50
    peaks, _ = find_peaks(fft_amplitude, prominence=50)

    peak_info = "Peak:\n"
    for p in peaks:
        freq_val = freqs[p]
        peak_info += f"{freq_val:.0f} Hz\n"

    peak_text.set_text(peak_info)

# Animation Production
ani = animation.FuncAnimation(fig, updatePlot, interval=500, blit=False) # 每500ms更新一次
plt.show()
ser.close()
