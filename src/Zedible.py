
from cProfile import run
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
from itertools import compress

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Zedible')
        
        #self['background']='#9bc2ac'
        self.resizable(True,False)
        self.addButons()
        self.minsize(800, 500)
        #self.geometry("800x500+200+200")
        self.iconbitmap("Zedible_Branding_STG05_Brandmark.ico")
        self.percentageHistoryDict = dict()

    def textFieldWithButton(self,outerFrame: Frame,frame_text: str,help_text: str) -> Frame:
        label_frame = LabelFrame(outerFrame,highlightcolor='#3398FF', text = frame_text,padx=5,pady=5)
        label_frame.pack(expand=True,anchor="w")
        text_help = Label(label_frame,justify="left",text=help_text,anchor='w')
        text_help.pack(expand=False,fill="x",side=TOP,pady=0)
        text_field = tk.Text(label_frame,highlightcolor='#3398FF',height=1)
        text_field.pack(expand=True,fill="x",side=LEFT, padx=5,pady=0)
        select_button = tk.Button(label_frame,
            text='...',
            command=lambda: self.fill_text_field(frame_text,text_field),
            padx=10
        )
        select_button.pack(side=RIGHT,expand=False, padx=5, pady=0,fill=NONE)
        return label_frame, text_field

       
    def addButons(self):  

        main_text =   'Main Database File'
        main_help_text = 'Comma seperated file with 5 columns: Kategorie, Name DE, Name EN, CO2 / 1.6FU (ohne Flug), kg CO2 / kg (ohne Flug).\n\
The file should have a headerline.'
        [self.mainDBframe,self.mainFile] = self.textFieldWithButton(self,main_text,main_help_text)
        self.mainFile.insert(INSERT,"C:/Users/henry/Documents/HJS_Dev/Zedible/Zedible/inputs/Master Db (v3).csv")
        sub_help_text = 'Comma seperated file with 2 columns: Supplier Database Name EN, Main Database Name EN.\n\
The file must have a headerline.'
        substitue_text = 'Substitutions Database File'
        [self.subDBframe,self.subFile] = self.textFieldWithButton(self,substitue_text,sub_help_text)
        self.subFile.insert(INSERT,'C:/Users/henry/Documents/HJS_Dev/Zedible/Zedible/inputs/substitutions.csv')
        supplier_help_text = "Comma seperated file with 5 columns: Supplier, Product Code, Product Name, Case Size, Ingredients.\n\
The file must have a headerline."
        supplier_text = 'Supplier Database File'
        [self.supplierDBframe, self.supplierFile] = self.textFieldWithButton(self,supplier_text,supplier_help_text)
        self.supplierFile.insert(INSERT,'C:/Users/henry/Documents/HJS_Dev/Zedible/Zedible/inputs/Supplier DB.csv')
        
        default_percentage_help_text="Comma seperated file with 3 columns: E Number, Name EN and Fraction.\n\
The file must have a headerline."
        default_percent_text = 'Default Percentages File'
        [self.defaultDBframe,self.defaultFile] = self.textFieldWithButton(self,default_percent_text,default_percentage_help_text)
        self.defaultFile.insert(INSERT,'C:/Users/henry/Documents/HJS_Dev/Zedible/Zedible/inputs/defaultPercentages2.csv')
        
        auto_sub_products = 'Automatic Sub-ingredient file'
        auto_product_help_text = "Comma seperated file with 2 columns: List of ingredients to replace, Main DB name.\n\
The file must have a headerline."
        [self.autoProductDBframe,self.autoProductFile] = self.textFieldWithButton(self,auto_sub_products,auto_product_help_text)
        self.autoProductFile.insert(INSERT,'C:/Users/henry/Documents/HJS_Dev/Zedible/Zedible/inputs/autoIngredientReplacements.csv')
        launch_text = 'Run'
        self.launch_button = tk.Button(
            self,
            text=launch_text,
            command= self.go
        )
        
        self.mainDBframe.pack(expand=False,side= TOP, padx=5, pady=5,fill="x")
        self.subDBframe.pack(expand=False,side = TOP, padx=5, pady=5,fill="x")
        self.defaultDBframe.pack(expand=False,side = TOP, padx=5, pady=5,fill="x")
        self.supplierDBframe.pack(expand=False,side = TOP, padx=5, pady=5,fill="x")      
        self.autoProductDBframe.pack(expand=False,side = TOP, padx=5, pady=5,fill="x")       

        runLabel = Label(self,text='Output is saved into the same directory as the supplier database.\n\
Generated files are:\n\
fraction_history_YYMMDD.csv listing the minimum, mean and maximum fraction of items in the supplier database\n\
output_Db_YYMMDD.csv listing the updated supplier database with CO2/kg and calculational data',anchor='w',justify='left')
        runLabel.pack(expand=True,fill='x',side = TOP,anchor='s',padx=5)
        self.progress_bar = ttk.Progressbar(self,orient='horizontal',mode='determinate',length=720)
        self.progress_bar.pack(expand=True,side = TOP,padx=5, pady=5,fill="x",anchor='s') 
        self.launch_button.pack(expand=False,side = TOP, padx=5, pady=5)
        
        
        
        
    def fill_text_field(self,text: str,text_field: Frame):
        curr_dir = text_field.get(0.0,"end-1c")
        text_field.delete(1.0,"end-1c")
        text_field.insert(INSERT,self.select_file(text,curr_dir))

    def loadFiles(self):    
        mainFileStr = self.mainFile.get(0.0,"end-1c")
        subFileStr = self.subFile.get(0.0,"end-1c")
        defaultFileStr = self.defaultFile.get(0.0,"end-1c")
        supplierFileStr = self.supplierFile.get(0.0,"end-1c")
        autoProductFileStr = self.autoProductFile.get(0.0,"end-1c")
        
        try:
            self.autoProduct_dataframe = pd.read_csv(autoProductFileStr,
                delimiter=',',
                header=0,
                usecols=[0,1],
                names=['Ingredients','CO2'])
        except:
            showwarning(title=None, message="Failed to ingredient list replacement database")
            self.progress_bar.stop()   

        try:
            self.supplier_dataframe = pd.read_csv(supplierFileStr,
                delimiter=',',
                header=0,
                usecols=[0,1,2,3,4],
                names=['Supplier','Product Code','Product Name','Case Size','Ingredients'])
        except:
            showwarning(title=None, message="Failed to load supplier database")
            self.progress_bar.stop()   
        
        try:     
            self.master_dataframe = pd.read_csv(mainFileStr,
                delimiter=',',
                header=0,
                usecols=[0,1,2,4],
                names=['Categorie','Name DE','Name EN','kg CO2 / kg (ohne Flug)'])
        except:
            showwarning(title=None, message="Failed to load main database")
            self.progress_bar.stop()               
        
        try:        
            self.sub_dataframe = pd.read_csv(subFileStr,
                delimiter=',',
                header=0,
                usecols=[0,1],
                names=['SupplierDB','MainDB'])
        except:
            showwarning(title=None, message="Failed to load substitutions database")
            self.progress_bar.stop()    
        
        try:
            self.default_percentagaes_dataframe = pd.read_csv(defaultFileStr,
                delimiter=',',
                header=0,
                usecols=[0,1,2],
                names=['E_Number','Item','Fraction'])
        except:
            showwarning(title=None, message="Failed to load default percentages database")
            self.progress_bar.stop()  

        self.supplier_dataframe = self.supplier_dataframe.apply(lambda x: self.lowerCase(x)) 
        self.master_dataframe = self.master_dataframe.apply(lambda x: self.lowerCase(x))  
        self.default_percentagaes_dataframe = self.default_percentagaes_dataframe.apply(lambda x: self.lowerCase(x)) 
        self.sub_dataframe = self.sub_dataframe.apply(lambda x: self.lowerCase(x)) 
        self.autoProduct_dataframe = self.autoProduct_dataframe.apply(lambda x: self.lowerCase(x)) 

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
            return
        date_time = datetime.now().strftime("%m_%d_%Y_%H%M%S")

        nTotal = len(self.supplier_dataframe.Ingredients)
        CO2perKG = [float] * nTotal
        missing = [str] * nTotal
        main = [str] * nTotal
        calculate = [str] * nTotal
        matched = [str] * nTotal
        lastPercent = -1
        list_all_missing = list()
        list_all_matches = list()
        for index, ingredientString in self.supplier_dataframe.Ingredients.items():
            if index == 2089 or index == 2090 or index == 1901  :
                print(ingredientString)

            prcentCom= numpy.floor(100*index/nTotal)
            self.progress_bar.step(1.0/nTotal)
            self.update()
            if (prcentCom) % 5 == 0 and prcentCom != lastPercent:
                print("{:.0f}%".format(prcentCom))
                lastPercent = prcentCom
            if isinstance(ingredientString, str):
                try:
                    parsedIngredientString = parseIngredientString(ingredientString)
                except:
                    returnMessage = "Supplier:"+self.supplier_dataframe['Supplier'][index]+"\n\
                        Product Code:"+self.supplier_dataframe['Product Code'][index]+"\n\
                        Failed to parse ingredient string: "+ ingredientString  
                    showwarning(title=None, message=returnMessage)
                try:
                    product = Products(parsedIngredientString,self.master_dataframe,self.sub_dataframe,self.default_percentagaes_dataframe,self.autoProduct_dataframe)
                    CO2perKG[index] = product.totalCO2
                except:
                    returnMessage = "Supplier:"+self.supplier_dataframe['Supplier'][index]+"\n\
                        Product Code:"+self.supplier_dataframe['Product Code'][index]+"\n\
                        Failed to calculate CO2"  
                    showwarning(title=None, message=returnMessage)
                    return
                main[index] = product.databaseIngredients
                calculate[index] = product.calculateIngredients
                matched[index] = product.matchedIngredients
                missing[index] = product.missingIngredients
                list_all_missing.extend(product.missingIngredients)
                list_all_matches.extend(product.autoIngredients)
                goodPercentage = ~numpy.isnan(product.percentages)
                if any(goodPercentage):
                    goodIngredients = list(compress(product.databaseIngredients,goodPercentage))
                    goodPercentageValues = [[val] for val in list(compress(product.percentages,goodPercentage))]
                    updateDictVals = dict(zip(goodIngredients,goodPercentageValues))
                    for key in updateDictVals:
                        if key in self.percentageHistoryDict.keys():
                            self.percentageHistoryDict[key] = self.percentageHistoryDict[key]+ updateDictVals[key]
                        else: 
                            self.percentageHistoryDict[key] = updateDictVals[key]
            else:
                missing[index]=''
                calculate[index] = ''
        print("date and time:",date_time)
        self.supplier_dataframe['missingName'] = missing
        self.supplier_dataframe['Calculation'] = calculate
        self.supplier_dataframe['co2perkg'] = CO2perKG
        saveDir = os.path.dirname(os.path.abspath(self.supplierFile.get(0.0,"end-1c")))
        saveName = os.path.join(saveDir,'output_Db_'+date_time+'.csv')
        self.supplier_dataframe.to_csv(saveName,sep=',')
        self.progress_bar.stop()
        returnDict = dict()
        for key in self.percentageHistoryDict:
            minVal = numpy.min(self.percentageHistoryDict[key]) 
            maxVal = numpy.max(self.percentageHistoryDict[key])
            meanVal = numpy.mean(self.percentageHistoryDict[key])
            returnDict[key] = [minVal, meanVal, maxVal]
        percentageHistoryDB = pd.DataFrame.from_dict(returnDict)
        percentageHistoryDB = percentageHistoryDB.transpose()
        percentageHistoryDB.columns = ['Min','Mean','Max']
        
        saveName = os.path.join(saveDir,'fraction_history_'+date_time+'.csv')
        percentageHistoryDB.to_csv(saveName,sep=',')

        unique_missing_list = list(set(list_all_missing))
        count = [ list_all_missing.count(missing_name) for missing_name in unique_missing_list ]
        missing_data = {'Count':count}
        unique_missing_dataframe = pd.DataFrame(data=missing_data, index = unique_missing_list)
        unique_missing_dataframe = unique_missing_dataframe.sort_values(by=['Count'],ascending=False)
        
        unique_missing_dataframe.index.name = 'Ingredient'
        saveDir = os.path.dirname(os.path.abspath(self.supplierFile.get(0.0,"end-1c")))
        saveName = os.path.join(saveDir,'unqiue_missing_'+date_time+'.csv')
        unique_missing_dataframe.to_csv(saveName,sep=',')

        unique_matches_list = list(set(list_all_matches))
        count = [ list_all_matches.count(match_name) for match_name in unique_matches_list ]
        match_count = {'Count':count}
        unique_matches_dataframe = pd.DataFrame(data=match_count, index = unique_matches_list)
        unique_matches_dataframe.index.name = 'Match'
        saveDir = os.path.dirname(os.path.abspath(self.supplierFile.get(0.0,"end-1c")))
        saveName = os.path.join(saveDir,'unqiue_matched_'+date_time+'.csv')
        unique_matches_dataframe.to_csv(saveName,sep=',')

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

