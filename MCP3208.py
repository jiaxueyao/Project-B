import numpy as np
from DAH import MCP3208
import matplotlib.pyplot as plt
import time

#Define ADC as SPI chip 0 (CE0/GPIO8)
ADC0 = MCP3208( chip = 0 )

#Set the sample
num_samples = 1024
samples = []

#Record the starting time
start = time.time()
#Data sampling
for i in range(num_samples):
    adc_value = ADC0.analogReadVolt(0)
    samples.append(adc_value)
signal = np.array(samples)


#Record the ending time
end = time.time()
#Actual sample rate
total = end - start
f_sample = num_samples / total

#Perform an FFT analysis
fft_result  = np.fft.rfft(signal)
fft_magnitude = np.abs(fft_result)
freq_bins = np.fft.rfftfreq(num_samples, 1/f_sample)

#Draw the time domain signal
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
t = np.arange(num_samples) / f_sample
plt.plot(t, signal_ac_only)
plt.title('Sample Data')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.grid(True)

#Draw the frequency domain signal
plt.subplot(1,2,2)
plt.plot(freq_bins, fft_magnitude)
plt.title('FFT Frequency Spectrum')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid(True)

plt.tight_layout()
plt.savefig('spectrum_analysis.pdf')
plt.show()



