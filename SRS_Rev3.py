
""" PSD Plotting routine called by Main Program  """


import sys, os, random, inspect
import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib
import numpy as np
from numpy import zeros,floor,array
from numpy import sqrt,pi,log
import scipy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import QtCore, QtGui
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PyQt5.QtCore import pyqtSignal, pyqtSignal
from types import SimpleNamespace
import numpy as np
import multi
import scipy.signal as signal
import pandas as pd
import matplotlib.pyplot as plt
import pyyeti
from pyyeti import psd
from pyyeti import dsp, srs
from pyyeti.pp import PP
from pyyeti import fdepsd
from datacursor import DC
import scipy.io as io
import scipy.integrate as Int
plt.interactive(1)


class QMainWindow(QtWidgets.QMainWindow, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent1 = parent.parent       # Define Class Window as "Parent" instance for this Class
        self.parent = parent               # Define Class For PsdPlot_Window "Parent
        self.sw = self.parent1
        self.sw1 = self.parent
        

    def ensure_directory(self, dirname):
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        
                
    def Start_Plot_SRS(self):

        sw = self.sw
        sw1 = self.sw1
        print("I reached this point")
        sr = sw.sr
        print(sr)
        starttime = sw.starttime
        endtime = sw.endtime

# Define Spin & Combo Boxes

        hpfiltval = sw1.SpinBox4.value()
        lpfiltval = sw1.SpinBox5.value()
        bplowval = sw1.SpinBox6.value()
        bphighval = sw1.SpinBox7.value()
        bfval = sw1.SpinBox8.value()
        octval = sw1.SpinBox9.value()        
        flow = sw1.SpinBox13.value()
        fhigh = sw1.SpinBox14.value()
        fsteps = sw1.SpinBox15.value()
        qfact = sw1.SpinBox16.value()
        nppc = sw1.SpinBox17.value()
        rolloffn = sw1.rolloffComboBox.currentText()

# Define Check Boxes from Accel_Time Function:
        dels   = sw1.checkBox1.isChecked()
        deld   = sw1.checkBox2.isChecked()
        delot  = sw1.checkBox3.isChecked()
        hpfilt = sw1.checkBox4.isChecked()
        lpfilt = sw1.checkBox5.isChecked()
        bpfilt =  sw1.checkBox6.isChecked()        
        detrendData = sw1.checkBox7.isChecked()
        octn = sw1.checkBox8.isChecked()
        ftime = sw1.checkBox10.isChecked()


# Start Calculations, Accel-Time History
        # Define selection range of Data - Define relative to main class 'Window'
        Data1 = [sw1.time_x, sw1.value_y]
        time_x = sw1.time_x
        value_y = sw1.value_y  
   
# PLot Final Accel-Time History        
        plt.figure(f'Final Accel-Time Histories, Channel/Axis = {sw.save_channel}')
        plt.clf()

        plt.title(f'Accel-Time ({"{0:.2f}".format(starttime)} - {"{0:.2f}".format(endtime)})sec, Channel/Axis = {sw.save_channel}')
        plt.plot(time_x,value_y)
        plt.grid(True,which='both',ls="-")
        plt.xlabel('Time (Sec)')
        plt.ylabel('Acceleration - (Gs)')
        self.ensure_directory('plot_test1')

        plt.savefig(f'./plot_test1/Accel-Time_{sw.save_channel}_{int(sw.starttime)}-{int(sw.endtime)}sec.png',orientation='landscape')    # Save figure

# Plot Detrended Velocity & Displacement and FFT 
        dt = 1/sr
        g = 9.80665
        conv = 0.00259
        start=np.log10(100)
        stop=np.log10(10000)
        N=800
        freq = np.logspace(start,stop,N )
        Q = 10
        cutoff = 10.0
        txt = (f'Computed Veloctiy, Displacement and FFT,  Plot_Channel/Axis = {sw.save_channel} \n ')
        
        velo = Int.cumtrapz(value_y/conv, dx=dt, axis=0, initial=0.0)
        disp = Int.cumtrapz(velo, dx=dt, axis=0, initial=0.0)

        plt.figure(f'Computed Veloctiy, Displacement and FFT - Plot_Channel/Axis-{sw.save_channel}, ({"{0:.2f}".format(starttime)} - {"{0:.2f}".format(endtime)})sec',  figsize=(12,8))
        plt.clf()

        plt.figtext(0.5, 0.99, txt, ha='center', va='top', size='large')
        plt.title(f'Computed Veloctiy, Displacement and FFT - ({"{0:.2f}".format(starttime)} - {"{0:.2f}".format(endtime)})sec,  Channel/Axis = {sw.save_channel}')

        if sw1.detrendData == "True":            # Check to Detrend Data
            plt.subplot(311)
            plt.title(f'Computed Velocity - Detrended')
            plt.plot(time_x, velo)
            plt.xlabel('Time (sec)')
            plt.ylabel('Velocity (in/sec)')

            plt.subplot(312)
            plt.plot(time_x, disp)
            plt.title(f'Computed Displacement - Detrended')
            plt.xlabel('Time (sec)')
            plt.ylabel('Displacement (in)')
        else:
            plt.subplot(311)
            plt.title(f'Computed Velocity')
            plt.plot(time_x, velo)
            plt.xlabel('Time (sec)')
            plt.ylabel('Velocity (in/sec)')

            plt.subplot(312)
            plt.plot(time_x, disp)
            plt.title(f'Computed Displacement')
            plt.xlabel('Time (sec)')
            plt.ylabel('Displacement (in)')
        
    # Calculate & plot fft data:
        mag, ph, frq = dsp.fftcoef(value_y, sr)
# Initialize FFT Figure:
        plt.subplot(313)
        plt.semilogx(frq, mag)
        plt.title(f'FFT Magnitude')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.grid(1, which='both')
        plt.show()

        plt.tight_layout(pad=3)

        plt.savefig(f'./plot_test1/FFT-SRS_{sw.save_channel}_{int(sw.starttime)}-{int(sw.endtime)}sec.png',orientation='landscape')    # Save figure
            
     
# PLot SRS     

# Define fdepsd parameters
        freq = np.logspace(np.log10(flow),np.log10(fhigh),fsteps)
        sig = value_y

# Calculate SRS and  plot data:
        sh = srs.srs(value_y, sr, freq, qfact, ppc=nppc, rolloff=rolloffn)
        shpos = srs.srs(value_y, sr, freq, qfact, peak='pos', ppc=nppc, rolloff=rolloffn)
        shneg = srs.srs(value_y, sr, freq, qfact, peak='neg', ppc=nppc, rolloff=rolloffn)

# Initialize SRS Figure :
        plt.figure(f'SRS - Plot_Channel-{sw.save_channel}', figsize=(10,8))
        plt.clf()
        plt.loglog(freq, sh, color = 'black', ls='solid', lw=1.5, 
                   label=f'SRS-absmax -, SR={sr}, Q={qfact}')
        plt.loglog(freq, shpos, color = 'red', ls='dashed', lw=1.5, label=f'SRS+ , SR={sr}, Q={qfact}')
        plt.loglog(freq, shneg, color = 'green',  ls='dashed', lw=1.5, label=f'SRS- , SR={sr}, Q={qfact}')
        plt.title(f'SRS - ({"{0:.2f}".format(starttime)} - {"{0:.2f}".format(endtime)})sec,  Channel/Axis = {sw.save_channel}')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Abs. Acceleration SRS (G)')
        plt.xlim([100, 10000])
        plt.legend(loc='best')
        plt.grid(1,which='both')
        plt.show()

        plt.savefig(f'./plot_test1/SRS_{sw.save_channel}_{int(sw.starttime)}-{int(sw.endtime)}sec.png',orientation='landscape')    # Save figure


    # Save select data to file
        savevars = [ 'sr', 'qfact', 'freq', 'sh', 'shpos', 'shneg', 'mag', 'ph', 'frq', 'velo', 'disp', 'time_x', 'value_y', 'starttime', 'endtime']

        dct = locals()
        myvars = {key: dct[key] for key in savevars}
        self.ensure_directory('data_test1')

        PSD_save=io.savemat(f'./data_test1/SRS-FFT_{int(sw.starttime)}-{int(sw.endtime)}sec_sr_{round(sw.sr)}.mat', myvars)



 

