from scipy.signal import savgol_filter


import lmfit as lm
import numpy as np  
from photopeak_database import database

class Fitter():
    def __init__(self,peak_type,background_type, initial_guess_peak_amount, initial_guess_const):
        self.initial_guess_const = initial_guess_const
        if peak_type == 1:
            self.peak_model = lm.models.GaussianModel()
        elif peak_type == 2:
            self.peak_model = lm.models.PseudoVoigtModel()
        elif peak_type == 3:
            self.peak_model = lm.models.LorentzianModel()
        if (background_type==1):
            self.background_model = lm.Model(Fitter.sherley, independent_vars=['y'])
            
        elif (background_type==2):
            self.background_model = lm.models.LinearModel()

        elif (background_type==3):  
            self.background_model = lm.models.ConstantModel()

        self.model = self.peak_model + self.background_model
    def sherley(y, k,const):
        y_right = const
        y_temp = y - y_right  
        bg = []
        for i in range(len(y)):
            bg.append(np.sum(y_temp[i:]))
        return np.asarray([k * elem + y_right for elem in bg]) 
    def fit(self, ranges,spectrum, background_type):
        results = []
        for range in ranges:
            y = np.array(spectrum['Data'][spectrum['Energy'].between(range[0], range[1])])
            x = np.array(spectrum['Energy'][spectrum['Energy'].between(range[0], range[1])])
            params = self.peak_model.guess(y, x=x)
            if(background_type==1):
                params.add('const', value=self.initial_guess_const)
                params.add('k', value=0.1)
                fit = self.model.fit(y,y=y,x=x,params=params)
                
            elif(background_type==2):
                params.add('intercept', value=self.initial_guess_const)
                params.add('slope', value=0.1)
                fit = self.model.fit(y, x=x,params=params)
        
            background = self.background_model.eval(y=y,x=x,params=fit.params)
            counts =np.sum(self.model.eval(y=y,x=x,params=fit.params) - background)
            dely = fit.eval_uncertainty(sigma=1)
            delta_counts = counts - np.sum(self.model.eval(y=y,x=x,params=fit.params)+dely - background)
            results.append([fit,background,counts, delta_counts])
        return results


def convertToEnergy(x,calibration_coeff):
    y = calibration_coeff[2]*x**2 + calibration_coeff[1]*x + calibration_coeff[0]
    return y
def findclosestMatchingPeak(x):
    closed_peak_name = ["K",0]
    for element in database.keys():
        for i,photo_peak in enumerate(database[element]):
            if abs(photo_peak[0] - x ) < abs(database[closed_peak_name[0]][closed_peak_name[1]][0]-x):
                closed_peak_name = [element,i]
    if(abs(database[closed_peak_name[0]][closed_peak_name[1]][0]-x) > 20):
        return [None,0]
    return closed_peak_name

def subtractBackground(sepectrum,background):
        processed_spectrum = sepectrum.copy()
        processed_spectrum["Data"] = processed_spectrum["Data"] - background["Data"]

def amplify(spectrum_x,spectrum_y, factor):
    y = spectrum_y*(np.array(spectrum_x)**factor)
    return y
def filter(spectrum, f, polynomial_order):
    processed_spectrum = spectrum.copy()  
    if f > polynomial_order:
        processed_spectrum["Data"]= savgol_filter(processed_spectrum["Data"], f, polynomial_order)

    elif(f>0):
        processed_spectrum["Data"]= savgol_filter(processed_spectrum["Data"], f, f-1)
    else:
        return processed_spectrum
    return processed_spectrum