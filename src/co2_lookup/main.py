
import pandas as pd
import numpy
from datetime import datetime
from parseIngredientString import parseIngredientString
from Products import Products
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showwarning
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Zedible')
        self.minsize(800,400)
        #self['background']='#9bc2ac'
        self.resizable(False,False)
        self.addButons()
        self.iconbitmap("zedible.ico")

    def textFieldWithButton(self,outerFrame: Frame,frame_text: str) -> Frame:
        label_frame = LabelFrame(outerFrame,highlightcolor='#3398FF', text = frame_text,padx=5,pady=5)
        label_frame.pack(expand=True)
        text_field = tk.Text(label_frame,highlightcolor='#3398FF',height=1)
        text_field.pack(expand=False,fill=Y,side=LEFT, padx=5, pady=5)
        select_button = tk.Button(label_frame,
            text='...',
            command=lambda: self.fill_text_field(frame_text,text_field),
            padx=10
        )
        select_button.pack(side=RIGHT,expand=False, padx=5, pady=5,fill=NONE)
        return label_frame, text_field

       
    def addButons(self):  

        main_text =   'Main Database File'
        [self.mainDBframe,self.mainFile] = self.textFieldWithButton(self,main_text)
    
        substitue_text = 'Substitutions Database File'
        [self.subDBframe,self.subFile] = self.textFieldWithButton(self,substitue_text)
        
        supplier_text = 'Supplier Database File'
        [self.supplierDBframe, self.supplierFile] = self.textFieldWithButton(self,supplier_text)
               
        default_percent_text = 'Default Percentages File'
        [self.defaultDBframe,self.defaultFile] = self.textFieldWithButton(self,default_percent_text)

        launch_text = 'Run'
        self.launch_button = tk.Button(
            self,
            text=launch_text,
            command= self.go
        )

        self.mainDBframe.pack(expand=False,side= TOP, padx=5, pady=5)
        self.subDBframe.pack(expand=False,side = TOP, padx=5, pady=5)
        self.defaultDBframe.pack(expand=False,side = TOP, padx=5, pady=5)
        self.supplierDBframe.pack(expand=False,side = TOP, padx=5, pady=5)       

        self.progress_bar = ttk.Progressbar(self,orient='horizontal',mode='determinate',length=720) 
        self.progress_bar.pack(expand=True,side = TOP,padx=5, pady=5)
        self.launch_button.pack(expand=False,side = BOTTOM, padx=5, pady=5)
        
        
    def fill_text_field(self,text: str,text_field: Frame):
        curr_dir = text_field.get(0.0,"end-1c")
        text_field.delete(1.0,"end-1c")
        text_field.insert(INSERT,self.select_file(text,curr_dir))

    def loadFiles(self):    
        ingredientCols=[0,1,2,3,4]
        mainFileStr = self.mainFile.get(0.0,"end-1c")
        subFileStr = self.subFile.get(0.0,"end-1c")
        defaultFileStr = self.defaultFile.get(0.0,"end-1c")
        supplierFileStr = self.supplierFile.get(0.0,"end-1c")
        self.supplier_dataframe = pd.read_csv(supplierFileStr,skiprows=1,header=0,delimiter=',',usecols=ingredientCols)
        self.master_dataframe = pd.read_csv(mainFileStr,delimiter=',',header=0)
        self.sub_dataframe = pd.read_csv(subFileStr,delimiter=',')
        self.default_percentagaes_dataframe = pd.read_csv(defaultFileStr,delimiter=',')
        self.supplier_dataframe = self.supplier_dataframe.apply(lambda x: self.lowerCase(x)) 
        self.master_dataframe = self.master_dataframe.apply(lambda x: self.lowerCase(x))  
        self.default_percentagaes_dataframe = self.default_percentagaes_dataframe.apply(lambda x: self.lowerCase(x)) 
        self.sub_dataframe = self.sub_dataframe.apply(lambda x: self.lowerCase(x)) 

    @staticmethod
    def lowerCase(inputVar):
        return [var.lower() if isinstance(var,str) else var for var in inputVar]


    def go(self):
        self.progress_bar.start(1000)
        try:
            self.loadFiles()
        except:
            self.progress_bar.stop()
            showwarning(title=None, message="Failed to load one or more of the input files")
        date_time = datetime.now().strftime("%m_%d_%Y_%H%M%S")

        nTotal = len(self.supplier_dataframe.Ingredients)
        CO2perKG = [float] * nTotal
        missing = [str] * nTotal
        main = [str] * nTotal
        supplier = [str] * nTotal
        matched = [str] * nTotal
        lastPercent = -1
        for index, ingredientString in self.supplier_dataframe.Ingredients.items():
            prcentCom= numpy.floor(100*index/nTotal)
            self.progress_bar.step(1.0/nTotal)
            self.update()
            if (prcentCom) % 5 == 0 and prcentCom != lastPercent:
                print("{:.0f}%".format(prcentCom))
                lastPercent = prcentCom
            if isinstance(ingredientString, str):
                try:
                    product = Products(parseIngredientString(ingredientString),self.master_dataframe,self.sub_dataframe,self.default_percentagaes_dataframe)
                    CO2perKG[index] = product.totalCO2
                    main[index] = product.databaseIngredients
                    supplier[index] = product.supplierIngredients
                    matched[index] = product.matchedIngredients
                    missing[index] = product.missingIngredients
                except:
                    returnMessage = "Supplier:"+self.supplier_dataframe['supplier'][index]+"\n\
                        Product Code:"+self.supplier_dataframe['product code'][index]+"\n\
                        Failed to fully process: "+ ingredientString  
                    showwarning(title=None, message=returnMessage)

        print("date and time:",date_time)
        self.supplier_dataframe['missingName'] = missing
        self.supplier_dataframe['matchedName'] = matched
        self.supplier_dataframe['supplier'] = supplier
        self.supplier_dataframe['main'] = main
        self.supplier_dataframe['co2perkg'] = CO2perKG
        self.supplier_dataframe.to_csv('output_Db_'+date_time+'.csv',sep=',')
        self.progress_bar.stop()

    @staticmethod
    def select_file(csv_title,cur_dir):
        if os.path.isfile(cur_dir):
            initial_dir = os.path.dirname(os.path.abspath(cur_dir))
        elif os.path.isdir(cur_dir):
            initial_dir = os.path.abspath(cur_dir)
        else:
            initial_dir = '/'

        
        filetypes = (
            ('csv files','*.csv'),
            ('All files','*.*')
        )

        filename = fd.askopenfilename(
            title = csv_title,
            initialdir=initial_dir,
            filetypes=filetypes)

        return filename

if __name__ == "__main__":
    app = App()
    app.mainloop()       


supplierDb = 'Supplier DB.csv'
ingredientCols=[0,1,2,3,4]
supplierSkipRows = 0

masterPdHeaders=['Kategorie','Name DE','Name EN','CO2perKg']
pdMaster = pd.read_csv('Master Db (v3).csv',delimiter=',',header=0)
pdUser = pd.read_csv('user.csv',delimiter=',')

defaultPercentagaes = pd.read_csv('defaultPercentages.csv',delimiter=',')



# things that are bad
# string seperated by full stops

#TODO
# need to have a list of preservatives ect that we can assing 0.1% to by default.






#for index, ingredientString in pdIngredients.Ingredients.items():
#    #print(index,nTotal)
#    if isinstance(ingredientString, str):
#        results = calcCO2(parseIngredientString(ingredientString),pdMaster,pdUser)
#        CO2perKG[index] = results[0]
#        main[index] = [item.mainName for item in results[1] if len(item.mainName) > 0 ]
#        supplier[index] = [item.supplierName for item in results[1] if len(item.supplierName) > 0]
#        matched[index] = [item.matchedName for item in results[1] if len(item.matchedName) > 0]
#        missing[index] = [item.missingName for item in results[1] if len(item.missingName) > 0]
#print("date and time:",date_time)

#pdIngredients['MissingName'] = missing
#pdIngredients['MatchedName'] = matched
#pdIngredients['Supplier'] = supplier
#pdIngredients['Main'] = main
#pdIngredients['CO2perKG'] = CO2perKG
#pdIngredients['CO2perKG'] = [calcCO2(pdMaster,parseIngredientString(ingredientString)) for ingredientString in pdIngredients.Ingredients]
#pdIngredients.to_csv('output_Db_'+date_time+'.csv',sep=',')
