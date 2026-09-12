"""Reusable plot and control widgets for Tauno Serial Plotter."""
import logging
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget
import pyqtgraph as pg

def create_styles(theme):
    colors = theme.colors
    icon_minus = theme.icons["minus"]
    icon_plus = theme.icons["plus"]
    icon_arrow_down = theme.icons["arrow_down"]
    FONTSIZE = '16px'
    BORDER_RADIUS = '5px'
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
        color: {colors['hall']};
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
    return {
        "btn_icon_style": btn_icon_style,
        "btn_icon_style_disabled": btn_icon_style_disabled,
        "btn_style": btn_style,
        "btn_style_disabled": btn_style_disabled,
        "label_style": label_style,
        "Qinfo_text_style": Qinfo_text_style,
        "dropdown_style": dropdown_style,
        "dropdown_style_disabled": dropdown_style_disabled,
        "QDoubleSpinBox_style": QDoubleSpinBox_style,
    }

class Plot(pg.GraphicsLayoutWidget):
    """ Plot definition """
    def __init__(self, nr_plot_lines='1', labels=["sensor1"], theme=None):
        super(Plot,self).__init__(parent=None)
        plot_colors = theme.plot_colors if theme else []
        if theme:
            pg.setConfigOptions(antialias=True)
            pg.setConfigOption("background", theme.colors["dark"])
            pg.setConfigOption("foreground", theme.colors["foreground"])

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
    def __init__(self, parent=None, theme=None):
        super(Controls, self).__init__(parent=parent)
        styles = create_styles(theme)
        icons = theme.icons

        # Plot time scale == data visible area size
        self.plot_timescale = 400 # default
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
        self.baud_label.setStyleSheet(styles["label_style"])
        # Select Baud
        self.select_baud = QtWidgets.QComboBox(parent=self)
        self.menu_top.addWidget(self.select_baud)
        self.select_baud.setStyleSheet(styles["dropdown_style"])
        self.select_baud.setFixedWidth(100)
        self.select_baud.setEditable(True)
        self.select_baud.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        

        # Label Port
        self.device_label = QLabel(self)
        self.menu_top.addWidget(self.device_label)
        self.device_label.setText("Port:")
        self.device_label.setStyleSheet(styles["label_style"])
        # Select Port
        self.select_port = QtWidgets.QComboBox(parent=self)
        self.menu_top.addWidget(self.select_port)
        self.select_port.setStyleSheet(styles["dropdown_style"])
        self.select_port.setFixedWidth(150)

        # Button Connect
        self.connect = QtWidgets.QPushButton('Connect', parent=self)
        self.menu_top.addWidget(self.connect)
        self.connect.setFixedWidth(100)
        self.connect.setStyleSheet(styles["btn_style"])

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
        self.time_scale_txt.setStyleSheet(styles["label_style"])
        ## SpinBox
        self.time_scale_spin = QtWidgets.QDoubleSpinBox()
        self.time_scale_spin.setSingleStep(1)
        self.time_scale_spin.setDecimals(0)
        self.time_scale_spin.setFixedWidth(120)
        self.time_scale_spin.setMaximum(self.plot_timescale_max)
        self.time_scale_spin.setMinimum(self.plot_timescale_min)
        self.time_scale_spin.setValue(self.plot_timescale)
        self.menu_left.addWidget(self.time_scale_spin)
        self.time_scale_spin.setStyleSheet(styles["QDoubleSpinBox_style"])


        self.btn_clear = QtWidgets.QPushButton()
        self.btn_clear.setIcon(QtGui.QIcon(icons["clean"]))
        self.btn_clear.setIconSize(QtCore.QSize(13,16))
        self.btn_clear.setFixedWidth(30)
        self.btn_clear.setStyleSheet(styles["btn_icon_style_disabled"])
        self.btn_clear.setEnabled(False)

        self.menu_left.addWidget(self.btn_clear)

        # Button: About
        self.about = QtWidgets.QPushButton(
            icon=QtGui.QIcon(icons["about"]),
            text='',
            parent=self)
        self.menu_left.addWidget(self.about)
        self.about.setFixedWidth(30)
        self.about.setStyleSheet(styles["btn_icon_style"])

        self.top_menu_row.addLayout(self.menu_left)

    def update_timescale(self, new_value):
        """ Assign new value. """
        self.plot_timescale = new_value

    def resizeEvent(self, event):
        """ If we resize main window. """
        super(Controls, self).resizeEvent(event)


# END of class Controls ----------------------------------------
