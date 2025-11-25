import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from scipy.signal import find_peaks

sample_rate = 100000
dt = 1 / sample_rate
# Programme start time
start_time = time.time()
relative_times = []
measurements = []
# Because there is no change, it is written outside the function
fft_frequencies = np.fft.rfftfreq(sample_num, 1 / sample_rate)
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
time.sleep(1)

fig, (ax_time, ax_freq) = plt.subplots(1, 2, figsize=(12, 5))

ax_time.set_title("Time Domain Signal")
ax_time.set_xlabel('Time (s)')
ax_time.set_ylabel('Voltage (V)')
ax_time.grid(True)
time_plot, = ax_time.plot([], [], 'g-')

# Frequency domain plot configuration
def setup_freq_axis(ax, fft_magnitude):
    ax.set_title("FFT Spectrum")
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')
    ax.set_xlim(0, 20000)
    if fft_magnitude is not None:
        # Dynamically setting the y-axis range in animations
        ax.set_ylim(0, np.max(fft_magnitude) * 1.2)
    else:
        ax.set_ylim(0, 1000)
    ax.grid(True)

setup_freq_axis(ax_freq, None)

def annotate_peaks(freqs, mags, ax):
    peaks, _ = find_peaks(mags, prominence=30)
    for peak_idx in peaks:
        peak_freq = freqs[peak_idx]
        peak_mag = mags[peak_idx]
        # Mark the text with straight lines
        ax.annotate(f'{peak_freq:.1f}Hz\n{peak_mag:.1f}',
                    xy=(peak_freq, peak_mag),
                    xytext=(peak_freq, peak_mag * 0.8),
                    arrowprops=dict(arrowstyle='-', facecolor='black', shrink=0.05))

def update_plot(i):
    global measurements, relative_times
    ser.flushInput()
    ser.write(bytes([4, 2]))
    data = ser.read(sample_num)
    values = np.frombuffer(data, dtype=np.uint8)
    voltages = (values / 255.0 * 5.0)
    voltages_ac = voltages - np.mean(voltages)

    # Time-domain plot update
    t_start = time.time() - start_time
    timestamps = np.arange(t_start, t_start + len(values) * dt, dt)
    relative_times.extend(timestamps)
    measurements.extend(voltages_ac)
    time_plot.set_data(relative_times, measurements)

    # Frequency domain plot update
    fft_result = np.fft.rfft(voltages_ac)
    fft_magnitude = np.abs(fft_result)
    # Annotate is a text object attached to the coordinate axis
    # Old curves and annotations must be cleared before redrawing
    ax_freq.clear()
    ax_freq.plot(fft_frequencies, fft_magnitude, 'r-')
    annotate_peaks(fft_frequencies, fft_magnitude, ax_freq)  # 标注多峰值
    # All settings for the axes must also be reset.
    setup_freq_axis(ax_freq, fft_magnitude)

    return time_plot

ani = animation.FuncAnimation(fig, update_plot, interval=500)
plt.show()
ser.close()
