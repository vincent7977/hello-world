
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
plt.interactive(1)


class QMainWindow(QtWidgets.QMainWindow, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent1 = parent.parent       # Define Class Window as "Parent" instance for this Class
        sw = self.parent1
        self.sw = sw
        self.parent = parent               # Define Class For PsdPlot_Window "Parent
        sw1 = self.parent
        self.sw1 = sw1
        

    def ensure_directory(self, dirname):
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        
                
    def Start_Plot_FdePSD(self):

        # initialize 
        sw = self.sw
        sw1 = self.sw1
        Grms = np.zeros(shape=(5))     # Initialize Grms array 
        self.Grms = Grms
        sr = sw.sr
        j=0


# Define Spin & Combo Boxes

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
    
#        x = Data1[1]


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


# PLot Fatigue Damage Equivalent PSD     

        # Define fdepsd parameters
        flow = sw1.SpinBox13.value()
        fhigh = sw1.SpinBox14.value()
        fsteps = sw1.SpinBox15.value()
        qfact = sw1.SpinBox16.value()
        nppc = sw1.SpinBox17.value()
        nbinsnum = sw1.SpinBox18.value()
        t0n = sw1.SpinBox19.value()
        mcpu = sw1.SpinBox20.value()
        resp_anal = sw1.respComboBox.currentText()
        rolloffn = sw1.rolloffComboBox.currentText()
        parallel_state = sw1.parallelComboBox.currentText()
        verbose_state = sw1.verboseComboBox.currentText()

        freq = np.logspace(np.log10(flow),np.log10(fhigh),fsteps)
        sig = value_y

        print('Value of value_y = ',  sig)
        fde50 = fdepsd.fdepsd(sig, sr, freq, qfact,hpfilter=None, resp=resp_anal, nbins=nbinsnum, 
                       T0=t0n, rolloff=rolloffn, ppc=nppc, parallel=parallel_state,
                       maxcpu=mcpu, verbose=verbose_state)            # Compute fde-PSD\
       
        self.fde30 = fde50.__dict__
        fde30 = self.fde30
        self.fde50 = fde50
        self.Gpsd=fde50.psd
        self.G1=fde50.psd[:,0]
        self.G2=fde50.psd[:,1]
        self.G4=fde50.psd[:,2]
        self.G8=fde50.psd[:,3]
        self.G12=fde50.psd[:,4]
        G1=self.G1
        G2=self.G2
        G4=self.G4
        G8=self.G8
        G12=self.G12
        Gpsd = self.Gpsd
        Gval = {'G1' : G1, 'G2' : G2, 'G4' : G4, 'G8' : G8, 'G12' : G12}
        Gname = ['G1', 'G2', 'G4', 'G8', 'G12']
  
        self.f1 = freq
        f1 = self.f1
        self.psdG1 = self.G1
        f5hz = 0
        p5hz = 0
        
        self.psd_grms()     # Compute GRMS
 
        # Define shape of re-scaled freq/psd
        print('The state of octn is:',  octn,  octval)
        if octn is True:          # If octave scale then rescale
            for j in [0,1,2,3,4]:
                p,f,ms5,ms6=psd.rescale(Gpsd[:,j], f1, n_oct=octval)   # Convert to 1/oct bandwidth
                if j == 0:
                    p5hz = np.zeros(shape=(len(p),5))    # if 1st pass thru loop, initialize arrays    
                    f5hz = np.zeros(shape=(len(f),5))
                f5hz[:,j] = f
                p5hz[:,j] = p
            print('lenght of f5hz, p5hz =',  len(f5hz), len(p5hz))

        if octn is False:
            print("Using non-oct scale")

        # Start Plotting FDE-PSDs  G1 - G12

        plt.figure(f'FDE-PSD-Plot_Channel-{sw.save_channel}', figsize=(10,8))
        plt.clf()
        if octn is True:
            for j in [0,1,2,3,4]:
                if j == 0:
                    plt.loglog(f5hz[:,j],p5hz[:,j], color = 'black', ls='solid', lw=1.5, label=f'PSD-{Gname[j]}, SR={sr}, Q={qfact}, Grms={"{0:.2f}".format(self.Grms[j])}, Scale={"1/{0:.0f}".format(octval)}oct')  # Print G1 at top level
                else:
                    if Gname[j] == 'G2':     # test for G2 and continue
                        continue
                    else:
                        plt.loglog(f5hz[:,j],p5hz[:,j], ls='dashed',  lw=1.5, label=f'PSD-{Gname[j]}, SR={sr}, Q={qfact}, Grms={"{0:.2f}".format(self.Grms[j])}, Scale={"1/{0:.0f}".format(octval)}oct')   # print G4 thru G12
                    
        if octn is False:
            print('octave number is', octn)
            for j in [0,1,2,3,4]:
                if j == 0:
                    plt.loglog(f1,Gpsd[:,j], color='black', ls='solid', lw=1.5, label=f'PSD-{Gname[j]}, SR={sr}, Q={qfact}, Grms={"{0:.2f}".format(self.Grms[j])}')    # Print G1 at top level
                else:
                    if Gname[j] == 'G2':    # test for G2 and continue
                        continue
                    else:
                        plt.loglog(f1,Gpsd[:,j], ls='dashed',  lw=1.5, label=f'PSD-{Gname[j]}, SR={sr}, Q={qfact}, Grms={"{0:.2f}".format(self.Grms[j])}')     # print G4 thru G12

        plt.xlim(20,2000)
        plt.legend(loc='best')
        plt.grid(True,which='both',ls="-")
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('PSD - ($G^2$/Hz)')
        plt.title(f'Fatigue Damage Equivalent-PSD - ({"{0:.2f}".format(int(sw.starttime))} - {"{0:.2f}".format(int(sw.endtime))})sec,  Channel/Axis = {sw.save_channel}')
        plt.show()
        plt.savefig(f'./plot_test1/FDE_PSD_{sw.save_channel}_{int(sw.starttime)}-{int(sw.endtime)}sec.png',orientation='landscape')    # Save figure

    # Save select data to file
        if sw1.octn is True:
            savevars = [ 'fde50', 'fde30', 'Gpsd', 'Gval', 'Gname', 'Grms',  'sr', 'freq', 'G1', 'G4', 'G8', 'G12', 'p5hz', 'f5hz',
                         'time_x', 'value_y']
        else:
            savevars = [ 'fde50', 'fde30', 'Gval', 'Gname', 'Gpsd', 'Grms', 'freq', 'sr', 'G1', 'G4', 'G8', 'G12',
                         'time_x', 'value_y']    
        dct = locals()
        myvars = {key: dct[key] for key in savevars}
        self.ensure_directory('data_test1')
#        os.system("if [ -d ./data_test1 ]; then echo 'data_test1 directory exists'; else echo 'Creating Directory data_test1';mkdir ./data_test1;fi")
        PSD_save=io.savemat(f'./data_test1/FDE_PSD_{int(sw.starttime)}-{int(sw.endtime)}sec_sr_{round(sw.sr)}.mat', myvars)

# Define Grms function :
 
    def psd_grms(self):
        
 
        for j in [0,1,2,3,4]:
            num = len(self.Gpsd[:,j])
            a=array(self.f1)
            b=array(self.Gpsd[:,j])
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
            self.Grms[j] = grms
 

 

