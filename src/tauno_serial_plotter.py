#!/usr/bin/env python3
"""
    File:    Tauno-Serial-Plotter.py
    Author:  Tauno Erik
    Started: 07.03.2020
"""
import sys
import logging
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import (Qt, QMetaObject, QThread, pyqtSignal,
                          pyqtSlot)
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QMessageBox
try:
    from .parser import parse_numbers
    from .app_model import AppModel, ConnectionState
    from .serial_workers import PortScanner, SerialWorker
    from .theme import create_theme
    from .widgets import Controls, Plot, create_styles
except ImportError:
    from parser import parse_numbers
    from app_model import AppModel, ConnectionState
    from serial_workers import PortScanner, SerialWorker
    from theme import create_theme
    from widgets import Controls, Plot, create_styles

VERSION = '1.21.5'
# Set debug level
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.CRITICAL)




class MainWindow(QWidget):
    """
    Define MainWindow
    """
    serial_connect_requested = pyqtSignal(str, int)
    serial_disconnect_requested = pyqtSignal()

    def __init__(self, app, theme=None, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.app = app
        self.theme = theme or create_theme(app)
        self.styles = create_styles(self.theme)
        self.model = AppModel()
        self.plot_exist = False
        self.is_fullscreen = False

        self.init_ui()
        self.center_mainwindow()
        self.horizontal_layout = QVBoxLayout(self) #QHBoxLayout(self)

        # Controls
        self.controls = Controls(parent=self, theme=self.theme)
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

        # Control selct and button calls
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
            f"QWidget#mainWindow {{ background-color: {self.theme.colors['dark']}; }}")
        self.setWindowTitle("Tauno Serial Plotter")
        self.setWindowIcon(QtGui.QIcon(self.theme.icons["logo"]))
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
        logging.debug("self.connection_state %s", self.model.connection_state.name)

        before_selected_port = self.model.selected_port
        logging.debug("before_selected_port %s", before_selected_port)

        if self.plot_exist and self.model.connection_state == ConnectionState.CONNECTED:
            return

        self.model.ports = ports
        self.controls.select_port.blockSignals(True)
        self.controls.select_port.clear()
        self.controls.select_port.addItems(self.model.ports)

        if self.model.ports:
            index = (self.model.ports.index(before_selected_port)
                     if before_selected_port in self.model.ports else 0)
            self.controls.select_port.setCurrentIndex(index)
            self.model.selected_port = self.model.ports[index]
        else:
            self.model.selected_port = ''
        self.controls.select_port.blockSignals(False)

    def init_baudrates(self):
        self.controls.select_baud.addItems(self.model.BAUDRATES)
        self.controls.select_baud.setCurrentIndex(
            self.model.BAUDRATES.index(self.model.selected_baudrate))

    def selected_port_changed(self, i):
        if i < 0 or i >= len(self.model.ports):
            return
        self.model.selected_port = self.model.ports[i]
        logging.info("Main selected port changed:")
        logging.info(self.model.selected_port)

    def selected_baud_changed(self, i):
        self.model.selected_baudrate = self.model.BAUDRATES[i]
        logging.info("Main selected baud index changed:")
        logging.info(self.model.selected_baudrate)
        self.model.plot.equalize()
        if self.model.connection_state == ConnectionState.CONNECTED:
            self.request_serial_connection()

    def time_scale_changed(self):
        logging.debug("Timescale changed!")
        new_value = int(self.controls.time_scale_spin.value())
        self.controls.update_timescale(new_value)
        #print("New Timescale value = {}".format(self.controls.plot_timescale))

        self.model.update_data_size(new_value)

    def connect_stop(self):
        """ Connected or Pause button press? """
        if self.model.connection_state in (
                ConnectionState.DISCONNECTED, ConnectionState.ERROR):
            logging.debug('--> Connect Button.')
            self.connect()
        elif self.model.connection_state in (
                ConnectionState.CONNECTING, ConnectionState.CONNECTED):
            logging.debug('--> Pause Button.')
            self.disconnect()


    def connect(self):
        """ When we press button Connect. """
        self.model.set_connection_state(ConnectionState.CONNECTING)
        # Change button txt
        self.controls.connect.setText('Connecting...')
        # Disable button
        self.controls.select_port.setEnabled(False)
        self.controls.select_baud.setEnabled(False)
        # Change button style
        self.controls.select_port.setStyleSheet(self.styles["dropdown_style_disabled"])
        self.controls.select_baud.setStyleSheet(self.styles["dropdown_style_disabled"])

        self.request_serial_connection()

    def disconnect(self):
        """ When we press Pause button """
        self.serial_disconnect_requested.emit()
        self.model.set_connection_state(ConnectionState.DISCONNECTED)
        # Change button txt
        self.controls.connect.setText('Connect')
        # Enable buttons
        self.controls.select_port.setEnabled(True)
        self.controls.select_baud.setEnabled(True)
        # Change button style
        self.controls.select_port.setStyleSheet(self.styles["dropdown_style"])
        self.controls.select_baud.setStyleSheet(self.styles["dropdown_style"])
        self.controls.btn_clear.setEnabled(False)
        self.controls.btn_clear.setStyleSheet(self.styles["btn_icon_style_disabled"])

    def request_serial_connection(self):
        self.serial_connect_requested.emit(
            self.model.selected_port, int(self.model.selected_baudrate))

    @pyqtSlot()
    def serial_disconnected(self):
        if self.model.connection_state != ConnectionState.DISCONNECTED:
            self.model.set_connection_state(ConnectionState.DISCONNECTED)

    @pyqtSlot(int, list)
    def serial_connected(self, number_of_lines, labels):
        if self.model.connection_state != ConnectionState.CONNECTING:
            logging.debug("Ignoring stale serial connection result")
            return
        self.model.configure_plot(number_of_lines, labels)
        if not self.plot_exist:
            self.plot = Plot(
                self.model.plot.number_of_lines,
                self.model.labels,
                theme=self.theme)
            self.horizontal_layout.addWidget(self.plot)
            self.plot_exist = True
        self.model.set_connection_state(ConnectionState.CONNECTED)
        self.controls.connect.setText('Pause')
        self.controls.btn_clear.setEnabled(True)
        self.controls.btn_clear.setStyleSheet(self.styles["btn_icon_style"])

    @pyqtSlot(str)
    def serial_connection_failed(self, error):
        logging.error("Serial connection failed: %s", error)
        self.model.set_connection_state(ConnectionState.ERROR)
        self.controls.connect.setText('Connect')
        self.controls.select_port.setEnabled(True)
        self.controls.select_baud.setEnabled(True)
        self.controls.select_port.setStyleSheet(self.styles["dropdown_style"])
        self.controls.select_baud.setStyleSheet(self.styles["dropdown_style"])
        self.controls.btn_clear.setEnabled(False)
        self.controls.btn_clear.setStyleSheet(self.styles["btn_icon_style_disabled"])
        QMessageBox.critical(
            self,
            "Serial connection failed",
            error or "Unable to connect to the selected serial port.")

    @pyqtSlot(str)
    def handle_serial_data(self, incoming_data):
        if (not self.plot_exist
                or self.model.connection_state != ConnectionState.CONNECTED):
            return
        try:
            numbers = parse_numbers(incoming_data)

            self.model.add_data(numbers)
            for i in range(self.model.plot.number_of_lines):
                self.plot.data_lines[i].setData(
                    self.model.plot.x_axis, self.model.plot.y_axis[i])
        except (ValueError, IndexError) as error:
            logging.error("Error processing serial data: %s", error)

    def clear_data(self):
        """ Button clear data """
        logging.debug('--> Clear data Button.')
        # delete existing data
        size = len(self.model.plot.x_axis)
        logging.debug("x_axis: %s", size)
        self.model.clear_data()

    def about(self):
        """ Button About """
        logging.debug('--> About Button.')
        self.aboutbox.setWindowTitle("About")
        self.aboutbox.setWindowIcon(QtGui.QIcon(self.theme.icons["logo"]))
        self.aboutbox.setText("<center></center><b>Tauno Serial Plotter</b><br/><br/>\
            More info: <a href ='https://github.com/taunoe/tauno-serial-plotter'>\
            github.com/taunoe/tauno-serial-plotter</a><br/><br/>\
            Version {}<br/><br/>\
            Tauno Erik<br/><br/>\
            2021-2026".format(VERSION))
        self.aboutbox.exec()

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
        """ F11 on/off fullscreen"""
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
        self.model.save_settings()
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

def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    if hasattr(Qt, 'AA_Use96Dpi'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_Use96Dpi, True)
    app = QApplication(sys.argv)
    theme = create_theme(app)
    window = MainWindow(app, theme=theme)
    window.show()

    exit_code = app.exec()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
