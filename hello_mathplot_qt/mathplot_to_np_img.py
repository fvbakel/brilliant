print('mathplot')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import cv2

# Data for plotting
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)

fig, ax = plt.subplots()
canvas = FigureCanvasAgg(fig)
ax.plot(t, s)

ax.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='About as simple as it gets, folks')
ax.grid()

#fig.savefig("test.png")
#plt.show()
canvas.draw()
buf = canvas.buffer_rgba()
# convert to a NumPy array
img = np.asarray(buf)
tmp_file_name = './tmp' + '/' + 'plt-' + "001" + ".png"
cv2.imwrite(tmp_file_name,img)