#!/usr/bin/env python3
"""
    Tauno-Serial-Plotter.py
    Author: Tauno Erik
    Started:    07.03.2020
    Edited:     03.01.2021

    Useful links:
    - https://www.learnpyqt.com/courses/graphics-plotting/plotting-pyqtgraph/
    - https://www.materialui.co/colors
    - https://stackoverflow.com/questions/40577104/how-to-plot-two-real-time-data-in-one-single-plot-in-pyqtgraph
    - https://www.youtube.com/watch?v=IEEhzQoKtQU&t=800s

"""

import sys
import re
import serial # pip3 install pyserial
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout,
                            QLabel, QWidget, QDesktopWidget, QMessageBox)
import pyqtgraph as pg

# Enable highdpi scaling:
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
# Use highdpi icons:
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# Define GUI colours
colors =  {
            'oranz':"#FF6F00",
            'green':"#9CCC65",
            'dark' :"#263238",
            'hall' :"#B0BEC5",
	        'black':"#212121"
}

# Define PLOT colors
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
    image: url(icons/arrow_down.svg);
    width: 24px;
    height: 24px;
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
    image: url(icons/arrow_down.svg);
    width: 24px;
    height: 24px;
}}
"""


QDoubleSpinBox_style = f"""
QDoubleSpinBox{{
    background-color: {colors['hall']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    padding: 5px 25px 5px 25px; 
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
    height:32px;
}}

QDoubleSpinBox::up-arrow {{
    image: url(icons/plus.svg);
    width: 24px;
    height: 24px;
}}

QDoubleSpinBox::down-button{{
    /*subcontrol-origin: border;*/
    background-color: {colors['dark']};
    subcontrol-position: top left;
    width: 25px;
    /*border-width: 1px;*/
    height:32px;
}}

QDoubleSpinBox::down-arrow {{
    image: url(icons/minus.svg);
    width: 24px;
    height: 24px;
}}

"""

class Plot(pg.GraphicsWindow):
    """
    Define Plot
    """
    def __init__(self, nr_plot_lines='1', scatter_plot=False):
        super(Plot,self).__init__(parent=None)

        self.nr_plot_lines = nr_plot_lines
        self.scatter_plot = scatter_plot

        if self.nr_plot_lines is None:
            print("nr_plot_lines is None!")

        print("Init Plot class. With {} plot lines.".format(self.nr_plot_lines))

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
            if self.scatter_plot:  # Dotts
                pen = None
            else:                  # Lines
                if i >= len(plot_colors):
                    # If we have more data than colors
                    color_i = i - len(plot_colors)
                else:
                    color_i = i
            pen = pg.mkPen(color=(plot_colors[color_i]))
            brush = pg.mkBrush(color=(plot_colors[color_i]))
            line = self.serialplot.plot(x=self.x_axis, y=self.y_axis[i], pen=pen,
                                symbol='o', symbolBrush=brush, symbolSize=5)
            self.data_lines.append(line)

# END of class Plot ------------------------------------------------------

class Controls(QWidget):
    """
    Define controls and menus design.
    """
    def __init__(self, parent=None):
        super(Controls, self).__init__(parent=parent)

        # Plot time scale == data size
        self.plot_timescale = 100 # default
        self.plot_timescale_min = 50
        self.plot_timescale_max = 500

        self.vertical_layout = QVBoxLayout(self)

        # Menu width:
        self.control_width = 150

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

        # Select line or dot
        self.line_box = QtWidgets.QCheckBox('Line plot', parent=self)
        self.menu_1.addWidget(self.line_box)
        self.line_box.setChecked(1)
        self.line_box.setStyleSheet(QCheckBox_style)

        self.dot_box = QtWidgets.QCheckBox('Dot plot', parent=self)
        self.menu_1.addWidget(self.dot_box)
        self.dot_box.setChecked(0)
        self.dot_box.setStyleSheet(QCheckBox_style)

        # Select Time scale size
        ## Time scale txt
        self.time_scale_txt = QLabel(self)
        self.menu_1.addWidget(self.time_scale_txt)
        self.time_scale_txt.setText("Timescale:")
        self.time_scale_txt.setStyleSheet(QLabel_style)
        ## SpinBox
        self.time_scale_spin = QtWidgets.QDoubleSpinBox()
        self.time_scale_spin.setSingleStep(1)
        self.time_scale_spin.setDecimals(0)
        self.time_scale_spin.setMaximum(self.plot_timescale_max)
        self.time_scale_spin.setMinimum(self.plot_timescale_min)
        self.time_scale_spin.setValue(self.plot_timescale)
        self.menu_1.addWidget(self.time_scale_spin)
        self.time_scale_spin.setStyleSheet(QDoubleSpinBox_style)

        # Button Connect
        self.connect = QtWidgets.QPushButton('Connect', parent=self)
        self.menu_1.addWidget(self.connect)
        self.connect.setFixedWidth(self.control_width)
        self.connect.setStyleSheet(QPushButton_style)

        self.vertical_layout.addLayout(self.menu_1)
        # Grpup 1 ends

        # Button goup 2
        self.menu_3 = QVBoxLayout()
        self.menu_3.setAlignment(Qt.AlignBottom)

        # Button: Clear data
        self.clear_data = QtWidgets.QPushButton('Clear data', parent=self)
        self.menu_3.addWidget(self.clear_data)
        self.clear_data.setFixedWidth(self.control_width)
        self.clear_data.setStyleSheet(QPushButton_style)

        # Button: About
        self.about = QtWidgets.QPushButton('About', parent=self)
        self.menu_3.addWidget(self.about)
        self.about.setFixedWidth(self.control_width)
        self.about.setStyleSheet(QPushButton_style)

        self.vertical_layout.addLayout(self.menu_3)

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
        self.baudrates = ['300','1200','2400','4800','9600','19200','38400','57600',
                        '74880','115200','230400','250000','500000','1000000','2000000']
        self.selected_baudrate = self.baudrates[4]

        self.number_of_lines = 0
        self.error_counter = 0
        self.plot_data_size = 100
        self.scatter_plot = False
        self.is_button_connected = False

        self.init_ui()
        self.center_mainwindow()

        self.init_timer()
        self.ser = serial.Serial()

        self.horizontal_layout = QHBoxLayout(self)

        # Controlls
        self.controls = Controls(parent=self)
        self.horizontal_layout.addWidget(self.controls)

        self.find_ports()       # Ports on dropdown menu
        self.init_baudrates()   # Baud Rates on dropdown menu

        # Controll selct and button calls
        self.controls.select_port.currentIndexChanged.connect(self.selected_port_changed)
        self.controls.select_baud.currentIndexChanged.connect(self.selected_baud_changed)
        self.controls.time_scale_spin.valueChanged.connect(self.time_scale_changed)
        self.controls.connect.pressed.connect(self.connect_stop)
        self.controls.clear_data.pressed.connect(self.clear_data)
        self.controls.about.pressed.connect(self.about)

        self.controls.dot_box.pressed.connect(self.selected_dot)
        self.controls.line_box.pressed.connect(self.selected_line)

    # Init functions

    def init_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        self.timer.start()

    def init_ui(self):
        self.setStyleSheet(f"MainWindow {{ background-color: {colors['dark']}; }}")
        self.setWindowTitle("Tauno Serial Plotter")
        self.setWindowIcon(QtGui.QIcon('icons/tauno-plotter.svg'))
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

    def init_baudrates(self):
        self.controls.select_baud.addItems(self.baudrates)
        self.controls.select_baud.setCurrentIndex(4)

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
            try:
                print("equal_x_and_y try")
                for i in range(self.number_of_lines):
                    if len(self.plot.x_axis) > len(self.plot.y_axis[i]):
                        print("\t x on suurem kui y[{}]".format(i))
                        while len(self.plot.x_axis) > len(self.plot.y_axis[i]):
                            # Remove the first element on list
                            self.plot.x_axis = self.plot.x_axis[1:]
                    if len(self.plot.y_axis[i]) > len(self.plot.x_axis):
                        print("\t y[{i}] on suurem kui x_axis".format(i))
                        while len(self.plot.y_axis[i]) > len(self.plot.x_axis):
                            # Remove the first element on list
                            self.plot.y_axis[i] = self.plot.y_axis[i][1:]
            except:
                print(sys.exc_info())
                self.error_counter += 1
                self.error_status()


    def selected_dot(self):
        print("Selected dot plot.")
        if not self.plot_exist:
            self.controls.line_box.setChecked(0)
            self.scatter_plot = True


    def selected_line(self):
        print("Selected line plot.")
        if not self.plot_exist:
            self.controls.dot_box.setChecked(0)
            self.scatter_plot = False

    def time_scale_changed(self):
        print("Timescale changed!")
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
            print('--> Connect Button.')
            self.connect()
        else:
            self.is_button_connected = False
            print('--> Pause Button.')
            self.disconnect()

    
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
            print("connect: create plot")
            self.number_of_lines = self.how_many_lines()
            if self.number_of_lines is not None:
                self.plot = Plot(self.number_of_lines, self.scatter_plot)
                self.horizontal_layout.addWidget(self.plot)
                self.open_serial()
                self.plot_exist = True
                self.timer.timeout.connect(self.read_serial_data)
                self.controls.dot_box.setEnabled(False)
                self.controls.line_box.setEnabled(False)
            else:
                print("connect: None!")
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
        print('--> Clear data Button.')
        # delete existing data
        size = len(self.plot.x_axis)
        print("x_axis: {}".format(size))
        del self.plot.x_axis[0:(size-1)]
        for i in range(self.number_of_lines):
            del self.plot.y_axis[i][0:(size-1)]

    def about(self):
        """ Button About """
        print('--> About Button.')
        self.msg = QMessageBox()
        self.msg.setWindowTitle("About")
        self.msg.setText("Tauno Serial Plotter<br/><br/>Author: Tauno Erik<br/><a href ='https://github.com/taunoe/tauno-serial-plotter'>github.com/taunoe/tauno-serial-plotter</a><br/><br/>2021")
        self.aboutbox = self.msg.exec_()

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
        print("add_numbers y-axis")
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
        print("add_time x-axis")
        # If list is full
        if len(self.plot.x_axis) > plot_data_size:
            # Remove the first element on list
            self.plot.x_axis = self.plot.x_axis[1:]
        # Add a new value 1 higher than the last to end
        self.plot.x_axis.append(self.plot.x_axis[-1] + 1)

    def open_serial(self):
        print("0 Open serial: {} {}".format(self.selected_port, self.selected_baudrate))
        if self.ser.is_open:
            self.ser.close()
        self.ser = serial.Serial(self.selected_port, int(self.selected_baudrate), timeout=0.09)
        print("1 Open serial: {} {}".format(self.ser.name, self.ser.baudrate))

    def close_serial(self):
        """ Close serial connection. """
        print("Close serial.")
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
                incoming_data = self.ser.readline()[:-2].decode('ascii')
                # [:-2] gets rid of the new-line chars
                if incoming_data:
                    print("Incoming data: {}".format(incoming_data))
                    numbers = self.get_numbers(incoming_data)
                    print("numbers: {}".format(len(numbers)))

                    # mitu data punkti tuleb sisse?
                    while len(numbers) > len(self.plot.y_axis):
                        self.plot.y_axis.append([0])

                    for count, value in enumerate(numbers):
                        self.add_numbers(count, value, self.plot_data_size)

                    self.add_time(self.plot_data_size) # x axis

                    for i in range(self.number_of_lines):
                        print("for loop {}".format(i))
                        print("plot.x_axis {}".format(self.plot.x_axis))
                        print("plot.y_axis[i] {}".format(self.plot.y_axis[i]))
                        # TODO: !!! siin on probleem !!!
                        # plot.x_axis [8, 9]
                        # plot.y_axis[i] [333.0]
                        if len(self.plot.x_axis) > len(self.plot.y_axis[i]):
                            # At beginning append 0.0 
                            self.plot.y_axis[i].insert(0, 0.0)
                        self.plot.data_lines[i].setData(self.plot.x_axis, self.plot.y_axis[i])

            except:
                print(sys.exc_info())
                print("Error read_serial_data!!!")
                self.error_counter += 1
                self.error_status()
                self.equal_x_and_y()

    
    def how_many_lines(self):
        """
            Return number of different incoming data lines.
            Example: --454-45-454- == 3
        """
        print("How_many_lines?")
        self.open_serial()
        if self.ser.is_open:
            try:
                incoming_data = self.ser.readline()[:-2].decode('ascii')
                # [:-2] removes new-line chars
                while not incoming_data:
                    incoming_data = self.ser.readline()[:-2].decode('ascii')
                if incoming_data:
                    print("Incoming data {}".format(incoming_data))
                    numbers = self.get_numbers(incoming_data)
                    print("Found: {} lines".format(len(numbers)))
                    return len(numbers)
            except:
                print(sys.exc_info())
                print("Error how_many_lines")
                self.ser.close()

    # Keyboard functions:
    def keyPressEvent(self, event):
        """
            Detect keypress and run function
        """
        if event.key() == 32: # Space
            print("Space")
        elif event.key() == 16777219: # Backspace
            print("Backspace")
        elif event.key() == 16777274: # F11
            self.fullscreen()
        elif event.key() == 16777216: # Esc
            self.esc()
        else:
            print(f'Unknown keypress: {event.key()}, "{event.text()}"')

    def fullscreen(self):
        if not self.is_fullscreen:
            self.showFullScreen()
            self.is_fullscreen = True
        else:
            self.showNormal()
            self.is_fullscreen = False

    def esc(self):
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
    sys.exit(app.exec_())
