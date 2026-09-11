#!/usr/bin/env python3
"""
    File:    Tauno-Serial-Plotter.py
    Author:  Tauno Erik
    Started: 07.03.2020
    Edited:  08.09.2026
"""
import sys
import re
import logging
from enum import Enum, auto
import serial
import serial.tools.list_ports
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import (QSettings, Qt, QMetaObject, QThread, pyqtSignal,
                          pyqtSlot)
from PyQt6.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout,
                            QLabel, QWidget, QMessageBox)
import pyqtgraph as pg
from theme import create_theme

VERSION = '1.21.2'
TIMESCALESIZE = 400  # = self.plot_timescale and self.plot_data_size

if __name__ == '__main__':
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    if hasattr(Qt, 'AA_Use96Dpi'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_Use96Dpi, True)
    app = QApplication(sys.argv)
    theme = create_theme(app)
    colors = theme.colors
    plot_colors = theme.plot_colors
    icon_logo = theme.icons["logo"]
    icon_minus = theme.icons["minus"]
    icon_plus = theme.icons["plus"]
    icon_arrow_down = theme.icons["arrow_down"]
    icon_about = theme.icons["about"]
    icon_clean = theme.icons["clean"]
    icon_size = theme.icons["size"]


class ConnectionState(Enum):
    """States in the serial connection lifecycle."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()

# Set debuge level
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.CRITICAL)


# STYLING
FONTSIZE = '16px'
BORDER_RADIUS = '5px'

# Graph style
pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', colors['dark'])
pg.setConfigOption('foreground', colors['foreground'])

btn_icon_style = f"""
QPushButton{{
    color: {colors['black']};
    background-color: {colors['hall']};
    border: 1px solid {colors['dark']};
    border-radius: {BORDER_RADIUS};
    padding: 5px;
    margin-top: 0px;
    font: {FONTSIZE};
}}

QPushButton::hover{{
    background-color: {colors['accent']};
    color: {colors['black']};
}}

QPushButton::pressed{{
    border: 1px solid {colors['oranz']};
    background-color: {colors['hall']};
}}"""

btn_icon_style_disabled = f"""
QPushButton{{
    color: {colors['black']};
    background-color: {colors['dark']};
    border: 1px solid {colors['dark']};
    padding: 5px;
    margin-top: 0px;
    font: {FONTSIZE};
}}
"""

btn_style = f"""
QPushButton{{
    color: {colors['black']};
    background-color: {colors['hall']};
    border: 1px solid {colors['black']};
    border-radius: {BORDER_RADIUS};
    padding: 5px;
    margin-top: 0px;
    font: {FONTSIZE};
}}

QPushButton::hover{{
    background-color: {colors['accent']};
    color: {colors['black']};
}}

QPushButton::pressed{{
    border: 1px solid {colors['oranz']};
    background-color: {colors['hall']};
}}"""

btn_style_disabled = f"""
QPushButton{{
    color: {colors['black']};
    background-color: {colors['dark']};
    border: 1px solid {colors['black']};
    padding: 5px;
    margin-top: 0px;
    font: {FONTSIZE};
}}
"""

label_style = f"""
QLabel{{
    color: {colors['foreground']};
    font: {FONTSIZE};
    margin-top: 0px;
}}
"""

Qinfo_text_style = f"""
QLabel{{
    color: {colors['foreground']};
    font: {FONTSIZE};
    margin-top: 0px;
}}
"""


dropdown_style = f"""
QComboBox:editable, QComboBox{{
    background-color: {colors['hall']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    border-radius: {BORDER_RADIUS};
    padding: 5px 25p 5px 5px;
    font: {FONTSIZE};
}}

QComboBox::hover{{
    background-color: {colors['accent']};
    color: {colors['black']}; /* tekst*/
}}

QComboBox:editable:on, QComboBox:on {{ /* shift the text when the popup opens */
    padding-left: 10px;
    background-color: {colors['accent']};
    color: {colors['dark']};
}}

QComboBox::drop-down {{ /* shift the text when the popup opens */
    background-color: {colors['dark']}; /* noole tagune */
    color: {colors['accent']};
    border: none;
    border-top-right-radius: {BORDER_RADIUS};
    border-bottom-right-radius: {BORDER_RADIUS};
    width: 24px;
}}

QComboBox::down-arrow {{
    background-color: {colors['dark']};/* nool */
    image: url({icon_arrow_down});
    width: 24px;
    height: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {colors['hall']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    border-radius: {BORDER_RADIUS};
}}
"""

dropdown_style_disabled = f"""
QComboBox:editable, QComboBox{{
    background-color: {colors['dark']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    border-radius: {BORDER_RADIUS};
    padding: 5px 25p 5px 5px;
    font: {FONTSIZE};
}}

QComboBox::drop-down {{ /* shift the text when the popup opens */
    background-color: {colors['dark']}; /* noole tagune */
    color: {colors['accent']};
    border: none;
    border-top-right-radius: {BORDER_RADIUS};
    border-bottom-right-radius: {BORDER_RADIUS};
    width: 24px;
}}

QComboBox::down-arrow {{
    background-color: {colors['dark']};/* nool */
    image: url({icon_arrow_down});
    width: 24px;
    height: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {colors['dark']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    border-radius: {BORDER_RADIUS};
}}
"""


QDoubleSpinBox_style = f"""
QDoubleSpinBox{{
    background-color: {colors['hall']};
    color: {colors['black']};
    border: 1px solid {colors['black']};
    border-radius: {BORDER_RADIUS};
    padding: 0px; 
    font: {FONTSIZE};
}}

QDoubleSpinBox::hover{{
    background-color: {colors['accent']};
    color: {colors['black']}; /* tekst*/
}}

QDoubleSpinBox::up-button{{
    subcontrol-origin: border;
    subcontrol-position: top right;
    background-color: {colors['dark']};
    border: 1px solid {colors['black']};
    border-top-right-radius: {BORDER_RADIUS};
    width: 25px;
    height: 12px;
    margin:0px;
    /*padding-bottom: 1px;*/
}}

QDoubleSpinBox::down-button{{
    subcontrol-origin: border;
    background-color: {colors['dark']};
    subcontrol-position: bottom right;
    border: 1px solid {colors['black']};
    border-bottom-right-radius: {BORDER_RADIUS};
    width: 25px;
    height: 12px;
    /*padding-bottom: 1px;*/
}}

QDoubleSpinBox::up-arrow {{
    image: url({icon_plus});
    width: 16px;
    height: 12px;
}}

QDoubleSpinBox::down-arrow {{
    image: url({icon_minus});
    width: 16px;
    height: 12px;
}}

"""

class PortScanner(QtCore.QObject):
    """
    Scan serial ports in a worker thread and publish results to the GUI.
    """
    ports_found = pyqtSignal(list)

    def __init__(self, interval=10, parent=None):
        super().__init__(parent)
        self.interval = interval
        self.timer = None

    @pyqtSlot()
    def start(self):
        """Start periodic scanning after the worker thread's event loop starts."""
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(self.interval * 1000)
        self.timer.timeout.connect(self.scan)
        self.scan()
        self.timer.start()

    @pyqtSlot()
    def scan(self):
        """Scan ports without touching any GUI objects."""
        ports = []
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
        except OSError:
            logging.exception("Unable to scan serial ports")
        self.ports_found.emit(ports)


class SerialWorker(QtCore.QObject):
    """Own the serial connection and perform all serial I/O off the GUI thread."""
    connected = pyqtSignal(int, list)
    data_received = pyqtSignal(str)
    connection_failed = pyqtSignal(str)
    disconnected = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial = None
        self.timer = None
        self.probing = False
        self.probe_attempts = 0
        self.probe_limit = 7500

    @pyqtSlot()
    def start(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.read_serial)
        self.timer.start()

    @pyqtSlot(str, int)
    def connect_to(self, port, baudrate):
        self._close_serial()
        try:
            self.serial = serial.Serial(port, baudrate, timeout=0)
            self.serial.reset_input_buffer()
            self.probing = True
            self.probe_attempts = 0
        except (OSError, serial.SerialException) as error:
            self.serial = None
            self.connection_failed.emit(str(error))

    @pyqtSlot()
    def disconnect_from_serial(self):
        self._close_serial()
        self.disconnected.emit()

    def _close_serial(self):
        self.probing = False
        if self.serial is not None:
            self.serial.close()
            self.serial = None

    @pyqtSlot()
    def read_serial(self):
        if self.serial is None or not self.serial.is_open:
            return

        try:
            if self.serial.in_waiting == 0:
                if self.probing:
                    self.probe_attempts += 1
                    if self.probe_attempts >= self.probe_limit:
                        self.disconnect_from_serial()
                        self.connection_failed.emit("No numeric data received")
                return

            line = self.serial.readline().decode("utf8", errors="replace")
            if not line:
                return

            if self.probing:
                numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+', line)
                if not numbers:
                    return
                labels = re.findall(r'[-+]?[a-zA-Z]*\.?[a-zA-Z]+', line)
                self.probing = False
                self.connected.emit(len(numbers), labels)
            self.data_received.emit(line)
        except (OSError, serial.SerialException, UnicodeError) as error:
            self.disconnect_from_serial()
            self.connection_failed.emit(str(error))

    @pyqtSlot()
    def stop(self):
        if self.timer is not None:
            self.timer.stop()
        self.disconnect_from_serial()
        self.stopped.emit()


class Plot(pg.GraphicsLayoutWidget):
    """ Plot definition """
    def __init__(self, nr_plot_lines='1', labels=["sensor1"]):
        super(Plot,self).__init__(parent=None)

        self.nr_plot_lines = nr_plot_lines
        self.data_labels =labels

        if self.nr_plot_lines is None:
            logging.debug("nr_plot_lines is None!")

        logging.debug("Init Plot class. With %i plot lines.", self.nr_plot_lines)

        # Create plot
        self.serialplot = self.addPlot()
        self.serialplot.setLabel('left', 'Data')
        self.serialplot.setLabel('bottom', 'Time')
        self.serialplot.showGrid(x=True, y=True)
        self.serialplot.addLegend()

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

            pen = pg.mkPen(color=(plot_colors[color_i]), width=3)

            brush = pg.mkBrush(color=(plot_colors[color_i]))
            # Quick fix:
            # https://github.com/taunoe/tauno-serial-plotter/issues/71#issuecomment-1769499968
            if len(self.data_labels) == len(self.y_axis):
                line = self.serialplot.plot(x=self.x_axis, y=self.y_axis[i], name=self.data_labels[i],
                                       pen=pen, symbol='o', symbolBrush=brush, symbolSize=3)
            else:
                line = self.serialplot.plot(x=self.x_axis, y=self.y_axis[i],
                                       pen=pen, symbol='o', symbolBrush=brush, symbolSize=3)
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

        self.top_menu_row = QHBoxLayout(self)
        self.top_menu_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Menu width:
        self.control_width = 550

        # Top Menu
        self.menu_top = QHBoxLayout()#QVBoxLayout()
        self.menu_top.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Label Baud
        self.baud_label = QLabel(self)
        self.menu_top.addWidget(self.baud_label)
        self.baud_label.setText("Baud:")
        self.baud_label.setStyleSheet(label_style)
        # Select Baud
        self.select_baud = QtWidgets.QComboBox(parent=self)
        self.menu_top.addWidget(self.select_baud)
        self.select_baud.setStyleSheet(dropdown_style)
        self.select_baud.setFixedWidth(100)
        self.select_baud.setEditable(True)
        self.select_baud.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        

        # Label Port
        self.device_label = QLabel(self)
        self.menu_top.addWidget(self.device_label)
        self.device_label.setText("Port:")
        self.device_label.setStyleSheet(label_style)
        # Select Port
        self.select_port = QtWidgets.QComboBox(parent=self)
        self.menu_top.addWidget(self.select_port)
        self.select_port.setStyleSheet(dropdown_style)
        self.select_port.setFixedWidth(150)

        # Button Connect
        self.connect = QtWidgets.QPushButton('Connect', parent=self)
        self.menu_top.addWidget(self.connect)
        self.connect.setFixedWidth(100)
        self.connect.setStyleSheet(btn_style)

        # Info text
        #self.info_text = QLabel(self)
        #self.menu_top.addWidget(self.info_text)
        #self.info_text.setText("\nTo export data\nright-click on the plot.")
        #self.info_text.setStyleSheet(Qinfo_text_style)

        self.top_menu_row.addLayout(self.menu_top)
        # Top menu ends


        # Bottom menu
        self.menu_left = QHBoxLayout()#QVBoxLayout()
        self.menu_left.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Select Time scale size
        ## Time scale txt
        self.time_scale_txt = QLabel(self)
        self.menu_left.addWidget(self.time_scale_txt)
        #self.time_scale_txt.set(QtGui.QIcon(icon_size))
        self.time_scale_txt.setText("Size:")
        self.time_scale_txt.setStyleSheet(label_style)
        ## SpinBox
        self.time_scale_spin = QtWidgets.QDoubleSpinBox()
        self.time_scale_spin.setSingleStep(1)
        self.time_scale_spin.setDecimals(0)
        self.time_scale_spin.setFixedWidth(120)
        self.time_scale_spin.setMaximum(self.plot_timescale_max)
        self.time_scale_spin.setMinimum(self.plot_timescale_min)
        self.time_scale_spin.setValue(self.plot_timescale)
        self.menu_left.addWidget(self.time_scale_spin)
        self.time_scale_spin.setStyleSheet(QDoubleSpinBox_style)


        self.btn_clear = QtWidgets.QPushButton()
        self.btn_clear.setIcon(QtGui.QIcon(icon_clean))
        self.btn_clear.setIconSize(QtCore.QSize(13,16))
        self.btn_clear.setFixedWidth(30)
        self.btn_clear.setStyleSheet(btn_icon_style_disabled)
        self.btn_clear.setEnabled(False)

        self.menu_left.addWidget(self.btn_clear)

        # Button: About
        self.about = QtWidgets.QPushButton(
            icon=QtGui.QIcon(icon_about),
            text='',
            parent=self)
        self.menu_left.addWidget(self.about)
        self.about.setFixedWidth(30)
        self.about.setStyleSheet(btn_icon_style)

        self.top_menu_row.addLayout(self.menu_left)

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
    serial_connect_requested = pyqtSignal(str, int)
    serial_disconnect_requested = pyqtSignal()

    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.app = app
        self.settings = QSettings("TaunoErik", "TaunoSerialPlotter")
        self.plot_exist = False
        self.is_fullscreen = False

        self.labels = ["label"]
        self.ports = [''] # list of avablie devices
        self.selected_port = self.settings.value("serial/port", self.ports[0], type=str)
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
        saved_baudrate = self.settings.value(
            "serial/baudrate", self.baudrates[self.default_baud_index], type=str)
        if saved_baudrate not in self.baudrates:
            saved_baudrate = self.baudrates[self.default_baud_index]
        self.selected_baudrate = saved_baudrate
        logging.debug("self.selected_baudrate =")
        logging.debug(self.selected_baudrate)

        self.number_of_lines = 0
        self.error_counter = 0
        self.plot_data_size = TIMESCALESIZE #?
        self.connection_state = ConnectionState.DISCONNECTED

        self.init_ui()
        self.center_mainwindow()
        self.horizontal_layout = QVBoxLayout(self) #QHBoxLayout(self)

        # Controlls
        self.controls = Controls(parent=self)
        self.horizontal_layout.addWidget(self.controls)

        self.init_baudrates()   # Baud Rates on dropdown menu

        self.port_scanner_thread = QThread(self)
        self.port_scanner = PortScanner()
        self.port_scanner.moveToThread(self.port_scanner_thread)
        self.port_scanner_thread.started.connect(self.port_scanner.start)
        self.port_scanner.ports_found.connect(self.update_ports)
        self.port_scanner_thread.finished.connect(self.port_scanner.deleteLater)
        self.port_scanner_thread.start()

        self.serial_thread = QThread(self)
        self.serial_worker = SerialWorker()
        self.serial_worker.moveToThread(self.serial_thread)
        self.serial_thread.started.connect(self.serial_worker.start)
        self.serial_connect_requested.connect(self.serial_worker.connect_to)
        self.serial_disconnect_requested.connect(self.serial_worker.disconnect_from_serial)
        self.serial_worker.connected.connect(self.serial_connected)
        self.serial_worker.data_received.connect(self.handle_serial_data)
        self.serial_worker.connection_failed.connect(self.serial_connection_failed)
        self.serial_worker.disconnected.connect(self.serial_disconnected)
        self.serial_worker.stopped.connect(self.serial_thread.quit)
        self.serial_thread.finished.connect(self.serial_worker.deleteLater)
        self.serial_thread.start()

        # Controll selct and button calls
        self.controls.select_port.currentIndexChanged.connect(self.selected_port_changed)
        self.controls.select_baud.currentIndexChanged.connect(self.selected_baud_changed)
        self.controls.time_scale_spin.valueChanged.connect(self.time_scale_changed)
        self.controls.connect.pressed.connect(self.connect_stop)
        self.controls.btn_clear.pressed.connect(self.clear_data)
        self.controls.about.pressed.connect(self.about)

        # Init About window
        self.aboutbox = QMessageBox()



    def init_ui(self):
        self.setObjectName("mainWindow")
        self.setStyleSheet(
            f"QWidget#mainWindow {{ background-color: {colors['dark']}; }}")
        self.setWindowTitle("Tauno Serial Plotter")
        self.setWindowIcon(QtGui.QIcon(icon_logo))
        self.setMinimumSize(900,550)

    def center_mainwindow(self):
        """ Center window on startup. """
        qr = self.frameGeometry()

        #cp = QDesktopWidget().availableGeometry().center() #PyQt5
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        cp = rect.center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @pyqtSlot(list)
    def update_ports(self, ports):
        """
        Update port controls on the GUI thread.
        """
        logging.debug("self.plot_exist %s", self.plot_exist)
        logging.debug("self.connection_state %s", self.connection_state.name)

        before_selected_port = self.selected_port
        logging.debug("before_selected_port %s", before_selected_port)

        if self.plot_exist and self.connection_state == ConnectionState.CONNECTED:
            return

        self.ports = ports
        self.controls.select_port.blockSignals(True)
        self.controls.select_port.clear()
        self.controls.select_port.addItems(self.ports)

        if self.ports:
            index = self.ports.index(before_selected_port) if before_selected_port in self.ports else 0
            self.controls.select_port.setCurrentIndex(index)
            self.selected_port = self.ports[index]
        else:
            self.selected_port = ''
        self.controls.select_port.blockSignals(False)

    def init_baudrates(self):
        self.controls.select_baud.addItems(self.baudrates)
        self.controls.select_baud.setCurrentIndex(
            self.baudrates.index(self.selected_baudrate))

    def selected_port_changed(self, i):
        if i < 0 or i >= len(self.ports):
            return
        self.selected_port = self.ports[i]
        self.settings.setValue("serial/port", self.selected_port)
        logging.info("Main selected port changed:")
        logging.info(self.selected_port)

    def selected_baud_changed(self, i):
        self.selected_baudrate = self.baudrates[i]
        self.settings.setValue("serial/baudrate", self.selected_baudrate)
        logging.info("Main selected baud index changed:")
        logging.info(self.selected_baudrate)
        self.equal_x_and_y()
        if self.connection_state == ConnectionState.CONNECTED:
            self.request_serial_connection()

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
        if self.connection_state in (
                ConnectionState.DISCONNECTED, ConnectionState.ERROR):
            logging.debug('--> Connect Button.')
            self.connect()
        elif self.connection_state in (
                ConnectionState.CONNECTING, ConnectionState.CONNECTED):
            logging.debug('--> Pause Button.')
            self.disconnect()


    def connect(self):
        """ When we press button Connect. """
        self.set_connection_state(ConnectionState.CONNECTING)
        # Change button txt
        self.controls.connect.setText('Connecting...')
        # Disable button
        self.controls.select_port.setEnabled(False)
        self.controls.select_baud.setEnabled(False)
        # Change button style
        self.controls.select_port.setStyleSheet(dropdown_style_disabled)
        self.controls.select_baud.setStyleSheet(dropdown_style_disabled)

        self.request_serial_connection()

    def disconnect(self):
        """ When we press Pause button """
        self.serial_disconnect_requested.emit()
        self.set_connection_state(ConnectionState.DISCONNECTED)
        # Change button txt
        self.controls.connect.setText('Connect')
        # Enable buttons
        self.controls.select_port.setEnabled(True)
        self.controls.select_baud.setEnabled(True)
        # Change button style
        self.controls.select_port.setStyleSheet(dropdown_style)
        self.controls.select_baud.setStyleSheet(dropdown_style)
        self.controls.btn_clear.setEnabled(False)
        self.controls.btn_clear.setStyleSheet(btn_icon_style_disabled)

    def request_serial_connection(self):
        self.serial_connect_requested.emit(
            self.selected_port, int(self.selected_baudrate))

    def set_connection_state(self, state):
        """Apply a valid connection transition and update shared state."""
        valid_transitions = {
            ConnectionState.DISCONNECTED: {
                ConnectionState.CONNECTING, ConnectionState.ERROR},
            ConnectionState.CONNECTING: {
                ConnectionState.CONNECTED, ConnectionState.DISCONNECTED,
                ConnectionState.ERROR},
            ConnectionState.CONNECTED: {
                ConnectionState.CONNECTING, ConnectionState.DISCONNECTED,
                ConnectionState.ERROR},
            ConnectionState.ERROR: {
                ConnectionState.CONNECTING, ConnectionState.DISCONNECTED},
        }
        if state != self.connection_state and state not in valid_transitions[self.connection_state]:
            logging.warning(
                "Ignoring invalid connection transition: %s -> %s",
                self.connection_state.name, state.name)
            return False
        self.connection_state = state
        logging.info("Connection state: %s", state.name)
        return True

    @pyqtSlot()
    def serial_disconnected(self):
        if self.connection_state != ConnectionState.DISCONNECTED:
            self.set_connection_state(ConnectionState.DISCONNECTED)

    @pyqtSlot(int, list)
    def serial_connected(self, number_of_lines, labels):
        if self.connection_state != ConnectionState.CONNECTING:
            logging.debug("Ignoring stale serial connection result")
            return
        self.number_of_lines = number_of_lines
        self.labels = labels or ["label"]
        if not self.plot_exist:
            self.plot = Plot(self.number_of_lines, self.labels)
            self.horizontal_layout.addWidget(self.plot)
            self.plot_exist = True
        self.set_connection_state(ConnectionState.CONNECTED)
        self.controls.connect.setText('Pause')
        self.controls.btn_clear.setEnabled(True)
        self.controls.btn_clear.setStyleSheet(btn_icon_style)

    @pyqtSlot(str)
    def serial_connection_failed(self, error):
        logging.error("Serial connection failed: %s", error)
        self.set_connection_state(ConnectionState.ERROR)
        self.controls.connect.setText('Connect')
        self.controls.select_port.setEnabled(True)
        self.controls.select_baud.setEnabled(True)
        self.controls.select_port.setStyleSheet(dropdown_style)
        self.controls.select_baud.setStyleSheet(dropdown_style)
        self.controls.btn_clear.setEnabled(False)
        self.controls.btn_clear.setStyleSheet(btn_icon_style_disabled)
        QMessageBox.critical(
            self,
            "Serial connection failed",
            error or "Unable to connect to the selected serial port.")

    @pyqtSlot(str)
    def handle_serial_data(self, incoming_data):
        if (not self.plot_exist
                or self.connection_state != ConnectionState.CONNECTED):
            return
        try:
            numbers = self.get_numbers(incoming_data)

            for count, value in enumerate(numbers[:self.number_of_lines]):
                self.add_numbers(count, value, self.plot_data_size)

            self.add_time(self.plot_data_size)
            for i in range(self.number_of_lines):
                if len(self.plot.y_axis[i]) > len(self.plot.x_axis):
                    self.plot.y_axis[i] = self.plot.y_axis[i][-len(self.plot.x_axis):]
                if len(self.plot.x_axis) > len(self.plot.y_axis[i]):
                    missing = len(self.plot.x_axis) - len(self.plot.y_axis[i])
                    self.plot.y_axis[i][0:0] = [0.0] * missing
                self.plot.data_lines[i].setData(
                    self.plot.x_axis, self.plot.y_axis[i])
        except (ValueError, IndexError) as error:
            logging.error("Error processing serial data: %s", error)

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
        self.aboutbox.setWindowTitle("About")
        self.aboutbox.setWindowIcon(QtGui.QIcon(icon_logo))
        self.aboutbox.setText("<center></center><b>Tauno Serial Plotter</b><br/><br/>\
            More info: <a href ='https://github.com/taunoe/tauno-serial-plotter'>\
            github.com/taunoe/tauno-serial-plotter</a><br/><br/>\
            Version {}<br/><br/>\
            Tauno Erik<br/><br/>\
            2021-2026".format(VERSION))
        self.aboutbox.exec()

    def get_numbers(self, string):
        """
        Function to extract all the numbers from the given string
        https://www.regular-expressions.info/floatingpoint.html
        """
        numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+', string)
        return numbers
    
    def get_labels(self, string):
        """
        Function to extract all the labels from the given string
        """
        labels = re.findall(r'[-+]?[a-zA-Z]*\.?[a-zA-Z]+', string)
        return labels

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

    def closeEvent(self, event):
        """Stop background work before the window is destroyed."""
        if self.selected_port:
            self.settings.setValue("serial/port", self.selected_port)
        self.settings.setValue("serial/baudrate", self.selected_baudrate)
        self.settings.sync()
        self.port_scanner_thread.requestInterruption()
        self.port_scanner_thread.quit()
        self.port_scanner_thread.wait()
        if self.serial_thread.isRunning():
            QMetaObject.invokeMethod(
                self.serial_worker,
                "stop",
                Qt.ConnectionType.BlockingQueuedConnection)
        self.serial_thread.quit()
        self.serial_thread.wait()
        event.accept()

    #def mouseClickEvent(self, event):
        #print("clicked")

# END of class MainWindow --------------------------------------------

if __name__ == '__main__':
    window = MainWindow(app)
    window.show()

    exit_code = app.exec()
    sys.exit(exit_code)
