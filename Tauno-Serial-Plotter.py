#!/usr/bin/env python3
"""
    Tauno Erik
    Started:  07.03.2020
"""
# https://www.learnpyqt.com/courses/graphics-plotting/plotting-pyqtgraph/

#from concurrent import futures  # The futures module makes it possible to run operations in parallel using different executors.

import serial # pip3 install pyserial
import serial.tools.list_ports
import sys
import os
import re
#from pathlib import Path
#from time import time
#import types
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout,
                            QLabel, QSizePolicy, QWidget, QDesktopWidget,
                            QSlider, QSpacerItem)

import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from random import randint
from time import time
import types

# Config
# TODO: user can config plot time scale
# TODO diffrent plot types
# Scatter plot https://www.youtube.com/watch?v=H4QQwWnFiEk

plot_data_size = 100
left_side_width = 150

# GUI colors
colors =  {
            'oranz' :"#FF6F00",
            'sinakas' :"#4589b2",  # sinine
            'dark'    :"#263238",  # sinakas
            'hall'    :"#546E7A",
	        'black'   :"#212121"
}

# PLOT colors
# https://www.materialui.co/colors
plot_colors = [
    "#ba8310", # Kollane
    "#00BCD4", # syan
    "#3F51B5", # indigo
    "#E91E63", # pink
    "#FF9800", # orange
    "#9C27B0", # purple
    "#4CAF50", # green
    "#FFC107", # amber
    "#f44336", # red
    "#03A9F4", # light blue
    "#FFEB3B", # yellow
    "#CDDC39", # lime
    "#2196F3", # blue
    "#8BC34A", # light green
    "#009688"  # teal
    ]

# STYLING
fontsize = 16

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', colors['dark'])
pg.setConfigOption('foreground', colors['hall'])

QPushButton_style = f"""
QPushButton{{
	color: {colors['black']};
	background-color: {colors['hall']};
	border: 1px solid {colors['black']};
	padding: 5px;
    margin-top: 5px;
    font: {fontsize}px;
}}

QPushButton::hover{{
	background-color: {colors['sinakas']};
    color: {colors['black']};
}}

QPushButton::pressed{{
	border: 1px solid {colors['oranz']};
	background-color: {colors['hall']};
}}"""

QLabel_style = f"""
QLabel{{
    color: {colors['hall']};
    font: {fontsize}px;
    margin-top: 5px;
}}
"""

QComboBox_style = f"""
QComboBox:editable, QComboBox{{
    background-color: {colors['hall']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    padding: 5px;
    font: {fontsize}px;
}}

QComboBox::hover{{
	background-color: {colors['sinakas']};
    color: {colors['black']}; /* tekst*/
}}

QComboBox:editable:on, QComboBox:on {{ /* shift the text when the popup opens */
    padding-left: 10px;
    background-color: {colors['sinakas']};
    color: {colors['dark']};
}}

QComboBox::drop-down {{ /* shift the text when the popup opens */
    background-color: {colors['dark']}; /* noole tagune */
    color: {colors['sinakas']};
}}

QComboBox::down-arrow {{
    background-color: {colors['dark']};/* nool */
    image: url(./img/downarrow.png);
}}

"""
# https://stackoverflow.com/questions/40577104/how-to-plot-two-real-time-data-in-one-single-plot-in-pyqtgraph
# https://www.youtube.com/watch?v=IEEhzQoKtQU&t=800s
# PLOT
class Plot(pg.GraphicsWindow):

    def __init__(self, number_of_plots='1', parent=None):
        super(Plot,self).__init__(parent=None)

        self.number_of_plots = number_of_plots

        if self.number_of_plots is None:
            print("number_of_plots is None")
            pass

        print("Init Plot class. With {} plots".format(self.number_of_plots))

        # Create plot
        self.serialplot = self.addPlot()
        self.serialplot.setLabel('left', 'Data')
        self.serialplot.setLabel('bottom', 'Time')
        self.serialplot.showGrid(x=True, y=True)

        # Place to hold data
        self.x = [0]  # Time
        #self.y = [0]  
        # generate list of lists, incoming data
        self.ynew = [[0] for i in range(number_of_plots)] # Datas

        # List of all data lines
        self.data_lines = []
        
        for i in range(self.number_of_plots):
            pen = pg.mkPen(color=(plot_colors[i]))
            brush = pg.mkBrush(color=(plot_colors[i]))
            line = self.serialplot.plot(x=self.x, y=self.ynew[i], pen=pen, symbol='o', symbolBrush=brush, symbolSize=5)
            self.data_lines.append(line)

# END of class Plot ------------------------------------------------------


# Controls Design
class Controls(QWidget):

    def __init__(self, variable='', parent=None):
        super(Controls, self).__init__(parent=parent)

        self.verticalLayout = QVBoxLayout(self)
 
        self.control_width = left_side_width
        
        # DropDown: Select Port
        self.menu_1 = QVBoxLayout()
        # Grpup 1 starts
        self.menu_1.setAlignment(Qt.AlignTop)
        # Label
        self.device_label = QLabel(self)
        self.menu_1.addWidget(self.device_label)
        self.device_label.setText("Select port:")
        self.device_label.setStyleSheet(QLabel_style)
        # Select
        self.select_port = QtWidgets.QComboBox(parent=self)
        self.menu_1.addWidget(self.select_port)
        self.select_port.setStyleSheet(QComboBox_style)
        self.select_port.setFixedWidth(self.control_width)
        # Label
        self.baud_label = QLabel(self)
        self.menu_1.addWidget(self.baud_label)
        self.baud_label.setText("Baud rate:")
        self.baud_label.setStyleSheet(QLabel_style)
        # Select
        self.select_baud = QtWidgets.QComboBox(parent=self)
        self.menu_1.addWidget(self.select_baud)
        self.select_baud.setStyleSheet(QComboBox_style)
        self.select_baud.setFixedWidth(self.control_width)
        # Button
        self.connect = QtWidgets.QPushButton('Connect', parent=self)
        self.menu_1.addWidget(self.connect) # funk
        self.connect.setFixedWidth(self.control_width)
        self.connect.setStyleSheet(QPushButton_style)

        self.verticalLayout.addLayout(self.menu_1)
        # Grpup 1 ends

        # Button: About
        self.menu_3 = QVBoxLayout()
        self.menu_3.setAlignment(Qt.AlignBottom)
        self.about = QtWidgets.QPushButton('About', parent=self)
        self.menu_3.addWidget(self.about) # funk
        self.about.setFixedWidth(self.control_width)
        self.about.setStyleSheet(QPushButton_style)
        self.verticalLayout.addLayout(self.menu_3)

    # ?
    def resizeEvent(self, event):
        super(Controls, self).resizeEvent(event)

# END of class Controls ----------------------------------------


class MainWindow(QWidget):

    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        
        self.app = app
        self.plot_exist = False

        self.ports = [''] # list of avablie devices
        self.selected_port = self.ports[0] # '/dev/ttyACM0'
        self.baudrates = ['300','1200','2400','4800','9600','19200','38400','57600',
                        '74880','115200','230400','250000','500000','1000000','2000000']
        self.selected_baudrate = self.baudrates[4]

        self.number_of_lines = 0

        self.init_ui()
        self.center_mainwindow()
        self.init_timer()
        self.ser = serial.Serial()

        self.horizontalLayout = QHBoxLayout(self)

        # Controlls
        self.controls = Controls(parent=self)
        self.horizontalLayout.addWidget(self.controls)

        self.find_ports()       # Ports on dropdown menu
        self.init_baudrates()   # Baud Rates on dropdown menu

        #self.open_serial()
         
        # Controll selct and button calls
        self.controls.select_port.currentIndexChanged.connect(self.selected_port_changed)
        self.controls.select_baud.currentIndexChanged.connect(self.selected_baud_changed)
        self.controls.about.pressed.connect(self.about) 
        self.controls.connect.pressed.connect(self.connect)
    
    # Init functions

    def init_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        #self.timer.timeout.connect(self.read_serial_data)
        self.timer.start()

    def init_ui(self):
        self.setStyleSheet(f"MainWindow {{ background-color: {colors['dark']}; }}")
        self.setWindowTitle("Tauno Serial Plotter")
        self.setWindowIcon(QtGui.QIcon('./img/tauno-plotter.svg'))
        self.setMinimumSize(800,450)

    def center_mainwindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def find_ports(self):
        self.ports.clear() # clear the devices list
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            #print(port[0]) # /dev/ttyACM0
            #print(port[1]) # USB2.0-Serial
            #print(port[2]) # USB VID:PID=2341:0043 SER=9563430343235150C281 LOCATION=1-1.4.4:1.0
            self.ports.append(port[0]) # add devices to list
        self.controls.select_port.addItems(self.ports) # add devices to dropdown menu
        if len(ports) > 0:
            self.controls.select_port.setCurrentIndex(0)
            self.selected_port = self.ports[0]
        #self.controls.select_port.currentIndex

    def init_baudrates(self):
        self.controls.select_baud.addItems(self.baudrates)
        self.controls.select_baud.setCurrentIndex(4)
    # Controll fuctions

    def selected_port_changed(self, i):
        self.selected_port = self.ports[i]
        print("Main selected port changed:")
        print(self.selected_port)
        self.equal_x_and_y()
        self.open_serial()

    def selected_baud_changed(self, i):
        self.selected_baudrate = self.baudrates[i]
        print("Main selected baud index changed:")
        print(self.selected_baudrate)
        self.equal_x_and_y()
        self.open_serial()

    def equal_x_and_y(self):
        if self.plot_exist:
            print("\t eqaul_x_and_y !!!")
            # mitu y joont on?
            for i in range(self.number_of_lines):
                if len(self.plot.x) > len(self.plot.ynew[i]):
                    print("\t x on suurem kui y[{}]".format(i))
                    while len(self.plot.x) > len(self.plot.ynew[i]):
                        # Remove the first element on list
                        self.plot.x = self.plot.x[1:]
                if len(self.plot.ynew[i]) > len(self.plot.x):
                    print("\t y[{i}] on suurem kui x".format(i))
                    while len(self.plot.ynew[i]) > len(self.plot.x):
                        # Remove the first element on list
                        self.plot.ynew[i] = self.plot.ynew[i][1:]
            '''
            if len(self.plot.x) > len(self.plot.ynew[0]):
                print("\t x on suurem kui y")
                while len(self.plot.x) > len(self.plot.ynew[0]):
                    # Remove the first element on list
                    self.plot.x = self.plot.x[1:]
            elif len(self.plot.ynew[0]) > len(self.plot.x):
                s = len(self.plot.ynew[0]) - len(self.plot.x)
                print("\t y on suurem kui x: {}".format(s))
            else:
                print("\t x == y")
            '''
    
    # Button Connect
    def connect(self):
        print('Connect Button')
        # TODO peaks kontrolima uuesti mitu ploti on 
        if not self.plot_exist:
            self.number_of_lines = self.how_many_lines()
            if self.number_of_lines is not None:
                self.plot = Plot(self.number_of_lines) # TODO data punktide arv!!!!
                self.horizontalLayout.addWidget(self.plot)
                self.open_serial()
                self.plot_exist = True
                self.timer.timeout.connect(self.read_serial_data)
            else:
                print("connect: None!")
        else:
            self.equal_x_and_y()
            self.open_serial()

    # Button about
    def about(self):
        print('About Button')
        #self.plot.clear()
        #self.plot_exist = False
        #self.connect()

    # Function to extract all the numbers from the given string 
    def get_numbers(self, str): 
        # numbers = re.findall(r'[0-9]+', str) # only detsimal
        numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+', str) # https://www.regular-expressions.info/floatingpoint.html
        return numbers

    # y-axis
    def add_numbers(self, i, number, plot_data_size):
        # If list is full
        if len(self.plot.ynew[i]) > plot_data_size:
            # Remove the first element on list
            self.plot.ynew[i] = self.plot.ynew[i][1:]
        # Before adding newone
        self.plot.ynew[i].append(float(number))
    
    # x-axis
    def add_time(self, plot_data_size):
        # If list is full
        if len(self.plot.x) > plot_data_size:
            # Remove the first element on list
            self.plot.x = self.plot.x[1:]
        # Add a new value 1 higher than the last to end
        self.plot.x.append(self.plot.x[-1] + 1)  
                         
                        
    # Serial functions
    def open_serial(self):
        print("Open serial: {} {}".format(self.selected_port, self.selected_baudrate))
        if self.ser.is_open:
            self.ser.close()
        self.ser = serial.Serial(self.selected_port, int(self.selected_baudrate), timeout=0.09)
        print("Open serial: {} {}".format(self.ser.name, self.ser.baudrate))
       
    def read_serial_data(self):
        if self.ser.is_open:
            try:
                incoming_data = self.ser.readline()[:-2].decode('ascii') # [:-2] gets rid of the new-line chars
                if incoming_data:
                    print("Incoming data {}".format(incoming_data))
                    numbers = self.get_numbers(incoming_data)

                    # mitu data punkti tuleb sisse?
                    while len(numbers) > len(self.plot.ynew):
                        self.plot.ynew.append([0])
                
                    for i in range(len(numbers)):
                        self.add_numbers(i, numbers[i], plot_data_size)

                    self.add_time(plot_data_size) # x axis

                    for i in range(self.number_of_lines):
                        self.plot.data_lines[i].setData(self.plot.x, self.plot.ynew[i])
            except:
                print("Error read_serial_data!!!")
                self.equal_x_and_y()

    # How many data point gome in
    # eg. --454-45-454- == 3
    def how_many_lines(self):
        print("how_many_lines")
        self.open_serial()
        if self.ser.is_open:
            try:
                incoming_data = self.ser.readline()[:-2].decode('ascii') # [:-2] gets rid of the new-line chars
                i = 0
                while not incoming_data:
                    incoming_data = self.ser.readline()[:-2].decode('ascii')
                    i = i+1
                if incoming_data:
                    print("Incoming data {}".format(incoming_data))
                    numbers = self.get_numbers(incoming_data)
                    print("Leidsin {}".format(len(numbers)))
                    return len(numbers)
                #else:
                    #return 0
            except:
                print("Error")
                self.ser.close()
        #self.ser.close()

    # Tuleviku tarbeks
    def keyPressEvent(self, event):
        if event.key() == 32: # Space
            print("Space")
        elif event.key() == 16777219: # Backspace
            print("Backspace")
        else:
            print(f'Unknown keypress: {event.key()}, "{event.text()}"')

    #def mouseClickEvent(self, event):
        #print("clicked")

# END of class MainWindow --------------------------------------------

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow(app)
    w.show()
    sys.exit(app.exec_())
