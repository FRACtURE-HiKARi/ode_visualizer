'''
Ordinary Differential Equation Visualizer
Authors:
    @FRACtURE-HiKARi
    @EIA2024
Date:
    Mar 2025
'''

try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError:
    print("Please install package numpy and matplotlib.")

from matplotlib import widgets
from matplotlib.axes import Axes
from typing import Any
import matplotlib.backend_bases as mpl_backend
from numpy import sin, cos, tan, arcsin, arccos, arctan, exp, log
from functools import partial

def within_range(x0, llim, hlim):
    return x0 > llim and x0 < hlim

class visualizer:
    w = 6
    h = 6
    x0 = 0
    y0 = 0
    gridsize = 0.2
    scroll_sensitivity = 0.1
    initial_points = []
    dragging = False
    drag_start = tuple()
    euler_step = 0.01
    graph_color = '#1f77b4'

    K: np.vectorize

    def __init__(self):
        self.fig = plt.figure(num=1, figsize=(self.w, self.h))
        self.ax: Axes = self.fig.add_axes([0.1, 0.15, 0.8, 0.8])
        self.fig.suptitle('Direction Field & IVP Solution')
        self.axbox: Axes = self.fig.add_axes([0.2, 0.05, 0.6, 0.06])
        self.textbox = widgets.TextBox(self.axbox, "dy/dx=:", initial="y**2 - y*3 + 1")
        self.textbox.on_submit(partial(self.submit_callback))
        helpbox = self.fig.add_axes([0.8, 0.05, 0.1, 0.06])
        self.help_button = widgets.Button(helpbox, "Help")
        self.help_button.on_clicked(partial(self.help_callback))
        self.fig.canvas.mpl_connect('button_press_event', partial(self.button_press_callback))
        self.fig.canvas.mpl_connect('button_release_event', partial(self.button_release_callback))
        self.fig.canvas.mpl_connect('motion_notify_event', partial(self.motion_callback))
        self.fig.canvas.mpl_connect('scroll_event', partial(self.scroll_callback))
        self.fig.canvas.mpl_connect('close_event', partial(self.close_callback))
        self.submit_callback("y**2 - y*3 + 1")

    def start_event_loop(self):
        plt.show()

    def get_edges(self):
        xm = self.x0 - self.w/2
        xM = self.x0 + self.w/2
        ym = self.y0 - self.h/2
        yM = self.y0 + self.h/2
        return xm, xM, ym, yM

    def resize_axes(self, step):
        self.h *= 1 - self.scroll_sensitivity * step
        self.w *= 1 - self.scroll_sensitivity * step
        self.euler_step *= 1 - self.scroll_sensitivity * step
        self.update_graph()

    def update_graph(self):
        self.draw_quiver(*self.get_edges())

    def draw_quiver(self, xm, xM, ym, yM):
        self.ax.cla()
        X = np.linspace(xm, xM, int((xM - xm) / self.gridsize))
        Y = np.linspace(ym, yM, int((yM - ym) / self.gridsize))
        X, Y = np.meshgrid(X, Y)

        try:
            T = np.arctan(self.K(X, Y))
        except SyntaxError:
            self.textbox.set_val("INVALID INPUT")
        U = np.cos(T)
        V = np.sin(T)
        self.ax.quiver(X, Y, U, V)
        for x_and_y in self.initial_points:
            self.explicitEuler(*x_and_y)
        plt.draw()

    def explicitEuler(self, x0, y0):
        xm, xM, ym, yM = self.get_edges()
        if within_range(x0, xm, xM) and within_range(y0, ym, yM):
            self.ax.scatter(x0, y0, s=16, c=self.graph_color)
        for _step in [self.euler_step, -self.euler_step]:
            x = x0
            y = y0
            xs = []
            ys = []
            while within_range(x, xm, xM) and within_range(y, ym, yM):
                xs.append(x)
                ys.append(y)
                y += _step * self.K(x, y)
                x += _step
            self.ax.plot(xs, ys, c=self.graph_color)
        plt.draw()

    def submit_callback(self, text):
        self.K = np.vectorize(lambda x, y: eval(text))
        self.update_graph()

    def button_press_callback(self, event: mpl_backend.MouseEvent):
        if event.inaxes == self.ax:
            if event.button == 1:  # Left click
                if event.dblclick:
                    self.initial_points.append((event.xdata, event.ydata))
                    self.explicitEuler(event.xdata, event.ydata)
                else:
                    self.dragging = True
                    self.drag_start = (event.xdata, event.ydata)

            elif event.button == 3:  # Right click
                self.initial_points.clear()
                self.update_graph()

    def button_release_callback(self, event: mpl_backend.MouseEvent):
        if event.inaxes == self.ax and event.button == 1:
            self.dragging = False
    
    def motion_callback(self, event: mpl_backend.MouseEvent):
        if not self.dragging:
            return
        xs, ys = self.drag_start
        self.x0 += xs - event.xdata
        self.y0 += ys - event.ydata
        self.update_graph()

    def scroll_callback(self, event: mpl_backend.MouseEvent):
        if event.inaxes == self.ax:
            if event.button == 'up' or 'down':
                self.resize_axes(event.step)

    def help_callback(self, event: mpl_backend.Event):
        if not plt.fignum_exists(2):
            help_fig = plt.figure(num=2, figsize=(6, 1))
            help_ax: Axes = help_fig.add_axes([0, 0, 1, 1])
            help_ax.text(0.1, 0.15, 
"\
Type in ODEs\n\
double click to add initial point\n\
right click to clear solutions\n\
hold and drag to move canvas\n\
This will re-draw the solutions so that clear before drag is recommended\
"
            )
            help_fig.show()

    def close_callback(self, event: mpl_backend.CloseEvent):
        if not plt.fignum_exists(1):
            plt.close('all')
            