
"""
Created on Thu Dec 12 08:38:21 2013

@author: Sukhbinder Singh
         - Modified by Tim Widrick to:
           - add a menu
           - make the toolbar visible
         - Modified by Vince Grillo :
           - Add multiple GUI interfaces, Pushbuttons & Comboboxes
           - Add Universal interface
           - Add External Functions :  PSD, FDE-PSD, SRS

PyQt5 with menu and MatplotLib+Toolbar
Built on the example provided at
How to embed matplotib in pyqt - for Dummies
http://stackoverflow.com/questions/12459811/how-to-embed-matplotib-in-pyqt-for-dummies

"""
import sys, os, random, inspect
import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
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

# Define Main Window class for Toolbar Navigator
class Window(QtWidgets.QMainWindow, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        global stime,stgt,st,sr, stage, stages,  starttime, endtime, times, names, descs, units, filename, filetype, t0,t1, time_x, value_y 
        self.filetype = {}
        self.t0={}
        self.t1={}
        self.time_x = 0
        self.value_y = 0
        stages = {}
        self.sr = 4100
        self.days = 0
        self.hours =0
        self.minutes = 0
        self.seconds = 0
        self.lo_time = 0
        self.events = {}
        self.stages = stages
        self.statusbar = self.statusBar()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.define_menu()
        self.init_plot()
        self.pause_on = False
#        self.initial_params()
        self.flight_events()
        self.dialog = AccelTime_Window(self)   # Define dialog Window for Accel-Time options
        self.dialog1 = PsdPlot_Window(self)    #Define dialog Window for PSD options
        self.dialog2 = FdePsdPlot_Window(self)    #Define dialog Window for FdePSD options
        self.dialog3 = SRS_Window(self)     #Define dialog Window for SRS options
#        self.dialog4 = SplPlot_Window(self)    #Define dialog Window for SPL  options
#        self.dialog5 = VrsPlot_Window(self)    #Define dialog Window for VRS options
#        self.dialog6 = FFTMap_Window(self)     Define FFT Map for given data set
#        self.dialog7 = WaterFall_Window(self)   Define a waterfall plot per Time History



    def dcon(self, event):
        DC.on(callbacks=True, reset=False)
        self.pause_on = False
 
    def dcoff(self, event):
        DC.off(stop_blocking=False)
        self.pause_on = True
 
    def dcend(self, event):
        DC.off(stop_blocking=True)
        self.pause_on = False

    def on_pushButton_psd_clicked(self):
#        self.setupUi()
        self.dialog1.show()
        print("You are in the psd_plot routine")
        
    def plot_fde(self):
        # start FDE process
        self.dialog2.show()
        print('This is a FDE process')

    def plot_srs(self):
        # start SRS process
        print('This is a srs process')
        self.dialog3.show()

    def plot_spl(self):
        # start SPL process
        print('This is a spl process')

    def plot_vrs(self):
        # start SPL process
        print('This is a vrs process')       

    def define_menu(self):
        
        png = ('/usr/share/icons/gnome/22x22/actions/exit.png')
        exitAction = QtWidgets.QAction(QIcon(png), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        self.fileOpenAction = QtWidgets.QAction(QIcon(png), '&Open - F9Borg MultiFile Format', self)
        self.fileOpenAction.setShortcut('Ctrl+O')
        self.fileOpenAction.setStatusTip('Open Multi-File format FileName')
        self.fileOpenAction.triggered.connect(self.fileOpenF9Borg_Multi)

        self.fileOpenAction1 = QtWidgets.QAction(QIcon(png), '&Open - F9-Borg Matlab Format', self)
        self.fileOpenAction1.setShortcut('Ctrl+O')

        self.fileOpenAction1.setStatusTip('Open F9 Borg Matlab format FileName')
        self.fileOpenAction1.triggered.connect(self.fileOpenF9Borg_Matlab)
        
        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        menubar.addSeparator()
        fileOpenMulti = fileMenu.addAction(self.fileOpenAction)
        menubar.addSeparator()
        fileOpenF9Borg_Matlab = fileMenu.addAction(self.fileOpenAction1)
        menubar.addSeparator()
        fileMenu.addAction(exitAction)
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.help_menu.setStatusTip('Matplotlib Information')
        menubar.addSeparator()
        menubar.addMenu(self.help_menu)
        self.help_menu.addAction('&About Interface', self.about)
  
    def about(self):
        QtWidgets.QMessageBox.about(self, "Dynamics Flight Data Interface", """ Matplotlib interface for PSD, FdePSD,  SRS, SPL and VRS using Matplotlib Backends for NavigationToolbar 
and Canvas Window to display & interact with plot .  Select Dropdown
Menu for Falcon9 Matlab or Multi-File data.  Plot PSD, FdePSD, SRS, SPL or VRS
for particular data set""")

    def fileOpenF9Borg_Multi(self):

        if self.filetype == 'F9_matlab':    # File error handler, Test to see if names  arrays exist
            try: 
                names
            except NameError:
                print("self.names does not exist")
            else:
                del self.names
                del self.desc
                del self.units
                del self.times

        self.plotwidget.channelDescsComboBox.clear()           # Clear all items in combo box
        filename = QFileDialog.getOpenFileName(self)
        if filename and self.fileOpenAction:
            self.filename = filename[0]

            self.filetype = 'F9_multi'
            names,descs,units = multi.mlist(filename[0])
            self.names = names
            self.descs = descs
            self.units = units
            self.plotwidget.channelDescsComboBox.addItems([name for name in (self.names)])
            self.updateUi3()

    def fileOpenF9Borg_Matlab(self):
        
        if self.filetype == 'F9_matlab':    # File error handler, Test to see if names  arrays exist
            try: 
                names
            except NameError:
                print("self.names does not exist")
            else:
                del self.names
                del self.desc
                del self.units
                del self.times

        self.plotwidget.channelDescsComboBox.clear()                  # Clear all items in combo box    
        filename1 = QFileDialog.getOpenFileName(self)
        if filename1 and self.fileOpenAction1:

            self.filename1 = filename1[0]
            self.filetype = 'F9_matlab'

            self.f9_flt = io.loadmat(filename1[0], squeeze_me=True)
            f9_flt = self.f9_flt
            names = f9_flt.keys()
            self.times = [word for word in names if word.endswith('_t')]   
            self.names = [word for word in names if word.endswith('_v')]
            self.plotwidget.channelDescsComboBox.addItems([name for name in (self.names)])
            self.updateUi4()
       
 # Initialize Main Plot Window :           
    def init_plot(self):
 
        global stages,stime,stgt,st,stage, starttime, endtime, f 
        filetype={}
        self.flight_events()
        sr = int(self.sr)
        self.plotwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.plotwidget)
        self.statusBar().showMessage("Matplotlib interface using NavigationToolBar Backends.", 2000)
        plotwidget = self.plotwidget
        plotwidget.figure = Figure(figsize=(12, 8))
        plotwidget.canvas = FigureCanvas(plotwidget.figure)

        plotwidget.toolbar = NavigationToolbar(plotwidget.canvas, plotwidget)


        # Just some buttons
        plotwidget.button5 = QtWidgets.QPushButton('Plot-Accel-Time History')
        plotwidget.button5.clicked.connect(self.plot_AccelTime)

        plotwidget.button6 = QtWidgets.QPushButton('&Show Filename & Channel List')
        plotwidget.button6.clicked.connect(self.button_click)

        plotwidget.button7 = QtWidgets.QPushButton('&DC ON')
        plotwidget.button7.clicked.connect(self.dcon)

        plotwidget.button8 = QtWidgets.QPushButton('&DC OFF')
        plotwidget.button8.clicked.connect(self.dcoff)

        plotwidget.button9 = QtWidgets.QPushButton('&DC End')
        plotwidget.button9.clicked.connect(self.dcend)

        plotwidget.button10 = QtWidgets.QPushButton('&Plot PSD')
        plotwidget.button10.clicked.connect(self.on_pushButton_psd_clicked)
    
        
        plotwidget.button11 = QtWidgets.QPushButton('&Plot FDE-PSD')
        plotwidget.button11.clicked.connect(self.plot_fde)
        
        plotwidget.button12 = QtWidgets.QPushButton('&Plot SRS')
        plotwidget.button12.clicked.connect(self.plot_srs)
        
        plotwidget.button13 = QtWidgets.QPushButton('&Plot SPL')
        plotwidget.button13.clicked.connect(self.plot_spl)
        
        plotwidget.button14 = QtWidgets.QPushButton('&Plot VRS')
        plotwidget.button14.clicked.connect(self.plot_vrs)

        
        stageLabel = QLabel("Events :") 
        plotwidget.stageComboBox = QComboBox()
        plotwidget.stageComboBox.addItem("Ignition HoldDown")
        plotwidget.stageComboBox.addItems(["{}".format(self.stages[x][0]) for x in range(1,24)])
        stage = plotwidget.stageComboBox.currentIndex()

        stageStartTime = QLabel("Stage Start Time :")
        plotwidget.stageStartTimeSpinBox = QDoubleSpinBox()
        plotwidget.stageStartTimeSpinBox.setRange(-20,    10000)
        if self.filetype == 'F9_matlab':
            plotwidget.stageStartTimeSpinBox.setValue(self.stages[x][1] for x in range(1,24))
        plotwidget.stageStartTimeSpinBox.setSuffix(" sec")
        stageEndTime = QLabel("     Stage End Time :") 
        plotwidget.stageEndTimeSpinBox = QDoubleSpinBox()
        plotwidget.stageEndTimeSpinBox.setRange(-20,    10000)
        if self.filetype == 'F9_matlab':
            plotwidget.stageEndTimeSpinBox.setValue(self.stages[x][2]) 
        plotwidget.stageEndTimeSpinBox.setSuffix(" sec")
        stageTimeLabel1 = QLabel("       Stage Default Start Time :")
        plotwidget.stageTimeLabel1 = QLabel()
        stageTimeLabel2 = QLabel("Stage Default End Time :")
        plotwidget.stageTimeLabel2 = QLabel()     

        plotwidget.stageStartTimeSpinLabel = QLabel()
        plotwidget.stageEndTimeSpinLabel = QLabel()

       
        if self.fileOpenAction:
            plotwidget.channelDescs = QLabel("Channels :")
            plotwidget.channelDescsComboBox = QComboBox()

            channelDescsLabel = QLabel("      Channel Descript:")
            plotwidget.channelDescsLabel = QLabel()
            channelUnitsLabel = QLabel("            Units:")
            plotwidget.channelUnitsLabel = QLabel()

##      Define Sample rate & Liftoff Time  Labels          
        sampleRateLabel = QLabel("Sample Rate =")
        plotwidget.sampleRateLabel = QLabel()
        plotwidget.sampleRateSpinBox = QDoubleSpinBox()
        plotwidget.sampleRateSpinBox.setRange(int(0),    int(100000))
        plotwidget.sampleRateSpinBox.setValue(sr)
        self.sampleRateSpinBox = plotwidget.sampleRateSpinBox.value()

        liftoffTimeDaysLabel = QLabel("Liftoff Time (Days):")
        plotwidget.liftoffTimeDaysLabel = QLabel()        
        plotwidget.liftoffTimeDaysSpinBox = QDoubleSpinBox()
        plotwidget.liftoffTimeDaysSpinBox.setRange(0,    365)
        plotwidget.liftoffTimeDaysSpinBox.setValue(0) 

        liftoffTimeHoursLabel = QLabel("Liftoff Time (Hrs):")
        plotwidget.liftoffTimeHoursLabel = QLabel()  
        plotwidget.liftoffTimeHoursSpinBox = QDoubleSpinBox()
        plotwidget.liftoffTimeHoursSpinBox.setRange(0,    24)
        plotwidget.liftoffTimeHoursSpinBox.setValue(0)
      
        liftoffTimeMinutesLabel = QLabel("  Liftoff Time (Min):")
        plotwidget.liftoffTimeMinutesLabel = QLabel()
        plotwidget.liftoffTimeMinutesSpinBox = QDoubleSpinBox()
        plotwidget.liftoffTimeMinutesSpinBox.setRange(0,   60 )
        plotwidget.liftoffTimeMinutesSpinBox.setValue(0)

        liftoffTimeSecondsLabel = QLabel("  Liftoff Time (Sec):")
        plotwidget.liftoffTimeSecondsLabel = QLabel()
        plotwidget.liftoffTimeSecondsSpinBox = QDoubleSpinBox()
        plotwidget.liftoffTimeSecondsSpinBox.setRange(0,    60)
        plotwidget.liftoffTimeSecondsSpinBox.setValue(0)  

        TotalLiftoffTimeLabel = QLabel("   Total Liftoff Time (sec):  :")
        plotwidget.TotalLiftoffTimeLabel = QLabel()  
          
# set the layout
        layout1 = QtWidgets.QVBoxLayout()
        layout2 = QtWidgets.QHBoxLayout()
        layout3 = QtWidgets.QHBoxLayout()
        layout4 = QtWidgets.QHBoxLayout()
        layout5 = QtWidgets.QHBoxLayout()
        layout6 = QtWidgets.QHBoxLayout()
        layout7 = QtWidgets.QHBoxLayout()
        layout8 = QtWidgets.QHBoxLayout()
        layout9 = QtWidgets.QHBoxLayout()
        layout1.addWidget(plotwidget.toolbar)
        layout1.addWidget(plotwidget.canvas)
        layout1.addLayout(layout2)
 #       layout2.addWidget(plotwidget.button4)
        layout2.addWidget(plotwidget.button5)
        layout2.addWidget(plotwidget.button6)
        layout1.addLayout(layout3)
        layout3.addWidget(plotwidget.button7)      
        layout3.addWidget(plotwidget.button8)
        layout3.addWidget(plotwidget.button9)
        layout1.addLayout(layout7)
        layout7.addWidget(plotwidget.button10)
        layout7.addWidget(plotwidget.button11)
        layout7.addWidget(plotwidget.button12)        
        layout7.addWidget(plotwidget.button13)
        layout7.addWidget(plotwidget.button14)

#       Set Layout for Combo Boxes & Spin Boxes
        layout4.addWidget(stageLabel)
        layout4.addWidget(plotwidget.stageComboBox)
        layout1.addLayout(layout4)
        layout4.addWidget(stageTimeLabel1)
        layout4.addWidget(plotwidget.stageTimeLabel1)
        layout4.addWidget(stageTimeLabel2)
        layout4.addWidget(plotwidget.stageTimeLabel2)
        layout1.addLayout(layout5)
        layout5.addWidget(stageStartTime)
        layout5.addWidget(plotwidget.stageStartTimeSpinBox)
        layout5.addWidget(stageEndTime)
        layout5.addWidget(plotwidget.stageEndTimeSpinBox)
        layout1.addLayout(layout6)
        layout6.addWidget(plotwidget.channelDescs)
        layout6.addWidget(plotwidget.channelDescsComboBox)
        layout6.addWidget(channelDescsLabel)
        layout6.addWidget(plotwidget.channelDescsLabel)
        layout6.addWidget(channelUnitsLabel)
        layout6.addWidget(plotwidget.channelUnitsLabel)

#       Set Layout for Sample Rate & Liftoff Time 
        layout1.addLayout(layout8)
        layout8.addWidget(sampleRateLabel)
        layout8.addWidget(plotwidget.sampleRateLabel)
        layout8.addWidget(plotwidget.sampleRateSpinBox)

        layout8.addWidget(liftoffTimeDaysLabel)
        layout8.addWidget(plotwidget.liftoffTimeDaysLabel)
        layout8.addWidget(plotwidget.liftoffTimeDaysSpinBox)
 
        layout8.addWidget(liftoffTimeHoursLabel)
        layout8.addWidget(plotwidget.liftoffTimeHoursLabel)
        layout8.addWidget(plotwidget.liftoffTimeHoursSpinBox)
        
        layout8.addWidget(liftoffTimeMinutesLabel)
        layout8.addWidget(plotwidget.liftoffTimeMinutesLabel)
        layout8.addWidget(plotwidget.liftoffTimeMinutesSpinBox)

        layout8.addWidget(liftoffTimeSecondsLabel)
        layout8.addWidget(plotwidget.liftoffTimeSecondsLabel)
        layout8.addWidget(plotwidget.liftoffTimeSecondsSpinBox)

        layout8.addWidget(TotalLiftoffTimeLabel)
        layout8.addWidget(plotwidget.TotalLiftoffTimeLabel)

        self.updateUi5()
        plotwidget.setLayout(layout1)

        # Connect Signal & Slots to User interface
        plotwidget.stageComboBox.currentIndexChanged.connect(self.updateUi2)
        plotwidget.stageStartTimeSpinBox.valueChanged.connect(self.updateUi1)
        plotwidget.stageEndTimeSpinBox.valueChanged.connect(self.updateUi1)
        plotwidget.channelDescsComboBox.currentIndexChanged.connect(self.updateUi3)
        plotwidget.channelDescsComboBox.currentIndexChanged.connect(self.updateUi4)
        plotwidget.sampleRateSpinBox.valueChanged.connect(self.updateUi5)
        plotwidget.liftoffTimeDaysSpinBox.valueChanged.connect(self.updateUi5)
        plotwidget.liftoffTimeHoursSpinBox.valueChanged.connect(self.updateUi5)
        plotwidget.liftoffTimeMinutesSpinBox.valueChanged.connect(self.updateUi5)
        plotwidget.liftoffTimeSecondsSpinBox.valueChanged.connect(self.updateUi5)
   
        self.updateUi1()
        self.updateUi2()

    def updateUi1(self):
        """Spin Box  Function"""
        stage = self.plotwidget.stageComboBox.currentIndex()
        self.stage = stage
        stg1 = self.stages[stage][1]
        stg2 = self.stages[stage][2]
        if self.filetype == 'F9_matlab':
            self.starttime = self.stages[stage][1]
            self.endtime = self.stages[stage][2]
        if self.filetype == 'F9_multi':
            self.starttime = stg1
            self.endtime = stg2

        self.starttime = self.plotwidget.stageStartTimeSpinBox.value()
        self.endtime = self.plotwidget.stageEndTimeSpinBox.value()
        self.plotwidget.stageTimeLabel1.setText(" {0:.2f}".format(self.starttime))
        self.plotwidget.stageTimeLabel2.setText(" {0:.2f}".format(self.endtime))

    def updateUi2(self):
        """Combo Box Function"""
        stage = self.plotwidget.stageComboBox.currentIndex()
        self.stage = stage
        stg1 = self.stages[stage][1]
        stg2 = self.stages[stage][2]
        starttime = self.plotwidget.stageStartTimeSpinBox.value()
        endtime = self.plotwidget.stageEndTimeSpinBox.value()
        self.plotwidget.stageTimeLabel1.setText(" {0:.2f}".format(stg1))
        self.plotwidget.stageTimeLabel2.setText(" {0:.2f}".format(stg2))
        self.plotwidget.stageStartTimeSpinBox.setValue(stg1)
        self.plotwidget.stageEndTimeSpinBox.setValue(stg2)

  
    def updateUi3(self):
#        """ Multi-File list Function"""
        if self.filetype == 'F9_multi':
            channel_num = self.plotwidget.channelDescsComboBox.currentIndex()
            self.channel = self.names[channel_num]
            self.save_channel = self.channel
            descs1 = self.descs[channel_num]
            units1 = self.units[channel_num]
            self.plotwidget.channelDescsLabel.setText("{}".format(descs1))
            self.plotwidget.channelUnitsLabel.setText("{}".format(units1)) 


    def updateUi4(self):
        #        """ Matlab file type """
        if self.filetype == 'F9_matlab':
            channel = self.plotwidget.channelDescsComboBox.currentIndex()
            self.Data = [self.f9_flt[self.times[channel]], self.f9_flt[self.names[channel]]]
            self.save_channel = self.names[channel]

# Define Liftoff Times :  Days, Hrs, Mins, sec & Total Time
    def updateUi5(self):
        self.sr  = self.plotwidget.sampleRateSpinBox.value()
        self.sr = int(self.sr)
        self.plotwidget.sampleRateSpinBox.value()
        self.days = self.plotwidget.liftoffTimeDaysSpinBox.value()
        self.plotwidget.liftoffTimeDaysSpinBox.value()
        self.hours = self.plotwidget.liftoffTimeHoursSpinBox.value()
        self.plotwidget.liftoffTimeHoursSpinBox.value()
        self.minutes = self.plotwidget.liftoffTimeMinutesSpinBox.value()
        self.plotwidget.liftoffTimeMinutesSpinBox.value()
        self.seconds = self.plotwidget.liftoffTimeSecondsSpinBox.value()
        self.plotwidget.liftoffTimeSecondsSpinBox.value()
        lo_time=((self.days)*3600*24)+((self.hours*60+self.minutes)*60+self.seconds)    #  Launch time T0
        self.lo_time = lo_time
        self.plotwidget.TotalLiftoffTimeLabel.setText(" {0:.0f}".format(self.lo_time))  # Total liftoff time 

        
    def home(self):
        self.plotwidget.toolbar.home()

    def zoom(self):
        self.plotwidget.toolbar.zoom()

    def pan(self):
        self.plotwidget.toolbar.pan()

    def plot_AccelTime(self):
 
        if self.filetype == 'F9_multi':
           #  Add some stuff
            ''' plot some random stuff '''
            # Start the code for Time Array Pick Test :

            # Define Mission parameters
            sr=self.sr
            starttime = self.starttime
            endtime = self.endtime
            stage = self.stage

            # Define Mission parameters & Event Descriptions

            event_stage=self.stages[stage][0]
            self.event_stage = event_stage
            # Define Channel Number 
            time_slice = (f'({starttime}_{endtime})sec')
            self.time_slice = time_slice
            lo_time=((self.days)*3600*24)+((self.hours*60+self.minutes)*60+self.seconds)    #  Launch time T0
            self.lo_time = lo_time
            # Define Sets and Axes
            j=0

            print("Start of the Loop")
            print('\n')

            Data,Desc1,Units = multi.load(self.filename,self.channel,starttime,endtime,lo_time)   # Read multi-file
            self.Data = Data

            # Start the loop for one channel of  Stage data 
            for j in [0]:
                # Read data
                # Define selection range of Data
                print(self.t0, self.t1,  self.starttime,  self.endtime)
                self.plotwidget.figure.clf()
                ax = self.plotwidget.figure.add_subplot(111)
                ax.set_title(f'Accel-Time History, Channel/Axis = {self.channel}')
                ax.plot(self.Data[:,0],self.Data[:,1])
                self.plotwidget.canvas.draw()
                axcolor = 'lightgoldenrodyellow'
                time_x = 0
                value_y = 0
                self.time_x = Data[:,0]
                self.value_y = Data[:,1]

        if self.filetype == 'F9_matlab':
            ''' plot some random stuff '''
            # Start the code for Time Array Pick Test :

            # Define Mission parameters

            sr=self.sr
            starttime = self.starttime
            endtime = self.endtime
            stage = self.stage
            print(starttime,  endtime,  stage)

            # Define Event descriptions

            event_stage=self.stages[stage][0]
            self.event_stage = event_stage
            # Define Channel Number 
            time_slice = (f'({starttime}_{endtime})sec')
            self.time_slice = time_slice
            # Define Sets and Axes
            j=0

            print("Start of the Loop")
            print(starttime, endtime, self.stages[stage][0])
            print('\n')

            # Start the loop for one channel of  Stage data 
            for j in [0]:
                # Read data
                # Define selection range of Data
                self.t0 = self.Data[0][0]
                self.t1 = self.Data[0][-1]
                t0=self.t0
                t1=self.t1
                print(self.t0, self.t1,  self.starttime,  self.endtime)
                t0_range=int(abs(t0-self.starttime)*self.sr)
                t1_range=int(abs(t0-self.endtime)*self.sr)
                print(t0_range,  t1_range)
                Data1 = [self.Data[0][t0_range:t1_range], self.Data[1][t0_range:t1_range]]
                newdata = Data1
                self.plotwidget.figure.clf()
                ax = self.plotwidget.figure.add_subplot(111)
                ax.set_title(f'Accel-Time History, Channel/Axis = {self.save_channel}')
                ax.plot(newdata[0],newdata[1])
                self.plotwidget.canvas.draw()
                axcolor = 'lightgoldenrodyellow'
                time_x = 0
                value_y = 0
                self.time_x = newdata[0]
                self.value_y = newdata[1]
                time_x = self.time_x
                value_y = self.value_y


    def flight_events(self):
                 	     
        stages = { 
               0                                       :     ('Ignition HoldDown',  -3,	1.5), 
               1                                       :     ('Liftoff',	 1.5,	15),
               2                                       :     ('Transonic_MaxQ',  45,	125 ),    
               3     	                               :     ('MECO'    ,  	142,	147  ),
               4                                       :     ( 'Stage_Sep',	147.75,	149.75 ),  
               5                                       :     ( 'SES1',	        155,	160    ), 
               6                                       :     ('PLF_Jettison ',	188.25,	195.25 ),  
               7                                       :     ('MVac_Burn1SS',	195.25,	541.5  ), 
               8                                       :     ('SECO1'         ,	541.5,	546.5  ),  
               9                                       :     ('SES2'        ,	3149,	3150.5 ),
               10                                      :     ('MVac_Burn2SS ',	3150.5,	3152.5 ), 
               11                                      :     ('SECO2'         ,	3152.5,	3154   ),
               12                                      :     ( 'S/C sep ',	0,	0      ),
               13                                      :     ('Ascent_Stage1 ' ,    -3,	147    ),
               14                                      :     ( 'Ascent_MVac_Burn1' ,	155,	546.5 ),
               15                                      :     ('Ascent_MVac_Burn2 '   ,	3149,	3154),
               16                                      :     ('MVac_Plume (S1 impingement)'  , 155,  165 ),
               17                                      :     ( 'Boostback_Burn',	248,	284 ),
               18                                      :     ( 'Entry_Burn ',	382,	403    ),
               19                                      :     ('Reentry_Aero' ,	403,	460    ),
               20                                      :     ('Landing_Burn ',	460,	489.5),
               21                                      :     ('Pegasus Stage-1 Burn',  7.0,  77.0),
               22                                      :     ('Pegasus Stage-2 Burn', 95, 166),
               23                                      :     ('Pegasus Stage-3 Burn', 414, 481)}

        self.stages = stages
        events = [events for events in stages.keys()]
                    
                    
    def button_click(self):
        print(self.filename[0], self.names,  self.descs,  self.units)

        
    def exitCall(self):
        self.close()
        print('Exit app')
#        os.system('kill $(cat pid_save)')


class AccelTime_Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
       # start Accel-Time & PSD  plot  process
        self.parent1 = parent.parent      # Define Class Window as "Parent" instance for this Class
        self.parent = parent
        sw1 = self.parent1
        sw = self.parent
        self.sw = sw
        self.sw1 = sw1
     
        sr = sw.sr
        print('Accel_Time Window SR =', sr)
        
        #  Initialize options
        self.dels = "True"
        self.deld = "False"
        self.delot = "False"
        self.hpfilt = "True"
        self.lpfilt = "False"
        self.bpfilt = "False"
        self.detrendData = "True"
        self.ftime = "True"
        self.octn = "True"
        self.ftime = "True"

        self.winends = ['none', 'front', 'back', 'both']

        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.sizeConstraint = QLayout.SetDefaultConstraint

        self.l1 =  QLabel()
        self.l1.setText("FIXTIME() Options :")
        self.main_layout.addWidget(self.l1)
        self.checkBox10 = QCheckBox("Use Fixtime for Data Set")
        self.checkBox10.setChecked(True)
        self.checkBox10.stateChanged.connect(self.btnstate10)
        self.main_layout.addWidget(self.checkBox10)
        self.checkBox1 = QCheckBox("Del Spikes")
        self.checkBox1.stateChanged.connect(self.btnstate1)
        self.checkBox1.setChecked(True)
        self.main_layout.addWidget(self.checkBox1)
        self.checkBox2 = QCheckBox("Del Drops")
        self.checkBox2.stateChanged.connect(self.btnstate2)
        self.main_layout.addWidget(self.checkBox2)
        self.checkBox3 = QCheckBox("Del OutTimes")
        self.checkBox3.stateChanged.connect(self.btnstate3)
        self.main_layout.addWidget(self.checkBox3)

        self.l5 = QLabel()
        self.l5.setText("Filter Type Options :")
        self.main_layout.addWidget(self.l5)

        self.checkBox4 = QCheckBox("High Pass Filter ")
        self.main_layout.addWidget(self.checkBox4) 
        self.checkBox4.setChecked(True) 
        self.checkBox4.stateChanged.connect(self.btnstate4)
        self.SpinBox4 = QSpinBox(self.main_widget)
        self.SpinBox4.setRange(0, 10000)
        self.SpinBox4.setProperty("value", 5)
        self.SpinBox4.setSuffix(" Hz")       
        self.SpinBox4.setSingleStep(1)
        self.SpinBox4.valueChanged.connect(self.spinState4)        
        self.main_layout.addWidget(self.SpinBox4)

        self.checkBox5 = QCheckBox("Low Pass Filter ")
        self.main_layout.addWidget(self.checkBox5)  
        self.checkBox5.stateChanged.connect(self.btnstate5)
        self.SpinBox5 = QSpinBox(self.main_widget)
        self.SpinBox5.setRange(0, 10000)
        self.SpinBox5.setProperty("value", 2000)
        self.SpinBox5.setSuffix(" Hz")       
        self.SpinBox5.setSingleStep(1)
        self.SpinBox5.valueChanged.connect(self.spinState5)        
        self.main_layout.addWidget(self.SpinBox5)

        self.checkBox6 = QCheckBox("Band Pass Filter ")
        self.main_layout.addWidget(self.checkBox6)  
        self.checkBox6.stateChanged.connect(self.btnstate6)
        self.SpinBox6 = QSpinBox(self.main_widget)
        self.SpinBox6.setRange(0, 10000)
        self.SpinBox6.setProperty("value", 5)
        self.SpinBox6.setSuffix(" Hz")       
        self.SpinBox6.setSingleStep(1)
        self.SpinBox6.valueChanged.connect(self.spinState6)        
        self.main_layout.addWidget(self.SpinBox6)
        self.SpinBox7 = QSpinBox(self.main_widget)
        self.SpinBox7.setRange(0, 10000)
        self.SpinBox7.setProperty("value", 2000)
        self.SpinBox7.setSuffix(" Hz")       
        self.SpinBox7.setSingleStep(1)
        self.SpinBox7.valueChanged.connect(self.spinState7)        
        self.main_layout.addWidget(self.SpinBox7)

        self.l6 = QLabel()
        self.l6.setText("Butterworth Filter Order :")
        self.main_layout.addWidget(self.l6)
        self.SpinBox8 = QSpinBox(self.main_widget)
        self.SpinBox8.setProperty("value", 5)
        self.SpinBox8.setRange(1, 20)
        self.SpinBox8.setSuffix(" Order #")       
        self.SpinBox8.setSingleStep(1)
        self.SpinBox8.valueChanged.connect(self.spinState8)        
        self.main_layout.addWidget(self.SpinBox8)

        self.l7 = QLabel()
        self.l7.setText("Normalize Data about Horrizontal Axis     :")
        self.main_layout.addWidget(self.l7)
        self.checkBox7 = QCheckBox("Detrend Data ")
        self.checkBox7.setChecked(True)
        self.main_layout.addWidget(self.checkBox7)  
        self.checkBox7.stateChanged.connect(self.btnstate7)       
        self.main_layout.addWidget(self.checkBox7)

        self.l8 = QLabel()
        self.l8.setText("Display Data in 1/oct scale     :")
        self.main_layout.addWidget(self.l8)
        self.checkBox8 = QCheckBox("Rescale to Oct Scale ")
        self.checkBox8.setChecked(True)
        self.main_layout.addWidget(self.checkBox8)  
        self.checkBox8.stateChanged.connect(self.btnstate8)       
        self.main_layout.addWidget(self.checkBox8)

        self.SpinBox9 = QSpinBox(self.main_widget)
        self.SpinBox9.setMaximum(100)
        self.SpinBox9.setProperty("value", 24)
        self.SpinBox9.setRange(1, 100)
        self.SpinBox9.setSuffix(" Octave Number")       
        self.SpinBox9.setSingleStep(1)
        self.SpinBox9.valueChanged.connect(self.spinState9)  
        self.main_layout.addWidget(self.SpinBox9)

        self.winendsLabel = QLabel("WindowEnds Function")
        self.main_layout.addWidget(self.winendsLabel)
        self.windendsComboBox = QComboBox()
        self.windendsComboBox.addItem("none")
        self.windendsComboBox.addItems(["{}".format(self.winends[x]) for x in range(1,4)])
        self.windends = self.windendsComboBox.currentIndex()
        self.windendsComboBox.currentIndexChanged.connect(self.comboState10)
        self.main_layout.addWidget(self.windendsComboBox) 

        self.setCentralWidget(self.main_widget)
        self.dialog = QMainWindow(self)     # Define "parent=self" for handle in QMainWindow Class
        # End Main window definitions

# Define Spin & Combo Boxes

        hpfiltval = self.SpinBox4.value()
        self.hpfiltval = hpfiltval
        lpfiltval = self.SpinBox5.value()
        self.lpfiltval = lpfiltval
        bplowval = self.SpinBox6.value()
        self.bplowval = bplowval
        bphighval = self.SpinBox7.value()
        self.bphighval = bphighval
        bfval = self.SpinBox8.value()
        self.bfval = bfval
        octval = self.SpinBox9.value()
        self.octval = octval
        
              
# Define Check Boxes from Accel_Time Function:
        dels   = self.checkBox1.isChecked()
        self.dels = dels
        deld   = self.checkBox2.isChecked()
        self.deld = deld
        delot  = self.checkBox3.isChecked()
        self.delot = delot
        hpfilt = self.checkBox4.isChecked()
        self.hpfilt = hpfilt
        lpfilt = self.checkBox5.isChecked()
        self.lpfilt = lpfilt
        bpfilt =  self.checkBox6.isChecked()
        self.bpfilt = bpfilt        
        detrendData = self.checkBox7.isChecked()
        self.detrendData = detrendData
        octn = self.checkBox8.isChecked()
        self.octn = octn



    def accelcalcs(self):
   # Start Calculations, Accel-Time History
       # Define selection range of Data

        print('currenty in accelcalcs routine') 
        sw = self.sw

        Data1 = [sw.time_x, sw.value_y]
        time_x = sw.time_x
        value_y = sw.value_y
        sr = sw.sr
        x = Data1[1]

        # Define Spin, Combo & Check boxes locally
        hpfiltval = self.SpinBox4.value()
        lpfiltval = self.SpinBox5.value()
        bplowval = self.SpinBox6.value()
        bphighval = self.SpinBox7.value()
        bfval = self.SpinBox8.value()
        octval = self.SpinBox9.value()
        dels = self.checkBox1.isChecked()
        deld = self.checkBox2.isChecked()
        delot = self.checkBox3.isChecked()
        hpfilt = self.checkBox4.isChecked()
        lpfilt = self.checkBox5.isChecked()
        bpfilt = self.checkBox6.isChecked()
        detrendData = self.checkBox7.isChecked()
        octn = self.checkBox8.isChecked()
        ftime = self.checkBox10.isChecked()   
        bvalue = self.SpinBox8.value()     # Define value of Butterworth filter
        windends = self.windendsComboBox.currentText()

        print('Detrend value is:', detrendData)
        if detrendData is True:            # Check to Detrend Data
            value_y = signal.detrend(value_y, type='linear')
            self.value_y = value_y

        if detrendData is False:
            value_y = sw.value_y

        if ftime:                  # Check to apply Fixtime to Data
#            print('inside ftime loop, ftime = True')
            newdata = dsp.fixtime(Data1,sw.sr,delspikes=dels, deldrops=deld, delouttimes=delot)
            x = newdata[1]
            time_x = newdata[0]         
            value_y = x
            self.time_x = time_x
            self.value_y = value_y
            
        if not ftime:
#            print('value of ftime is', ftime)
#            print('inside ftime loop, ftime = False')
            Data1 = [time_x, value_y]
            time_x = time_x
            self.time_x = time_x
            self.value_y = value_y
            x = Data1[1] 

        if hpfilt:
            hphz = hpfiltval		# Define high pass filter 
            [c,d]=signal.butter(bvalue, [hphz/(sw.sr/2)], 'high')
            d2=signal.filtfilt(c,d,x);     # filter out ridgid body
            if detrendData: 
                d2 = signal.detrend(d2, type='linear')
            value_y = d2
            self.value_y = value_y
            print("Using a High Pass Filter",   hphz , "Hz")
            self.hpfilt = "False"

        if lpfilt:
            lphz = lpfiltval                                # Define low pass filter
            [c,d]=signal.butter(bvalue, [lphz/(sw.sr/2)], 'low')
            d2=signal.filtfilt(c,d,x);     # filter out ridgid body
            if detrendData is True: 
                d2 = signal.detrend(d2, type='linear')
            value_y = d2
            self.value_y = value_y
            print("Using a low pass filter",  lphz)
            self.lpfilt = "False"


        if bpfilt:
            bp1hz = bplowval          # Define band-pass filter low freq
            bp2hz = bphighval          # Define band-pass filter high freq 3000hz
            [c,d]=signal.butter(bvalue, [bp1hz/(sr/2),  bp2hz/(sr/2)], 'band')
            d2=signal.filtfilt(c,d,x);     # filter out ridgid body
            if detrendData is True: 
                d2 = signal.detrend(d2, type='linear')
            value_y = d2
            self.value_y = d2
            print("Using a band pass filter",   bp1hz,  bp2hz)
            self.bpfilt = "False"


        if windends:
            d2 = dsp.windowends(Data1[1], portion=0.01, ends=windends, axis=-1)
            value_y = d2
            self.value_y = d2
            print('using Window Ends function value :', self.windendsComboBox.currentText())

    
    def btnstate1(self,checkBox1):
        if self.checkBox1.isChecked() == True:
            print("Delete Spikes is selected")
            self.dels = "True"
        else:
            print("Delete Spikes is not selected")
            self.dels = "False"

    def btnstate2(self,checkBox2):
        if self.checkBox2.isChecked() == True:
            print("Delete drops is selected")
            self.deld = "True"
        else:
            print("Delete drops is not selected")
            self.deld = "False"


    def btnstate3(self,checkBox3):
        if self.checkBox3.isChecked() == True:
            print("Delete Outtimes is selected")
            self.delot = "True"
        else:
            print("Delete Outtimes is not selected")
            self.delot = "False"


    def btnstate4(self,checkBox4):
        if self.checkBox4.isChecked() == True:
            print("High Pass Filter is checked")
            self.hpfilt = "True"
        else:
            print("High Pass Filter is not selected")
            self.hpfilt = "False"


    def btnstate5(self,checkBox5):
        if self.checkBox5.isChecked() == True:
            print("Low Pass Filter is checked")
            self.lpfilt = "True"
        else:
            print("Low Pass Filter is not selected")
            self.lpfilt = "False"


    def btnstate6(self,checkBox6):
        if self.checkBox6.isChecked() == True:
            print("Band Pass Filter is checked")
            self.bpfilt = "True"
        else:
            print("Band Pass Filter is not selected")
            self.bpfilt = "False"

    def btnstate7(self,checkBox7):
        if self.checkBox7.isChecked() == True:
            print("Detrend Data is checked")
            self.detrendData = "True"
        else:
            print("Detrend Data is not selected")
            self.detrendData = "False"

    def btnstate8(self,checkBox8):
        if self.checkBox8.isChecked() == True:
            print("Display in Oct scale is checked")
            self.octn = "True"
        else:
            print("Display in Octave Scale is not selected")
            self.octn = "False"

    def btnstate10(self,checkBox10):
        if self.checkBox10.isChecked() == True:
            print("Fixtime is Selected")
            ftime = "True"
            self.ftime = ftime
        else:
            print("Fixtime is not selected")
            self.ftime = "False"

    def on_2ndpushButton_clicked(self):

        print("The 2nd Windown button was clicked")
        self.dialog.show()

    def spinState4(self):
        print("High Pass Filter Value")
        print(self.SpinBox4.value())
        self.hpfilt = "True"

    def spinState5(self):
        print("Low Pass Filter Value")
        print(self.SpinBox5.value())
        self.lpfilt = "True"

    def spinState6(self):
        print("Band Pass low  Filter Value")
        print(self.SpinBox6.value())
        self.bpfilt = "True"

    def spinState7(self):
        print("Band Pass high Filter Value")
        print(self.SpinBox7.value())
        self.bpfilt = "True" 

    def spinState8(self):
        print("Butterworth Filter Value")
        print(self.SpinBox8.value())

    def spinState9(self):
        print("1/oct Number")
        print(self.SpinBox9.value())

    def comboState10(self):
        print("Windows ends state selected :")
        print(self.windendsComboBox.value())


class PsdPlot_Window(AccelTime_Window):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sw1 = self.parent
        sw1 = self.sw1

       # start Accel-Time & PSD  plot  process
       #  Initialize options

        value_y = sw1.value_y
        time_x = sw1.time_x



        self.l5 = QLabel()
        self.l5.setText("              ")    # Add blank space
        self.main_layout.addWidget(self.l5)

        self.l1 = QLabel()
        self.l1.setText(" PSD Plot Parameters :         ")    # Code block title
        self.main_layout.addWidget(self.l1)

        self.pushButton = QtWidgets.QPushButton("Plot")
        self.main_layout.addWidget(self.pushButton) 
        self.pushButton.clicked.connect(self.on_Psd_PlotpushButton_clicked)
#        self.l1 =  QLabel()
        
        self.l2 = QLabel()
        self.l2.setText("npseg - Bandwidth(Hz)")
        self.main_layout.addWidget(self.l2)
        self.doubleSpinBox1 = QDoubleSpinBox(self.main_widget)
        self.doubleSpinBox1.setProperty("value", 5.0)
        self.doubleSpinBox1.setSuffix(" Hz")
        self.dsbval1 = self.doubleSpinBox1.value()
        self.doubleSpinBox1.valueChanged.connect(self.spinState1)
        self.main_layout.addWidget(self.doubleSpinBox1)

        self.l3 = QLabel()
        self.l3.setText("Timeslice")
        self.main_layout.addWidget(self.l3)
        self.doubleSpinBox2 = QDoubleSpinBox(self.main_widget)
        self.doubleSpinBox2.setProperty("value", 1.0)
        self.doubleSpinBox2.setRange(0, 10000)
        self.doubleSpinBox2.setSingleStep(0.01)
        self.doubleSpinBox2.valueChanged.connect(self.spinState2)
        self.main_layout.addWidget(self.doubleSpinBox2)
        
        self.l4 = QLabel()
        self.l4.setText("Timeslice Overlap")
        self.main_layout.addWidget(self.l4)
        self.doubleSpinBox3 = QDoubleSpinBox(self.main_widget)
        self.doubleSpinBox3.setProperty("value", 0.5)
        self.doubleSpinBox3.setSingleStep(0.01)
        self.doubleSpinBox3.valueChanged.connect(self.spinState3)        
        self.main_layout.addWidget(self.doubleSpinBox3)
       
        self.setCentralWidget(self.main_widget)

# Define Button State for  Spin Boxes and buttons in PSD - Plot
    def spinState1(self):
        print("The npseg value was changed")
        print(self.doubleSpinBox1.value())
        self.dsb1Value = self.doubleSpinBox1.value()

    def spinState2(self):
        print("The Timeslice value was changed")
        print(self.doubleSpinBox2.value())
        self.dsb2Value = self.doubleSpinBox2.value()

    def spinState3(self):
        print("The Timeslice Overlap value was changed")
        print(self.doubleSpinBox3.value())
        self.dsb3Value = self.doubleSpinBox3.value()

    def btnstate8(self,checkBox8):
        if self.checkBox8.isChecked() == True:
            print("Display in Oct scale is checked")
            self.octn = "True"
        else:
            print("Display in Octave Scale is not selected")
            self.octn = "False"

     
    def on_Psd_PlotpushButton_clicked(self):

        print("I reached this point")       
        print("Start the PSD Plot process")
        self.accelcalcs()          # Run accel-time calculations       
        from PSD_Rev3 import QMainWindow
        self.qmw = QMainWindow(self)
        self.qmw.Start_Plot_PSD()



class FdePsdPlot_Window(AccelTime_Window):

    def __init__(self, parent=None):
        super().__init__(parent)

       # start Accel-Time & PSD  plot  process
       #  Initialize options
        self.sw1 = self.parent
        sw1 = self.sw1

        value_y = sw1.value_y
        self.value_y = value_y
        time_x = sw1.time_x
        self.time_x = time_x
 
       
    # include more code ....

        self.setWindowTitle("Fatigue Damage Equivalent - PSD,  fdepsd")
        self.resp = ["absacce", "pvelo"]
        self.rolloff = ['lanczos', 'fft', 'prefilter', 'linear', 'none', 'None']
        self.parallel = ['auto', 'no', 'yes']
        self.verbose = ['False', 'True']
        

        self.main_sublayout1 = QHBoxLayout()
        self.main_sublayout2 = QHBoxLayout()
        self.main_sublayout3 = QHBoxLayout()
        self.main_sublayout4 = QHBoxLayout()

        self.l2 = QLabel()
        self.l2.setText("        ")    # Add blank space
        self.main_layout.addWidget(self.l2)
        self.l3 =  QLabel()
        self.l3.setText("Fatigue Damage Equivalent PSD - Options :")
        self.main_layout.addWidget(self.l3)
        self.l4 = QLabel()
        self.l4.setText("        ")    # Add blank space
        self.main_layout.addWidget(self.l4)

        
        self.pushButton = QtWidgets.QPushButton("Plot")
        self.main_layout.addWidget(self.pushButton) 
        self.pushButton.clicked.connect(self.on_FdePsd_PlotpushButton_clicked)
        self.l1 =  QLabel()
    
        self.l11 = QLabel()
        self.l11.setText("Set Fatigue Damage Equivalet Parameters   :")
        self.main_layout.addWidget(self.l11)
        self.l12 = QLabel()
        self.l12.setText("Build Log Scale Frequency Vector:"
        "  Low,       High ,        Count   ")
        self.main_layout.addWidget(self.l12)

        self.SpinBox13 = QSpinBox(self.main_widget)
        self.SpinBox13.setMaximum(1000)
        self.SpinBox13.setProperty("value", 20)
        self.SpinBox13.setRange(1, 1000)
        self.SpinBox13.setSuffix(" Freq - Low")       
        self.SpinBox13.setSingleStep(1)
        self.SpinBox13.valueChanged.connect(self.spinState13)
        self.main_sublayout1.addWidget(self.SpinBox13)
        
        self.SpinBox14 = QSpinBox(self.main_widget)
        self.SpinBox14.setMaximum(10000)
        self.SpinBox14.setProperty('value', 2000)
        self.SpinBox14.setRange(500, 10000)

        self.SpinBox14.setSuffix(" Freq - High")       
        self.SpinBox14.setSingleStep(1)
        self.SpinBox14.valueChanged.connect(self.spinState14)       
        self.main_sublayout1.addWidget(self.SpinBox14)
        
        self.SpinBox15 = QSpinBox(self.main_widget)
        self.SpinBox15.setMaximum(10000)
        self.SpinBox15.setProperty("value", 480)
        self.SpinBox15.setRange(1, 2000)
        self.SpinBox15.setSuffix(" Freq-count ")       
        self.SpinBox15.setSingleStep(1)
        self.SpinBox15.valueChanged.connect(self.spinState15) 
        self.main_sublayout1.addWidget(self.SpinBox15)      
        self.main_layout.addLayout(self.main_sublayout1)
        

        self.SpinBox16 = QSpinBox(self.main_widget)
        self.SpinBox16.setProperty("value", 10)
        self.SpinBox16.setRange(1, 2000)
        self.SpinBox16.setSuffix(" Q-Factor")       
        self.SpinBox16.setSingleStep(1)
        self.SpinBox16.valueChanged.connect(self.spinState16) 
        self.main_sublayout2.addWidget(self.SpinBox16)

        self.SpinBox17 = QSpinBox(self.main_widget)
        self.SpinBox17.setProperty("value", 15)
        self.SpinBox17.setRange(1, 2000)
        self.SpinBox17.setSuffix(" PPC-Pts-per-Cycle")       
        self.SpinBox17.setSingleStep(1)
        self.SpinBox17.valueChanged.connect(self.spinState17) 
        self.main_sublayout2.addWidget(self.SpinBox17)

        self.respLabel = QLabel("Resp. Anal.:")
        self.main_sublayout2.addWidget(self.respLabel)
        self.respComboBox = QComboBox()
        self.respComboBox.addItem("absacce")
        self.respComboBox.addItems(["{}".format(self.resp[x]) for x in range(1,2)])
        self.resp = self.respComboBox.currentIndex()
        self.respComboBox.currentIndexChanged.connect(self.comboState1)
        self.main_sublayout2.addWidget(self.respComboBox)
        self.main_layout.addLayout(self.main_sublayout2)  


        self.SpinBox18 = QSpinBox(self.main_widget)
        self.SpinBox18.setMaximum(1000)
        self.SpinBox18.setProperty("value", 300)
        self.SpinBox18.setRange(1, 2000)
        self.SpinBox18.setSuffix(" nbins")       
        self.SpinBox18.setSingleStep(1)
        self.SpinBox18.valueChanged.connect(self.spinState18) 
        self.main_sublayout3.addWidget(self.SpinBox18)
        
        self.SpinBox19 = QSpinBox(self.main_widget)
        self.SpinBox19.setMaximum(10000)
        self.SpinBox19.setProperty("value", 60)
        self.SpinBox19.setRange(1, 10000)
        self.SpinBox19.setSuffix(" sec-T0")       
        self.SpinBox19.setSingleStep(1)
        self.SpinBox19.valueChanged.connect(self.spinState19) 
        self.main_sublayout3.addWidget(self.SpinBox19)
    
        self.rolloffLabel = QLabel("Rolloff")
        self.main_sublayout3.addWidget(self.rolloffLabel)
        self.rolloffComboBox = QComboBox()
        self.rolloffComboBox.addItem("lanczos")
        self.rolloffComboBox.addItems(["{}".format(self.rolloff[x]) for x in range(1,6)])
        self.rolloff = self.rolloffComboBox.currentIndex()
        self.rolloffComboBox.currentIndexChanged.connect(self.comboState2)
        self.main_sublayout3.addWidget(self.rolloffComboBox) 
        self.main_layout.addLayout(self.main_sublayout3)

        self.parallelLabel = QLabel("Parallel :")
        self.main_sublayout4.addWidget(self.parallelLabel)
        self.parallelComboBox = QComboBox()
        self.parallelComboBox.addItem("auto")
        self.parallelComboBox.addItems(["{}".format(self.parallel[x]) for x in range(1,3)])
        self.parallel = self.parallelComboBox.currentIndex()
        self.parallelComboBox.currentIndexChanged.connect(self.comboState3)
        self.main_sublayout4.addWidget(self.parallelComboBox) 

        self.SpinBox20 = QSpinBox(self.main_widget)
        self.SpinBox20.setProperty("value", 12)
        self.SpinBox20.setRange(1, 2000)
        self.SpinBox20.setSuffix(" Max-Cpu ")       
        self.SpinBox20.setSingleStep(1)
        self.SpinBox20.valueChanged.connect(self.spinState20) 
        self.main_sublayout4.addWidget(self.SpinBox20)

        self.verboseLabel = QLabel("Verbose :")
        self.main_sublayout4.addWidget(self.verboseLabel) 
        self.verboseComboBox = QComboBox()
        self.verboseComboBox.addItem("False")
        self.verboseComboBox.addItems(["{}".format(self.verbose[x]) for x in range(1,2)])
        self.verbose = self.verboseComboBox.currentIndex()
        self.verboseComboBox.currentIndexChanged.connect(self.comboState4)
        self.main_sublayout4.addWidget(self.verboseComboBox) 
        self.main_layout.addLayout(self.main_sublayout4)

  
    def spinState9(self):
        print("1/oct Number")
        print(self.SpinBox9.value())
     
    def spinState13(self):
        print("Low Freq")
        print(self.SpinBox13.value())
        self.flow = self.SpinBox13.value()

    def spinState14(self):
        print("High Frequency")
        print(self.SpinBox14.value())
        self.fhigh = self.SpinBox14.value()

    def spinState15(self):
        print("Freq Steps")
        print(self.SpinBox15.value())
        self.fsteps = self.SpinBox15.value()

    def spinState16(self):
        print("Q - Factor")
        print(self.SpinBox16.value())
        self.qfact = self.SpinBox16.value()

    def spinState17(self):
        print("PPC")
        print(self.SpinBox17.value())
        self.nppc = self.SpinBox17.value()

    def spinState18(self):
        print("N-Bins")
        print(self.SpinBox18.value())
        self.nbinsnum = self.SpinBox18.value()

    def spinState19(self):
        print(" T0 ")
        print(self.SpinBox19.value())
        self.t0n = self.SpinBox19.value()

    def spinState20(self):
        print("Max Cpu Number")
        print(self.SpinBox20.value())
        self.mcpu = self.SpinBox20.value()


    def comboState1(self):
        print("Response analysis:",  self.respComboBox.currentText())
        self.resp_anal = self.respComboBox.currentText()


    def comboState2(self):
        print("Rolloff Pts", self.rolloffComboBox.currentText())
        self.rolloffn = self.rolloffComboBox.currentText()

    def comboState3(self):
        print("Parallel State:", self.parallelComboBox.currentText())
        self.parallel_state = self.parallelComboBox.currentText()

    def comboState4(self):
        print("Verbose Flag:", self.verboseComboBox.currentText())
        self.verbose_state = self.verboseComboBox.currentText()
           
        
    def on_FdePsd_PlotpushButton_clicked(self):
        print("I reached this point")       
        print("Start the PSD Plot process") 
        self.accelcalcs()          # Run accel-time calculations           
        from FdePSD_Rev3 import QMainWindow
        self.qmw = QMainWindow(self)
        self.qmw.Start_Plot_FdePSD()

class SRS_Window(AccelTime_Window):

    def __init__(self, parent=None):
        super().__init__(parent)
  
       # start Accel-Time & PSD  plot  process
       #  Initialize options
        self.sw1 = self.parent
        sw1 = self.sw1

        value_y = sw1.value_y
        self.value_y = value_y
        time_x = sw1.time_x
        self.time_x = time_x

        
    # include more code ....

        self.setWindowTitle("Shock Response Spectrum - SRS")
        self.resp = ["absacce", "pvelo"]
        self.rolloff = ['lanczos', 'fft', 'prefilter', 'linear', 'none', 'None']
        self.parallel = ['auto', 'no', 'yes']
        self.verbose = ['False', 'True']

        self.main_sublayout1 = QHBoxLayout()
        self.main_sublayout2 = QHBoxLayout()
        self.main_sublayout3 = QHBoxLayout()
        self.main_sublayout4 = QHBoxLayout()

        self.l5 = QLabel()
        self.l5.setText("              ")    # Add blank space
        self.main_layout.addWidget(self.l5)

        self.l2 = QLabel()
        self.l2.setText(" SRS Plot Parameters :         ")    # Code block title
        self.main_layout.addWidget(self.l2)

        self.l11 = QLabel()
        self.l11.setText("Set SRS & FFT variables   :")
        self.main_layout.addWidget(self.l11)
        
        self.pushButton = QtWidgets.QPushButton("Plot")
        self.main_layout.addWidget(self.pushButton) 
        self.pushButton.clicked.connect(self.on_SRS_PlotpushButton_clicked)
        self.l1 =  QLabel()
    
        self.l12 = QLabel()
        self.l12.setText("Build Log Scale Frequency Vector:"
        "  Low,       High ,        Count   ")
        self.main_layout.addWidget(self.l12)

        self.SpinBox13 = QSpinBox(self.main_widget)
        self.SpinBox13.setMaximum(100000)
        self.SpinBox13.setProperty("value", 100)
        self.SpinBox13.setRange(1, 1000)
        self.SpinBox13.setSuffix(" Freq - Low")       
        self.SpinBox13.setSingleStep(1)
        self.SpinBox13.valueChanged.connect(self.spinState13)
        self.main_sublayout1.addWidget(self.SpinBox13)
        
        self.SpinBox14 = QSpinBox(self.main_widget)
        self.SpinBox14.setMaximum(10000)
        self.SpinBox14.setProperty('value', 10000)
        self.SpinBox14.setRange(500, 10000)

        self.SpinBox14.setSuffix(" Freq - High")       
        self.SpinBox14.setSingleStep(1)
        self.SpinBox14.valueChanged.connect(self.spinState14)       
        self.main_sublayout1.addWidget(self.SpinBox14)
        
        self.SpinBox15 = QSpinBox(self.main_widget)
        self.SpinBox15.setMaximum(10000)
        self.SpinBox15.setProperty("value", 480)
        self.SpinBox15.setRange(1, 2000)
        self.SpinBox15.setSuffix(" Freq-count ")       
        self.SpinBox15.setSingleStep(1)
        self.SpinBox15.valueChanged.connect(self.spinState15) 
        self.main_sublayout1.addWidget(self.SpinBox15)      
        self.main_layout.addLayout(self.main_sublayout1)
        
# Next line
        self.SpinBox16 = QSpinBox(self.main_widget)
        self.SpinBox16.setProperty("value", 10)
        self.SpinBox16.setRange(1, 2000)
        self.SpinBox16.setSuffix(" Q-Factor")       
        self.SpinBox16.setSingleStep(1)
        self.SpinBox16.valueChanged.connect(self.spinState16) 
        self.main_sublayout2.addWidget(self.SpinBox16)

        self.SpinBox17 = QSpinBox(self.main_widget)
        self.SpinBox17.setProperty("value", 15)
        self.SpinBox17.setRange(1, 2000)
        self.SpinBox17.setSuffix(" PPC-Pts-per-Cycle")       
        self.SpinBox17.setSingleStep(1)
        self.SpinBox17.valueChanged.connect(self.spinState17) 
        self.main_sublayout2.addWidget(self.SpinBox17)
        self.main_layout.addLayout(self.main_sublayout2)   

 
        self.rolloffLabel = QLabel("Rolloff")
        self.main_sublayout3.addWidget(self.rolloffLabel)
        self.rolloffComboBox = QComboBox()
        self.rolloffComboBox.addItem("lanczos")
        self.rolloffComboBox.addItems(["{}".format(self.rolloff[x]) for x in range(1,6)])
        self.rolloff = self.rolloffComboBox.currentIndex()
        self.rolloffComboBox.currentIndexChanged.connect(self.comboState2)
        self.main_sublayout3.addWidget(self.rolloffComboBox) 
        self.main_layout.addLayout(self.main_sublayout3)

    
    def spinState13(self):
        print("Low Freq")
        print(self.SpinBox13.value())
        self.flow = self.SpinBox13.value()

    def spinState14(self):
        print("High Frequency")
        print(self.SpinBox14.value())
        self.fhigh = self.SpinBox14.value()

    def spinState15(self):
        print("Freq Steps")
        print(self.SpinBox15.value())
        self.fsteps = self.SpinBox15.value()

    def spinState16(self):
        print("Q - Factor")
        print(self.SpinBox16.value())
        self.qfact = self.SpinBox16.value()

    def spinState17(self):
        print("PPC")
        print(self.SpinBox17.value())
        self.nppc = self.SpinBox17.value()

    def comboState2(self):
        print("Rolloff Pts", self.rolloffComboBox.currentText())
        self.rolloffn = self.rolloffComboBox.currentText()

    def comboState1(self):
        print("Response analysis:",  self.respComboBox.currentText())
        self.resp_anal = self.respComboBox.currentText()

    def comboState4(self):
        print("Verbose Flag:", self.verboseComboBox.currentText())
        self.verbose_state = self.verboseComboBox.currentText()
           
        
    def on_SRS_PlotpushButton_clicked(self):
        print("I reached this point")       
        print("Start the PSD Plot process") 
        self.accelcalcs()          # Run accel-time calculations              
        from SRS_Rev3 import QMainWindow   # Load SRS module and Import main window
        self.qmw = QMainWindow(self)      # Set handle to QMainWindow Class
        self.qmw.Start_Plot_SRS()       # Start Method Start_Plot_SRS within QMainWindow 


        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.setWindowTitle('PyQt5 with menu and MatplotLib+Toolbar')
    main.show()
    sys.exit(app.exec_())

