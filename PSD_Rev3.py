
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
from datacursor import DC
import scipy.io as io
plt.interactive(1)


class QMainWindow(QtWidgets.QMainWindow, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent1 = parent.parent       # Define Class Window as "Parent" instance for this Class
        sw = self.parent1
        self.sw = sw
        self.parent = parent               # Define Class For Window1 "Parent
        sw1 = self.parent
        self.sw1 = sw1
        

    def ensure_directory(self, dirname):
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        
                
    def Start_Plot_PSD(self):


        sw = self.sw
        sw1 = self.sw1
        print("I reached this point")
        sr = sw.sr
        j=0
        bw = sw1.doubleSpinBox1.value()
        npseg=round(sr/bw);
        self.npseg = npseg


# Define Spin & Combo Boxes

        dsb2Value = sw1.doubleSpinBox2.value()
        dsb3Value = sw1.doubleSpinBox3.value()
        hpfiltval = sw1.SpinBox4.value()
        lpfiltval = sw1.SpinBox5.value()
        bplowval = sw1.SpinBox6.value()

        bphighval = sw1.SpinBox7.value()
        bfval = sw1.SpinBox8.value()
        octval = sw1.SpinBox9.value()
              
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
 
        plt.title(f'Accel-Time ({"{:.2f}".format(sw.starttime)} - {"{:.2f}".format(sw.endtime)})sec, Channel/Axis = {sw.save_channel}')
        plt.plot(time_x,value_y)
        plt.grid(True,which='both',ls="-")
        plt.xlabel('Time (Sec)')
        plt.ylabel('Acceleration - (Gs)')
        self.ensure_directory('plot_test1')
        plt.savefig(f'./plot_test1/Accel-Time_{sw.save_channel}_{int(sw.starttime)}-{int(sw.endtime)}sec.png',orientation='landscape')    # Save figure
 


# PLot Final PSD  

        f1,psd1=pyyeti.psd.psdmod(value_y,sr,npseg,dsb2Value,dsb3Value)    # Compute PSD
        self.f1 = f1
        self.psd1 = psd1
        self.psd_grms()     # Compute GRMS
        
        if octn is True:
            print('inside loop')
            # If octave scale then rescale
            print('Inside rescale loop,  octn is True')
            p5hz,f5hz,ms5,ms6=psd.rescale(psd1,f1, n_oct=octval)    # Convert to 1/oct bandwidth
            n_oct = octval
            print('using 1/oct = ',  n_oct)
        if octn is False:
            print('octn is False')
            print("Using non-oct scale")

        if octn is True:
            plt.figure(f'PSD-Plot_Channel-{sw.save_channel}', figsize=(10,8))
            plt.clf()
            print('octn is True plotting using f5hz & p5hz')
            plt.loglog(f5hz,p5hz, color='green',lw=1.5, label=f'PSD, SR={sw.sr}, Grms={"{0:.2f}".format(self.grms)}, Scale={"1/{0:.0f}".format(octval)}oct')
            plt.xlim(20,2000)
            plt.legend(loc='best')
            plt.grid(True,which='both',ls="-")
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('PSD - ($G^2$/Hz)')
            plt.title(f'PSD - ({"{0:.2f}".format(sw.starttime)} - {"{:.2f}".format(sw.endtime)})sec,  Channel/Axis = {sw.save_channel}')
            plt.show()
        
        if octn is False:
            print('octn is False, plotting using f1 & psd1')
            plt.figure(f'PSD-Plot_Channel-{sw.save_channel}', figsize=(10,8))
            plt.clf()
            plt.loglog(f1,psd1, color='green',lw=1.5, label=f'PSD, SR={sw.sr}, Grms={"{0:.2f}".format(self.grms)}')
            plt.xlim(20,2000)
            plt.legend(loc='best')
            plt.grid(True,which='both',ls="-")
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('PSD - ($G^2$/Hz)')
            plt.title(f'PSD - ({"{0:.2f}".format(sw.starttime)} - {"{:.2f}".format(sw.endtime)})sec,  Channel/Axis = {sw.save_channel}')
            plt.show()
        plt.savefig(f'./plot_test/PSD_{sw.save_channel}_{int(sw.starttime)}-{int(sw.endtime)}sec.png',orientation='landscape')    # Save figure

    # Save select data to file
        if octn == True:
            savevars = [ 'Data1', 'sr', 'psd1', 'f1', 'p5hz', 'f5hz',
                         'time_x', 'value_y']
        else:
            savevars = [ 'Data1', 'sr', 'psd1', 'f1',
                         'time_x', 'value_y']    
        dct = locals()
        myvars = {key: dct[key] for key in savevars}
        self.ensure_directory('data_test1')
        PSD_save=io.savemat(f'./data_test1/PSD_{int(sw.starttime)}-{int(sw.endtime)}sec_sr_{round(sw.sr)}.mat', myvars)

# Define Grms function :
 
    def psd_grms(self):

        num = len(self.psd1)
        a=array(self.f1)
        b=array(self.psd1)
        nm1=num-1
        slope =zeros(nm1,'f')
        ra=0

        for i in range (0,nm1):
    
            s=log(b[i+1]/b[i])/log(a[i+1]/a[i])

            slope[i]=s
    
            if s < -1.0001 or s > -0.9999:
                ra += ( b[i+1] * a[i+1]- b[i]*a[i])/( s+1.)
            else:
                ra += b[i]*a[i]*log( a[i+1]/a[i])

        grms = sqrt(ra)
        self.grms = grms
 

