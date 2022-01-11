#!/usr/bin/env python3
"""
    File:   Tauno-Serial-Plotter.py
    Author: Tauno Erik
    Started:07.03.2020
    Edited: 09.01.2022

    TODO:
    - Add labels

    Useful links:
    - https://www.learnpyqt.com/courses/graphics-plotting/plotting-pyqtgraph/
    - https://www.materialui.co/colors
    - https://stackoverflow.com/questions/40577104/how-to-plot-two-real-time-data-in-one-single-plot-in-pyqtgraph
    - https://www.youtube.com/watch?v=IEEhzQoKtQU&t=800s
    - https://github.com/pyqt/examples
    
    - https://phrase.com/blog/posts/translate-python-gnu-gettext/
    - https://phrase.com/blog/posts/beginners-guide-to-locale-in-python/
"""

import sys
import re
import os
import logging
import time
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRunnable, QThreadPool # Threads
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout,
                            QLabel, QWidget, QDesktopWidget, QMessageBox)
import pyqtgraph as pg

VERSION = '1.18'
TIMESCALESIZE = 450  # = self.plot_timescale and self.plot_data_size

stop_port_scan = False # To kill port scan thread when sys.exit

# Set debuge level
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.CRITICAL)

# Enable highdpi scaling:
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
# Use highdpi icons:
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# GUI Icons
icon_logo = os.path.join(os.path.dirname(__file__), 'icons/tauno-plotter.svg')
icon_minus = os.path.join(os.path.dirname(__file__), 'icons/minus.svg')
icon_plus = os.path.join(os.path.dirname(__file__), 'icons/plus.svg')
icon_arrow_down = os.path.join(os.path.dirname(__file__), 'icons/arrow_down.svg')

# GUI colours
colors =  {
    'oranz':"#FF6F00",
    'green':"#9CCC65",
    'dark' :"#263238",
    'hall' :"#B0BEC5",
	'black':"#212121"
}

# PLOT colors
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
FONTSIZE = 16

# Graph style
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
    font: {FONTSIZE}px;
}}

QPushButton::hover{{
	background-color: {colors['green']};
    color: {colors['black']};
}}

QPushButton::pressed{{
	border: 1px solid {colors['oranz']};
	background-color: {colors['hall']};
}}"""

QPushButton_disabled_style = f"""
QPushButton{{
	color: {colors['black']};
	background-color: {colors['dark']};
	border: 1px solid {colors['black']};
	padding: 5px;
    margin-top: 5px;
    font: {FONTSIZE}px;
}}
"""

QLabel_style = f"""
QLabel{{
    color: {colors['hall']};
    font: {FONTSIZE}px;
    margin-top: 5px;
}}
"""

QCheckBox_style = f"""
QCheckBox{{
    background-color: transparent;
    color: {colors['hall']};
    padding:5px;
}}
QCheckBox::indicator:unchecked{{
    background-color: {colors['hall']};
    padding:5px;
}}

QCheckBox::indicator:checked{{
    background-color: {colors['green']};
    padding:5px;
}}
"""

QCheckBox_disabled_style = f"""
QCheckBox{{
    background-color: transparent;
    color: {colors['black']};
    padding:5px;
}}
QCheckBox::indicator:unchecked{{
    background-color: {colors['dark']};
    padding:5px;
}}

QCheckBox::indicator:checked{{
    background-color: {colors['black']};
    padding:5px;
}}
"""

QComboBox_style = f"""
QComboBox:editable, QComboBox{{
    background-color: {colors['hall']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    padding: 5px 25p 5px 5px;
    font: {FONTSIZE}px;
}}

QComboBox::hover{{
	background-color: {colors['green']};
    color: {colors['black']}; /* tekst*/
}}

QComboBox:editable:on, QComboBox:on {{ /* shift the text when the popup opens */
    padding-left: 10px;
    background-color: {colors['green']};
    color: {colors['dark']};
}}

QComboBox::drop-down {{ /* shift the text when the popup opens */
    background-color: {colors['dark']}; /* noole tagune */
    color: {colors['green']};
    width: 24px;
}}

QComboBox::down-arrow {{
    background-color: {colors['dark']};/* nool */
    image: url({icon_arrow_down});
    width: 24px;
    height: 24px;
}}
"""

QComboBox_disabled_style = f"""
QComboBox:editable, QComboBox{{
    background-color: {colors['dark']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    padding: 5px 25p 5px 5px;
    font: {FONTSIZE}px;
}}

QComboBox::drop-down {{ /* shift the text when the popup opens */
    background-color: {colors['dark']}; /* noole tagune */
    color: {colors['green']};
    width: 24px;
}}

QComboBox::down-arrow {{
    background-color: {colors['dark']};/* nool */
    image: url({icon_arrow_down});
    width: 24px;
    height: 24px;
}}
"""


QDoubleSpinBox_style = f"""
QDoubleSpinBox{{
    background-color: {colors['hall']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    padding: 5px 25px 0px 25px; 
    font: {FONTSIZE}px;
}}

QDoubleSpinBox::hover{{
	background-color: {colors['green']};
    color: {colors['black']}; /* tekst*/
}}

QDoubleSpinBox::up-button{{
    /*subcontrol-origin: border;*/
    subcontrol-position: top right;
    background-color: {colors['dark']};
    width: 25px;
    /*border-width: 1px;*/
    height:27px;
    padding-bottom: 4px;
}}

QDoubleSpinBox::down-button{{
    /*subcontrol-origin: border;*/
    background-color: {colors['dark']};
    subcontrol-position: top left;
    width: 25px;
    /*border-width: 1px;*/
    height:27px;
    padding-bottom: 4px;
}}

QDoubleSpinBox::up-arrow {{
    image: url({icon_plus});
    width: 24px;
    height: 24px;
}}

QDoubleSpinBox::down-arrow {{
    image: url({icon_minus});
    width: 24px;
    height: 24px;
}}

"""

# 1. Subclass QRunnable
# https://realpython.com/python-pyqt-qthread/
# https://www.learnpyqt.com/tutorials/multithreading-pyqt-applications-qthreadpool/
class ForeverWorker(QRunnable):
    """
    It put function to run forever on background.
    I use it to scan the avaible serial ports.
    """
    def __init__(self, fn):
        super(ForeverWorker, self).__init__()
        self.fn = fn
        self.is_working = True

    def __del__(self):
        self.is_working = True
        #self.wait()

    def run(self):
        """ Forever running task """
        while self.is_working:
            logging.debug("ForeverWorker.Run while loop")
            self.fn()
            time.sleep(10) # seconds
            if stop_port_scan:
               self.is_working = False


# Deprecated: GraphicsWindow
# New: GraphicsLayoutWidget
class Plot(pg.GraphicsLayoutWidget):
    """ Plot definition """
    def __init__(self, nr_plot_lines='1'):
        super(Plot,self).__init__(parent=None)

        self.nr_plot_lines = nr_plot_lines

        if self.nr_plot_lines is None:
            logging.debug("nr_plot_lines is None!")

        logging.debug("Init Plot class. With %i plot lines.", self.nr_plot_lines)

        # Create plot
        self.serialplot = self.addPlot()
        self.serialplot.setLabel('left', 'Data')
        self.serialplot.setLabel('bottom', 'Time')
        self.serialplot.showGrid(x=True, y=True)

        # Place to hold data
        self.x_axis = [0]  # Time
        # generate list of lists, incoming data
        self.y_axis = [[0] for i in range(nr_plot_lines)] # Datas

        # List of all data lines
        self.data_lines = []

        for i in range(self.nr_plot_lines):
            if i >= len(plot_colors):
                # If we have more data than colors
                color_i = i - len(plot_colors)
            else:
                color_i = i

            pen = pg.mkPen(color=(plot_colors[color_i]))

            brush = pg.mkBrush(color=(plot_colors[color_i]))
            line = self.serialplot.plot(x=self.x_axis, y=self.y_axis[i], pen=pen,
                                symbol='o', symbolBrush=brush, symbolSize=3)
            self.data_lines.append(line)

# END of class Plot ------------------------------------------------------

class Controls(QWidget):
    """
    Define controls and menus design.
    """
    def __init__(self, parent=None):
        super(Controls, self).__init__(parent=parent)

        # Plot time scale == data visible area size
        self.plot_timescale = TIMESCALESIZE # default
        self.plot_timescale_min = 50
        self.plot_timescale_max = 1000

        self.vertical_layout = QVBoxLayout(self)

        # Menu width:
        self.control_width = 150

        # Top Menu
        self.menu_top = QVBoxLayout()
        self.menu_top.setAlignment(Qt.AlignTop)

        # Label Baud
        self.baud_label = QLabel(self)
        self.menu_top.addWidget(self.baud_label)
        self.baud_label.setText("Baud rate:")
        self.baud_label.setStyleSheet(QLabel_style)
        # Select Baud
        self.select_baud = QtWidgets.QComboBox(parent=self)
        self.menu_top.addWidget(self.select_baud)
        self.select_baud.setStyleSheet(QComboBox_style)
        self.select_baud.setFixedWidth(self.control_width)

        # Label Port
        self.device_label = QLabel(self)
        self.menu_top.addWidget(self.device_label)
        self.device_label.setText("Port:")
        self.device_label.setStyleSheet(QLabel_style)
        # Select Port
        self.select_port = QtWidgets.QComboBox(parent=self)
        self.menu_top.addWidget(self.select_port)
        self.select_port.setStyleSheet(QComboBox_style)
        self.select_port.setFixedWidth(self.control_width)

        # Button Connect
        self.connect = QtWidgets.QPushButton('Connect', parent=self)
        self.menu_top.addWidget(self.connect)
        self.connect.setFixedWidth(self.control_width)
        self.connect.setStyleSheet(QPushButton_style)

        self.vertical_layout.addLayout(self.menu_top)
        # Top menu ends


        # Bottom menu
        self.menu_bottom = QVBoxLayout()
        self.menu_bottom.setAlignment(Qt.AlignBottom)

        # Select Time scale size
        ## Time scale txt
        self.time_scale_txt = QLabel(self)
        self.menu_bottom.addWidget(self.time_scale_txt)
        self.time_scale_txt.setText("Visible time area:")
        self.time_scale_txt.setStyleSheet(QLabel_style)
        ## SpinBox
        self.time_scale_spin = QtWidgets.QDoubleSpinBox()
        self.time_scale_spin.setSingleStep(1)
        self.time_scale_spin.setDecimals(0)
        self.time_scale_spin.setMaximum(self.plot_timescale_max)
        self.time_scale_spin.setMinimum(self.plot_timescale_min)
        self.time_scale_spin.setValue(self.plot_timescale)
        self.menu_bottom.addWidget(self.time_scale_spin)
        self.time_scale_spin.setStyleSheet(QDoubleSpinBox_style)

        # Button: Clear data
        self.clear_data = QtWidgets.QPushButton('Clear data', parent=self)
        self.menu_bottom.addWidget(self.clear_data)
        self.clear_data.setFixedWidth(self.control_width)
        self.clear_data.setStyleSheet(QPushButton_disabled_style)
        self.clear_data.setEnabled(False)

        # Button: About
        self.about = QtWidgets.QPushButton('About', parent=self)
        self.menu_bottom.addWidget(self.about)
        self.about.setFixedWidth(self.control_width)
        self.about.setStyleSheet(QPushButton_style)

        self.vertical_layout.addLayout(self.menu_bottom)

    def update_timescale(self, new_value):
        """ Assign new value. """
        self.plot_timescale = new_value

    def resizeEvent(self, event):
        """ If we resize main window. """
        super(Controls, self).resizeEvent(event)

# END of class Controls ----------------------------------------


class MainWindow(QWidget):
    """
    Define MainWindow
    """
    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.app = app
        self.plot_exist = False
        self.is_fullscreen = False

        self.ports = [''] # list of avablie devices
        self.selected_port = self.ports[0] # '/dev/ttyACM0'
        self.baudrates = [
                          '150', # 0
                          '200', # 1
                          '300', # 2
                          '600', # 3
                         '1200', # 4
                         '1800', # 5
                         '2400', # 6
                         '4800', # 7
                         '9600', # 8
                        '19200',
                        '28800',
                        '38400',
                        '57600',
                        '74880',
                        '76800',
                       '115200',
                       '230400',
                       '250000',
                       '460800',
                       '500000',
                       '576000']
        self.default_baud_index = 8
        self.selected_baudrate = self.baudrates[self.default_baud_index] # default selected baud rate
        logging.debug("self.selected_baudrate =")
        logging.debug(self.selected_baudrate)

        self.max_tryes = 75 # how_many_lines()
        self.number_of_lines = 0
        self.error_counter = 0
        self.plot_data_size = TIMESCALESIZE #?
        self.is_button_connected = False

        self.init_ui()
        self.center_mainwindow()
        self.horizontal_layout = QHBoxLayout(self)

        self.init_timer()
        self.ser = serial.Serial()

        # Controlls
        self.controls = Controls(parent=self)
        self.horizontal_layout.addWidget(self.controls)

        self.init_baudrates()   # Baud Rates on dropdown menu

        # TODO: How to exit thread when mainwindow is closed??
        self.threadpool = QThreadPool()
        self.thread_find_ports()
        #self.find_ports() # while threads disabled!

        # Controll selct and button calls
        self.controls.select_port.currentIndexChanged.connect(self.selected_port_changed)
        self.controls.select_baud.currentIndexChanged.connect(self.selected_baud_changed)
        self.controls.time_scale_spin.valueChanged.connect(self.time_scale_changed)
        self.controls.connect.pressed.connect(self.connect_stop)
        self.controls.clear_data.pressed.connect(self.clear_data)
        self.controls.about.pressed.connect(self.about)

        # Init About window
        self.aboutbox = QMessageBox()



    def thread_find_ports(self):
        """ Runs on background forewer. """
        # Pass the function to execute
        worker = ForeverWorker(self.find_ports)
        # Execute
        self.threadpool.start(worker)

    def init_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.start()

    def init_ui(self):
        self.setStyleSheet(f"MainWindow {{ background-color: {colors['dark']}; }}")
        self.setWindowTitle("Tauno Serial Plotter")
        self.setWindowIcon(QtGui.QIcon(icon_logo))
        self.setMinimumSize(900,550)

    def center_mainwindow(self):
        """ Center window on startup. """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def find_ports(self):
        """
        Find avaible ports/devices and add to self.ports
        """
        logging.debug("self.plot_exist %s", self.plot_exist)
        logging.debug("self.is_button_connected %s", self.is_button_connected)

        before_selected_port = self.selected_port
        logging.debug("before_selected_port %s", before_selected_port)

        try:
            if not self.plot_exist or not self.is_button_connected:
            # Kui plot on olemas siis me ei skänni!
                self.ports.clear() # clear the devices list
                self.controls.select_port.clear() # clear dropdown menu

                logging.debug("self.ports: %s", len(self.ports))
                ports = list(serial.tools.list_ports.comports())
                logging.debug("find_ports: %s", len(ports))

                for port in ports:
                    #print(port[0]) # /dev/ttyACM0
                    #print(port[1]) # USB2.0-Serial
                    #print(port[2]) # USB VID:PID=2341:0043
                                    # SER=9563430343235150C281
                                    # LOCATION=1-1.4.4:1.0
                    self.ports.append(port[0]) # add devices to list

                # add devices to dropdown menu
                self.controls.select_port.addItems(self.ports)

                if len(ports) > 0:
                    # Et valitud port ei muutuks
                    if before_selected_port in self.ports:
                        index = self.ports.index(before_selected_port)
                    else:
                        index = 0
                    self.controls.select_port.setCurrentIndex(index)
                    self.selected_port = self.ports[index]
        except IOError:
            logging.error("find_ports IOError")

    def init_baudrates(self):
        self.controls.select_baud.addItems(self.baudrates)
        self.controls.select_baud.setCurrentIndex(self.default_baud_index)

    def selected_port_changed(self, i):
        self.selected_port = self.ports[i]
        logging.info("Main selected port changed:")
        logging.info(self.selected_port)
        #self.equal_x_and_y()
        #self.open_serial()

    def selected_baud_changed(self, i):
        self.selected_baudrate = self.baudrates[i]
        logging.info("Main selected baud index changed:")
        logging.info(self.selected_baudrate)
        self.equal_x_and_y()
        self.open_serial()

    def equal_x_and_y(self):
        if self.plot_exist:
            logging.debug("\t eqaul_x_and_y !!!")
            try:
                logging.debug("equal_x_and_y try")
                for i in range(self.number_of_lines):
                    if len(self.plot.x_axis) > len(self.plot.y_axis[i]):
                        logging.debug("\t x on suurem kui y[%s]", i)

                        while len(self.plot.x_axis) > len(self.plot.y_axis[i]):
                            # Remove the first element on list
                            self.plot.x_axis = self.plot.x_axis[1:]
                    if len(self.plot.y_axis[i]) > len(self.plot.x_axis):
                        logging.debug("\t y[%s] on suurem kui x_axis", i)

                        while len(self.plot.y_axis[i]) > len(self.plot.x_axis):
                            # Remove the first element on list
                            self.plot.y_axis[i] = self.plot.y_axis[i][1:]
            
            except Exception as ex:
                logging.debug(ex)
                self.error_counter += 1
                self.error_status()

            except SystemExit:  
                logging.debug(sys.exc_info())


    def time_scale_changed(self):
        logging.debug("Timescale changed!")
        new_value = int(self.controls.time_scale_spin.value())
        old_value = self.plot_data_size

        self.controls.update_timescale(new_value)
        #print("New Timescale value = {}".format(self.controls.plot_timescale))

        self.update_data_size(new_value)
        #print("New data size value = {}".format(self.plot_data_size))

        if new_value < old_value:
            if self.plot_exist:
                real_size = len(self.plot.x_axis)
                difference = real_size - new_value
                # shrink data size
                if difference > 1:
                    del self.plot.x_axis[0:difference]
                    for i in range(self.number_of_lines):
                        del self.plot.y_axis[i][0:difference]


    def update_data_size(self, new_value):
        self.plot_data_size = new_value

    def connect_stop(self):
        """ Connected or Pause button press? """
        if not self.is_button_connected:
            self.is_button_connected = True
            logging.debug('--> Connect Button.')
            self.connect()
            # Enable Clear Data button
            self.controls.clear_data.setEnabled(True)
            self.controls.clear_data.setStyleSheet(QPushButton_style)
        else:
            self.is_button_connected = False
            logging.debug('--> Pause Button.')
            self.disconnect()
            # Diable Clear Data button
            self.controls.clear_data.setEnabled(False)
            self.controls.clear_data.setStyleSheet(QPushButton_disabled_style)


    def connect(self):
        """ When we press button Connect. """
        # Change button txt
        self.controls.connect.setText('Pause')
        # Disable button
        self.controls.select_port.setEnabled(False)
        self.controls.select_baud.setEnabled(False)
        # Change button style
        self.controls.select_port.setStyleSheet(QComboBox_disabled_style)
        self.controls.select_baud.setStyleSheet(QComboBox_disabled_style)

        if not self.plot_exist:
            logging.debug("connect: create plot")
            self.number_of_lines = self.how_many_lines()

            if self.number_of_lines is not None:
                self.plot = Plot(self.number_of_lines)
                self.horizontal_layout.addWidget(self.plot)
                self.open_serial()
                self.plot_exist = True
                self.timer.timeout.connect(self.read_serial_data)
            else:
                logging.debug("connect: None!")
        else:
            #self.equal_x_and_y()
            self.open_serial()

    def disconnect(self):
        """ When we press Pause button """
        self.close_serial()
        #self.clear_data() # ??
        # Change button txt
        self.controls.connect.setText('Resume')
        # Enable buttons
        self.controls.select_port.setEnabled(True)
        self.controls.select_baud.setEnabled(True)
        # Change button style
        self.controls.select_port.setStyleSheet(QComboBox_style)
        self.controls.select_baud.setStyleSheet(QComboBox_style)

    def clear_data(self):
        """ Button clear data """
        logging.debug('--> Clear data Button.')
        # delete existing data
        size = len(self.plot.x_axis)
        logging.debug("x_axis: %s", size)
        del self.plot.x_axis[0:(size-1)]
        for i in range(self.number_of_lines):
            del self.plot.y_axis[i][0:(size-1)]

    def about(self):
        """ Button About """
        logging.debug('--> About Button.')
        #self.aboutbox = QMessageBox()
        self.aboutbox.setWindowTitle("About")
        self.aboutbox.setText("<center></center><b>Tauno Serial Plotter</b><br/><br/>\
            More info: <a href ='https://github.com/taunoe/tauno-serial-plotter'>\
            github.com/taunoe/tauno-serial-plotter</a><br/><br/>\
            Version {}<br/><br/>\
            Tauno Erik<br/><br/>\
            2021-2022".format(VERSION))
        self.aboutbox.exec_()

    def get_numbers(self, string):
        """
        Function to extract all the numbers from the given string
        https://www.regular-expressions.info/floatingpoint.html
        """
        numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+', string)
        return numbers

    def add_numbers(self, i, number, plot_data_size):
        """
        y-axis
        """
        # If list is full
        if len(self.plot.y_axis[i]) > plot_data_size:
            # Remove the first element on list
            self.plot.y_axis[i] = self.plot.y_axis[i][1:]
        # Before adding newone
        self.plot.y_axis[i].append(float(number))

    def add_time(self, plot_data_size):
        """
        x-axis
        """
        # If list is full
        if len(self.plot.x_axis) > plot_data_size:
            # Remove the first element on list
            self.plot.x_axis = self.plot.x_axis[1:]
        # Add a new value 1 higher than the last to end
        self.plot.x_axis.append(self.plot.x_axis[-1] + 1)

    def open_serial(self):
        try:
            logging.debug("0 Open serial: %s %s", self.selected_port, self.selected_baudrate)
            if self.ser.is_open:
                self.ser.close()
            self.ser = serial.Serial(self.selected_port, int(self.selected_baudrate), timeout=0.09)
            self.ser.reset_input_buffer()## 09.02.2022
            logging.debug("1 Open serial: %s %s", self.ser.name, self.ser.baudrate)
        except IOError:
            logging.error("open_serial IOError")

    def close_serial(self):
        """ Close serial connection. """
        logging.debug("Close serial.")
        self.ser.close()

    def error_status(self):
        """
        If we have to many errors close serial connection.
        Example:
            self.error_counter += 1
            self.error_status()
        """
        if self.error_counter > 9:
            self.close_serial()
            self.error_counter = 0

    def read_serial_data(self):

        if self.ser.is_open:
            try:
                incoming_data = self.ser.readline().decode('utf8')
                # [:-2] gets rid of the new-line chars
                if incoming_data:
                    logging.info("read_serial_dat: Incoming data: %s", incoming_data)
                    numbers = self.get_numbers(incoming_data)
                    logging.debug("numbers: %s", len(numbers))

                    # mitu data punkti tuleb sisse?
                    while len(numbers) > len(self.plot.y_axis):
                        self.plot.y_axis.append([0])

                    for count, value in enumerate(numbers):
                        self.add_numbers(count, value, self.plot_data_size)

                    self.add_time(self.plot_data_size) # x axis

                    for i in range(self.number_of_lines):
                        logging.debug("for loop %s", i)
                        logging.debug("plot.x_axis %s", self.plot.x_axis)
                        logging.debug("plot.y_axis[i] %s", self.plot.y_axis[i])
                        # plot.x_axis [8, 9]
                        # plot.y_axis[i] [333.0]
                        if len(self.plot.x_axis) > len(self.plot.y_axis[i]):
                            # At beginning append 0.0
                            self.plot.y_axis[i].insert(0, 0.0)
                        self.plot.data_lines[i].setData(self.plot.x_axis, self.plot.y_axis[i])
            except Exception as ex:
                logging.debug(ex)
                logging.debug("Error read_serial_data!!!")
                self.error_counter += 1
                self.error_status()
                self.equal_x_and_y()
                
            except SystemExit:  
                logging.debug(sys.exc_info())
                #self.threadpool.disconnect()


    def how_many_lines(self):
        """
            Return number of different incoming data lines.
            Example: data:454something45t=454-\n == 3
        """
        logging.debug("How_many_lines?")
        self.open_serial()
        if self.ser.is_open:
            try:
                # This may be half of data
                # [:-2] removes the new-line chars.
                broken_data = self.ser.readline()#[:-2].decode('ascii')
                logging.debug("try broken_data %s", broken_data)
                # Full data is between two \n chars
                incoming_data = self.ser.readline().decode('utf8')
                
                logging.debug("try incoming_data %s", incoming_data)
                
                i = 0
                while not incoming_data:
                    #_ = self.ser.readline().decode('ascii')  # Often broken data
                    incoming_data = self.ser.readline().decode('utf8') #readline()[:-1]
                    if i > self.max_tryes:
                        break
                    logging.debug("i = %s", i)
                    logging.debug("while not incoming_data %s", incoming_data)
                    i = i+1
                    

                if incoming_data:
                    logging.debug("if Incoming data %s", incoming_data)
                    numbers = self.get_numbers(incoming_data)
                    logging.debug("Found: %s lines", len(numbers))
                    return len(numbers)

            except Exception as ex:
                logging.debug(ex)
                logging.debug("Error how_many_lines")
                self.ser.close()
                
            except SystemExit:  
                logging.debug(sys.exc_info())
                #logging.debug("Error how_many_lines")
                #self.ser.close()


    def keyPressEvent(self, event):
        """
            Detect keypress and runs function
        """
        if event.key() == 32: # Space
            logging.debug("Space")
        elif event.key() == 16777219: # Backspace
            logging.debug("Backspace")
        elif event.key() == 16777274: # F11
            self.key_f11()
        elif event.key() == 16777216: # Esc
            self.key_esc()
        else:
            logging.debug("Unknown keypress: %s, %s", event.key(),event.text())

    def key_f11(self):
        """ F11 of/off fullscreen"""
        if not self.is_fullscreen:
            self.showFullScreen()
            self.is_fullscreen = True
        else:
            self.showNormal()
            self.is_fullscreen = False

    def key_esc(self):
        """ Window is on fullscreen and user presses ESC """
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False

    #def mouseClickEvent(self, event):
        #print("clicked")

# END of class MainWindow --------------------------------------------

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()

    try:
        sys.exit(app.exec_()) # sys.exit(app.exec_())
    except SystemExit:
        stop_port_scan = True # Kill port scan thread
        print(SystemExit)
