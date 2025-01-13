
from tkinter import * 
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from tkinter import filedialog
import pandas as pd
import sys
import os
from photopeak_database import database
import  tkinter.scrolledtext as scrolledtext
from PlotWidget import PlottingCanvas
from Processing import filter,Fitter,convertToEnergy	
import json
from PeriodicTable import PeriodicTable


class Consoleredirect:
    def __init__(self, console):
        self.console = console
    def write(self, msg):
        self.console.insert(tk.END, msg)
        self.console.see(tk.END)
    def flush(self):
        pass             
        
class Config():
    calibration_coeff = [5.43647427623087,2.37359149302354,0.000357981437088942]
    background = None
    def __init__(self,config_file):
        self.config_file = config_file
    def load_config(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            self.calibration_coeff = config["calibration_coeff"]
            self.background = config["background"]
        f.close()
    def save_config(self):
        config = {
            "calibration_coeff": self.calibration_coeff,
            "background": self.background   
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        f.close()
        
    def get_calibration_coeff(self):
        return self.calibration_coeff
    def set_calibration_coeff(self,calibration_coeff):
        self.calibration_coeff = calibration_coeff
    def set_background(self,background):
        self.background = background
    def get_background(self):
        return self.background
    
    
class gui():
    selected_elements = []
    results = []
    photo_peaks = []
    og_spectrum = None
    processed_spectrum = None
    backgroundStatus = 1
    plotter = None
    config = None
    def __init__(self):
        self.root = Tk()
        
        self.config = Config(os.getcwd()+"\\config.json")
        self.config.load_config()
        self.periodicTable = PeriodicTable(self.root,self.new_Element_selected)
        self.root.configure(background='white')
        self.root.geometry("1920x1080")
        self.plotter = PlottingCanvas(self.root)
        self.plotter.configure(background='white')
        self.plotter.grid(row=0, column=0)
        button_frame = Frame(self.root)
        button_frame.grid(row=1, column=0)
        fit_button = Button(button_frame, text="Fit", command=self.doFIt)
        self.amplificationSlider = Scale(button_frame, from_=0, to=100, orient=HORIZONTAL)
        self.amplificationSlider.bind("<ButtonRelease-1>", self.amplify_callback)

        self.filterSlider = Scale(button_frame, from_=0, to=100, orient=HORIZONTAL)
        self.filterSlider.bind("<ButtonRelease-1>", self.filter_callback)

        self.filterSlider.grid(row=0, column=3)
        self.amplificationSlider.grid(row=1, column=3)
        fit_button.grid(row=6, column=0)
        
        self.PeakTypeLabel = Label(button_frame, text="Peak Type").grid(row=0, column=1)
        self.BackgroundLabel = Label(button_frame, text="Background Type").grid(row=0, column=0)
        
        self.AmplificationLabel = Label(button_frame, text="Amplification:").grid(row=1, column=2)
        self.amplificationLabel = Label(button_frame, text="Filter:").grid(row=0, column=2)
        self.toggleBackgroundButton = Button(button_frame, text="Toggle Background",command=self.toggleBackground).grid(row=2, column=2)
        self.switchScaleButton = Button(button_frame, text="Switch Scale",command=self.switchscale).grid(row=2, column=3)
        
        self.background_ = IntVar()
        self.shirleyButton =  Radiobutton (button_frame, text="Shirley -Background", variable=self.background_ ,value=1).grid(row=0, sticky=W)
        self.LinearButton =  Radiobutton (button_frame, text="Linear-Background", variable=self.background_ ,value=2).grid(row=1, sticky=W)
        self.ConstantButton = Radiobutton (button_frame, text="Constant-Background", variable=self.background_ ,value=3).grid(row=2, sticky=W)
        
        self.peaktype = IntVar()
        self.gaussianButton =  Radiobutton (button_frame, text="Gaussian", variable=self.peaktype,value=1).grid(row=0, column=1, sticky=W)
        self.pseudoVoigtButton =  Radiobutton (button_frame, text="Pseudo-Voigt", variable=self.peaktype,value=2).grid(row=1, column=1, sticky=W)
        self.lorenzian =  Radiobutton (button_frame, text="Lorentz", variable=self.peaktype,value=3).grid(row=2, column=1, sticky=W)  
        
        self.a0 = StringVar()
        self.a1 = StringVar()
        self.a2 = StringVar()
        
        self.a0.set(str(self.config.get_calibration_coeff()[0]))
        self.a1.set(str(self.config.get_calibration_coeff()[1]))
        self.a2.set(str(self.config.get_calibration_coeff()[2]))
        
        self.a0Label = Label(button_frame, text="a0:").grid(row=0, column=4)
        self.a0Entry = Entry(button_frame, textvariable=self.a0,).grid(row=0, column=5)
        self.a1Label = Label(button_frame, text="a1:").grid(row=1, column=4)
        self.a1Entry = Entry(button_frame, textvariable=self.a1).grid(row=1, column=5)
        self.a2Label = Label(button_frame, text="a2:").grid(row=2, column=4)
        self.a2Entry = Entry(button_frame, textvariable=self.a2).grid(row=2, column=5)
    
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0) 
        elementmenu = Menu(menubar, tearoff=0)
        elementmenu.add_command(label="Periodic Table", command=lambda: self.periodicTable.show(self.selected_elements))
        filemenu.add_command(label="Open", command=self.open)
        filemenu.add_command(label="Open Background", command=self.openBackground)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Elements", menu=elementmenu)
        self.root.config(menu=menubar)
        console_frame = Frame(self.root)
        console_frame.grid(row=0, column=1,rowspan=300,columnspan=2)
        self.console = scrolledtext.ScrolledText(console_frame, undo=True,width=60,height=60, wrap="word")
        self.console['font'] = ('Times New Roman', '10') 
        self.console.grid()
        self.console.focus()
        redirected = Consoleredirect(self.console)
        sys.stdout = redirected
        
        if(self.config.get_background() != None):
            self.background = pd.read_csv(self.config.get_background(), sep=',')
            
            self.background["Data"] = self.background["Data"][:-1]
            self.background["Energy"]  = convertToEnergy(self.background["Energy"][:-1],self.config.get_calibration_coeff())
            self.plotter.set_background(self.background)
            print("Background loaded")
        
        
        self.root.mainloop()
        
    def toggleBackground(self):
        if self.backgroundStatus == 1:
            self.processed_spectrum = self.subtractBackground()
            self.plotter.set_background([])
            self.plotter.redraw()
            self.backgroundStatus = 2
        elif self.backgroundStatus == 2:
            self.processed_spectrum = self.og_spectrum.copy()
            self.plotter.set_background([])
            self.plotter.set_spectrum(self.processed_spectrum)
            self.backgroundStatus = 3
        else:
            self.plotter.set_background(self.background)
            self.backgroundStatus = 1
        
        self.plotter.redraw()
    
    def switchscale(self):
        if self.plotter.scale == "linear":
            self.plotter.setscale("log")
        else:
            self.plotter.setscale("linear")
        self.plotter.redraw()
    
    def openBackground(self):
        spectrum_path = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
        self.background = pd.read_csv(spectrum_path, sep=',')
        self.config.set_background(spectrum_path)
        self.background["Data"] = self.background["Data"][:-1]
        self.background["Energy"]  = convertToEnergy(self.background["Energy"][:-1],self.config.get_calibration_coeff())
        self.plotter.set_background(self.background)
        self.config.save_config()
        self.plotter.redraw()
    def subtractBackground(self):
        self.processed_spectrum["Data"] = self.processed_spectrum["Data"] - self.background["Data"]
        self.plotter.set_spectrum(self.processed_spectrum)
        self.plotter.redraw()
    def new_Element_selected(self,element):
        if element not in self.selected_elements:
            self.selected_elements.append(element)
        else:
            self.selected_elements.remove(element)
            self.photo_peaks.remove(database[element])
            
        for element in self.selected_elements:
            if element in database.keys():     
                self.photo_peaks.append(database[element])
        self.plotter.set_photo_peaks(self.photo_peaks)
        self.plotter.redraw()
    def filter_callback(self,event):
        f = self.filterSlider.get()
        self.processed_spectrum = filter(self.og_spectrum,f,5)
        self.plotter.set_spectrum(self.processed_spectrum)
        self.plotter.redraw()
    def amplify_callback(self,event):
        self.plotter.ax.clear()
        amplification = self.amplificationSlider.get() /50
        self.plotter.set_amplification(amplification)
        self.plotter.redraw()
        
    def open(self):
        spectrum_path =filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
        # "F:\\Nextcloud_new\\Projects\\radiacode\\software\\Granit\\2025-01-06  17-56-15.csv"
        self.og_spectrum = pd.read_csv(spectrum_path, sep=',')
        self.og_spectrum["Data"] = self.og_spectrum["Data"][:-1]
        self.og_spectrum["Energy"]  = convertToEnergy(self.og_spectrum["Energy"][:-1],self.config.get_calibration_coeff())
        self.og_spectrum.to_csv("test.csv", sep='\t')
        self.processed_spectrum = self.og_spectrum.copy()
        
        self.plotter.set_spectrum(self.og_spectrum)
        self.plotter.redraw()

    def doFIt(self):
        fitter = Fitter(self.peaktype.get(),self.background_.get(), 0, 0)
        results= fitter.fit(self.plotter.selected_ranges, self.processed_spectrum, self.background_.get())
        self.console.delete("1.0","end")
        for i,result in enumerate(results):
            print("Fit for range: ", self.plotter.selected_ranges[i], "eV")
            print(result[0].fit_report())
            print("Area: ", result[2] ,"+- ", result[3],"eV*counts")
            print("\n\n")
        self.plotter.set_fits(results)
        self.plotter.redraw()    
        