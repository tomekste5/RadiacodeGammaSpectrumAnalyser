import tkinter as tk

class PeriodicTable(tk.Toplevel):
    def __init__(self, parent,callback):
        self.parent = parent
        self.callback = callback
        self.elements_ = [
            ["H", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "","",  "He"],
            ["Li", "Be", "", "", "", "", "", "", "", "", "", "","",  "B", "C", "N", "O", "F", "Ne"],
            ["Na", "Mg", "", "", "", "", "", "", "", "", "", "","","","Al", "Si", "P", "S", "Cl", "Ar"],
            ["K", "Ca", "Sc","", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr"],
            ["Rb", "Sr", "Y","", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe"],
            ["Cs", "Ba", "La","siehe\nunten", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn"],
            ["Fr", "Ra", "Ac","siehe\nunten", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"],
            ["", "","", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "","", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "","", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"],
            ["", "","", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
            ]
        self.elements = [
            ["1\nH", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "2\nHe"],
            ["3\nLi", "4\nBe", "", "", "", "", "", "", "", "", "", "","", "5\nB", "6\nC", "7\nN", "8\nO", "9\nF","10\nNe"],
            ["11\nNa", "12\nMg", "", "", "", "", "", "", "", "", "", "", "", "13\nAl", "14\nSi", "15\nP", "16\nS", "17\nCl", "18\nAr"],
            ["19\nK", "20\nCa", "21\nSc", "", "22\nTi", "23\nV", "24\nCr", "25\nMn", "26\nFe", "27\nCo", "28\nNi", "29\nCu", "30\nZn", "31\nGa", "32\nGe", "33\nAs", "34\nSe", "35\nBr", "36\nKr"],
            ["37\nRb", "38\nSr", "39\nY", "", "40\nZr", "41\nNb", "42\nMo", "43\nTc", "44\nRu", "45\nRh", "46\nPd", "47\nAg", "48\nCd", "49\nIn", "50\nSn", "51\nSb", "52\nTe", "53\nI", "54\nXe"],
            ["55\nCs", "56\nBa", "57\nLa", "58-71\nsiehe\nunten", "72\nHf", "73\nTa", "74\nW", "75\nRe", "76\nOs", "77\nIr", "78\nPt", "79\nAu", "80\nHg", "81\nTl", "82\nPb", "83\nBi", "84\nPo", "85\nAt", "86\nRn"],
            ["87\nFr", "88\nRa", "89\nAc", "90-103\nsiehe\nunten", "104\nRf", "105\nDb", "106\nSg", "107\nBh", "108\nHs", "109\nMt", "110\nDs", "111\nRg", "112\nCn", "113\nNh", "114\nFl", "115\nMc", "116\nLv", "117\nTs", "118\nOg"],
            ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "58\nCe", "59\nPr", "60\nNd", "61\nPm", "62\nSm", "63\nEu", "64\nGd", "65\nTb", "66\nDy", "67\nHo", "68\nEr", "69\nTm", "70\nYb", "71\nLu"],
            ["", "", "", "90\nTh", "91\nPa", "92\nU", "93\nNp", "94\nPu", "95\nAm", "96\nCm", "97\nBk", "98\nCf", "99\nEs", "100\nFm", "101\nMd", "102\nNo", "103\nLr"]
        ]
        self.selected_elements = []
        self.buttons = [[None for _ in row] for row in self.elements]
    def get_photo_peaks(self):
        return self.photo_peaks
    def get_selected_elements(self):
        return self.selected_elements
    def show(self,selected_elements = []):
        # Create a frame for the periodic table
        tk.Toplevel.__init__(self, self.parent)
        self.selected_elements = selected_elements

        self.callback = self.callback
        self.title("Periodic Table")
        self.frame = tk.Frame(self)
        self.frame.pack()    
    
        # Create buttons for each element
        for y,row in enumerate(self.elements):
            #row_frame = tk.Frame(frame)
            #row_frame.grid(row=y)
            for x,element in enumerate(row):
                if element:
                    button = tk.Button(self.frame, text=element, width=5, height=3)
                    button.config(command=lambda y=y,x=x: self.button_callback(x,y))
                    button.grid(column=x,row=y)
                    self.colorButton(button,x,y)
                    if(element in selected_elements): 
                        button.config(bg="red")
                    
                    self.buttons[y][x] = button
                else:
                    spacer = tk.Label(self.frame, text="", width=3, height=2)
                    spacer.grid(column=x,row=y)
    def colorButton(self,button,x,y):
        if(x==0 and y == 0):
            button.config(bg="lawn green",fg="red")
        elif(x==0):
            button.config(bg="tomato",fg="black")
        elif(x == 1):
            button.config(bg="violet red",fg="black")
        elif(x>=2 and x<=12 and y<=6):
            if(x==3):
                button.config(bg="white",fg="grey")
            elif(y==6 and x >3):
                button.config(bg="light gray",fg="black")
            else:
                button.config(bg="CadetBlue1",fg="black")
        elif(y>=7):
            button.config(bg="light salmon",fg="black")
        elif(x==18 and y!= 6):
            button.config(bg="MediumPurple1",fg="red")
        elif(x ==17 and y <=5):
            button.config(bg="light goldenrod")
            if(y >=1 and y <=2):
                button.config(fg="red")
            elif(y==3):
                button.config(fg="blue")
            else:
                button.config(fg="black")
        elif(x<17 and x >=13):
            if(y >5):
                button.config(bg="light gray",fg="black") 
            elif(y == x%13+1):
                button.config(bg="bisque2",fg="black")
            elif(y > x%13+1):
                button.config(bg="gray63",fg="black")
            else:
                if(y == 1 and x>14):
                    button.config(fg="red")
                button.config(bg="lime green")
        else:
            button.config(bg="light gray",fg="black")
        
    def button_callback(self,x,y):
        if self.elements_[y][x] in self.selected_elements:
            self.colorButton(self.buttons[y][x],x,y)
        else:
            self.buttons[y][x].config(bg="red")
        self.callback(self.elements_[y][x])