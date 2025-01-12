
from tkinter import * 
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from matplotlib.widgets import SpanSelector,RectangleSelector
import numpy as np
import os
from photopeak_database import database
from datetime import datetime
from Processing import amplify,findclosestMatchingPeak


class PlottingCanvas(tk.Frame):
    ax = None
    fig = None
    selected_ranges = []
    spectrum = None
    background = []
    zoomMode = False
    hoverline = None
    EnergyLabel = None
    closest_peak = None
    hoverMode =1
    scatter = False
    photo_peaks = []
    old_lim = []
    amplification = 0
    fits = []
    
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.fig = Figure(figsize=(16,7), dpi=100)
        self.ax = self.fig .add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, self)  
        button = Button(self, text="clear", command=self.clear)
        safeButton = Button(self, text="safe", command=self.safe)
        unzoombutton =  Button(self, text="unzoom", command=self.dezoom)
        scatterButton = Button(self, text="scatter", command=self.scatter_)
        self.old_lim = []
        self.scale = "linear"
        self.span = SpanSelector(
            self.ax,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            button=3,
            interactive=True,
            drag_from_anywhere=True
        )
        self.zoom_ = RectangleSelector(
            self.ax,
            self.zoom, useblit=True,
                                       button=[1],
                                       minspanx=5, minspany=5,
                                       spancoords='pixels',
                                       interactive=False
        )
        
        self.hoverHandler = self.canvas.mpl_connect('motion_notify_event', self.hover)
        
        self.canvas.mpl_connect('button_press_event', self.button_press)
        self.canvas.mpl_connect('key_press_event', self.span)
        self.canvas.get_tk_widget().grid(row=0,column=0,columnspan=20,rowspan=10)
        
        button.grid(row=11,column=10)
        unzoombutton.grid(row=11,column=11)
        safeButton.grid(row=11,column=12)
        scatterButton.grid(row=11,column=13)
    def scatter_(self):
        if(self.scatter == True):
            self.scatter = False
        else:
            self.scatter = True
        self.redraw()
    def safe(self):
        self.fig.savefig("spectrum"+datetime.today().strftime('%Y-%m-%d') + ".png",bbox_inches='tight')
    def button_press(self,event):
        if event.button == 2:
            if(self.hoverMode == 1):
                self.canvas.mpl_disconnect(self.hoverHandler)
                self.hoverMode = -1
            else:
                self.hoverMode = 1
                self.hoverHandler = self.canvas.mpl_connect('motion_notify_event', self.hover)
            
    def hover(self,event):
        if event.inaxes == self.ax:
            x = event.xdata
            y = event.ydata

            if(self.closest_peak in self.ax.lines):
                self.closest_peak.remove()
                self.closest_peakLabel.remove()
            self.closest_peak_ = findclosestMatchingPeak(x)
            
            if self.hoverline not in  self.ax.lines and self.closest_peak_[0] == None:
                self.hoverline = self.ax.axvline(x=x, color="r", linestyle="--",alpha=0.3)
                self.countsLabel = self.ax.text(x*1, y*1, f"{y:.2f} counts", color="black")    
                self.EnergyLabel = self.ax.text(x-10, self.ax.get_ylim()[1]*1.02, f"{x:.2f} keV", color="black",rotation=90)
            elif(self.closest_peak_[0] == None):
                self.hoverline.set_xdata([x])
                self.EnergyLabel.set_x(x-10)
                self.countsLabel.set_x(x*1.02)
                self.countsLabel.set_text(f"{y:.2f}")
                self.countsLabel.set_y(y*1.02)
                self.EnergyLabel.set_text(f"{x:.2f} keV")
            else:
                if(self.hoverline in self.ax.lines):
                    self.hoverline.remove()
                    self.EnergyLabel.remove()
                    self.countsLabel.remove()
                x_peak = database[self.closest_peak_[0]][self.closest_peak_[1]][0]
                self.closest_peak = self.ax.axvline(x=x_peak, color="green", linestyle="--",alpha=0.5)
                self.closest_peakLabel =  self.ax.text(x_peak-20, self.ax.get_ylim()[1]*1.02, str(database[self.closest_peak_[0]][self.closest_peak_[1]][1]), rotation=90)
            self.canvas.draw()
        else:
            if(self.hoverline in self.ax.lines or self.closest_peak in self.ax.lines):
                if(self.hoverline in self.ax.lines):
                    self.hoverline.remove()
                    self.EnergyLabel.remove()
                    self.countsLabel.remove()
                elif(self.closest_peak in self.ax.lines):
                    self.closest_peak.remove()
                    self.closest_peakLabel.remove()
                self.canvas.draw()
    
    def zoom(self, eclick, erelease):
        x0, y0 = eclick.xdata, eclick.ydata
        x1, y1 = erelease.xdata, erelease.ydata
        self.old_lim.append([self.ax.get_ylim(),self.ax.get_xlim()])
        self.ax.set_xlim(x0, x1)
        self.ax.set_ylim(y0, y1)
        self.canvas.draw()
        
    def dezoom(self):
        self.ax.set_xlim(self.old_lim[-1][1])
        self.ax.set_ylim(self.old_lim[-1][0])
        self.old_lim.pop()
        self.canvas.draw()
    def setZoomMode(self):
        if(self.zoomMode == True):
            self.reactangleSelector.set_active(True)
            self.span.set_active(False)
            self.span.set_visible(False)
            self.setZoomMode = False
        else:
            self.reactangleSelector.set_active(False)
            self.span.set_active(True)
            self.setZoomMode = True
    def setscale(self, scale):
        self.scale=scale
    def onselect(self,vmin, vmax):
        self.selected_ranges.append([vmin, vmax])
        self.redraw()
        self.span.set_visible(False)
        
    def clear(self):
        self.set_range([])
        self.set_fits([])
        self.set_spectrum(self.set_spectrum)
        self.redraw()

    def addFits(self, fits,range,amplification):
        for i,fit in enumerate(fits):
            self.ax.plot(self.spectrum["Energy"][self.spectrum["Energy"].between(range[i][0],range[i][-1])], fit.best_fit*self.spectrum["Energy"][self.spectrum["Energy"].between(range[i][0],range[i][-1])]**amplification, 'r-')
        self.canvas.draw()
    
    def set_amplification(self, amplification):
        self.amplification = amplification
        
    def set_range(self,range):
        self.selected_ranges = range
        
    def set_background(self,background):
        self.background = background
        
    def set_spectrum(self,spectrum):
        self.spectrum = spectrum
        
    def set_fits(self,fits):
        self.fits = fits
        
    def set_photo_peaks(self,photo_peaks):
        self.photo_peaks = photo_peaks
        
    def set_spectrum(self,spectrum):
        self.spectrum = spectrum
        
    def redraw(self):
        
        os.system('cls')
        self.ax.clear()   

        self.drawSpectrum()
        self.drawBackground()
        self.drawSelectedRanges()
        self.drawFits()
        self.drawPeaks()

        self.ax.set_xlabel('Energy [keV]')
        self.ax.set_ylabel('Counts')
        self.ax.grid()
        self.ax.set_yscale(self.scale)
        self.ax.set_xlim(0, self.ax.get_xlim()[1])
        self.canvas.draw()
        
    def drawSpectrum(self):
        energy = self.spectrum['Energy']
        counts = self.spectrum['Data']
        amplified_counts  = amplify(energy,counts,self.amplification)
        
        if(self.scatter == True):
            self.ax.scatter(energy, amplified_counts)
        else:
            self.ax.plot(energy, amplified_counts,color="orange")
            self.ax.fill_between(energy,0,amplified_counts,alpha=0.5,color="orange")#self.ax.plot(energy, amplified_counts)
            
            
    def drawBackground(self):
        if(type(self.background) == pd.DataFrame):
            self.ax.plot(self.background["Energy"],amplify(self.background["Energy"],self.background["Data"],self.amplification), color="tab:green",linestyle="dashed")
        
    def drawSelectedRanges(self):
        for range in self.selected_ranges:
            y = self.spectrum['Data'][self.spectrum['Energy'].between(range[0], range[1])]
            x=np.linspace(range[0],range[1],len(y))
            self.ax.fill_between(x=x, y1=np.zeros(len(y)),y2= amplify(x,y,self.amplification), color="tab:orange",alpha=0.2)
    def drawFits(self):
        for i,fit_ in enumerate(self.fits):
            fit = fit_[0]
            background = fit_[1]
            energy = self.spectrum["Energy"][self.spectrum["Energy"].between(self.selected_ranges[i][0],self.selected_ranges[i][-1])]
            fitted_curve =  amplify(energy,fit.best_fit,self.amplification)
            background_y = amplify(energy,background,self.amplification)
            self.ax.plot(energy, background_y, color='r',linestyle="dashed",alpha=0.5)

            self.ax.fill_between(energy, background_y, fitted_curve, color="tab:green",alpha=0.2)
            self.ax.plot(energy, fitted_curve, 'r-',alpha=0.5)
    def drawPeaks(self):
        for photo_peak in self.photo_peaks:
            for peak in photo_peak:
                self.ax.axvline(x=float(peak[0]), color="r", linestyle="--",alpha=0.3)
                self.ax.text(peak[0]-20, self.ax.get_ylim()[1]*1.02, str(peak[1]), rotation=90)