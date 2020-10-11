import numpy as np
import matplotlib.pyplot as plot
# Get x values of the sine wave
time = np.linspace(-2*np.pi, 2*np.pi, 256, endpoint=True)
# Amplitude of the sine wave is sine of a variable like time
amplitude_sin = np.sin(time)
amplitude_cos = np.cos(time)
# Plot a sine wave using time and amplitude obtained for the sine wave
plot.plot(time, amplitude_sin)
plot.plot(time, amplitude_cos)
# Give a title for the sine wave plot
plot.title('Sine & Cos wave')
# Give x axis label for the sine wave plot
plot.xlabel('Time')
# Give y axis label for the sine wave plot
plot.ylabel('Amplitude')
plot.grid(True, which='both')
plot.axhline(y=0, color='k')
plot.show()