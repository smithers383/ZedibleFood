
from cProfile import run
import pandas as pd
import numpy
from datetime import datetime
from parseIngredientString import parseIngredientString
from Products import Products
from tkinter import *
import tkinter as tk

import threading
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showwarning
import os
from itertools import compress

def read_file(file_str,header_skip,col_numbers,col_names):
    try:
        return_db = pd.read_excel(file_str,
                header=header_skip,
                usecols=col_numbers,
                names=col_names)
    except:
        return_db = pd.read_csv(file_str,
                delimiter=',',
                header=header_skip,
                usecols=col_numbers,
                names=col_names,
                encoding='latin-1')
    return return_db

def clean_ingredients(ingredientString):
    parsedIngredientString = ''
    if isinstance(ingredientString, str):
        try:
            parsedIngredientString = parseIngredientString(ingredientString)
        except:
            returnMessage = "Failed to parse ingredient string: "+ ingredientString  
            showwarning(title=None, message=returnMessage)
    elif isinstance(ingredientString, list):
        try:
            parsedIngredientString = [clean_ingredients(ingredient_str_sub) for ingredient_str_sub in ingredientString]        
        except:
            returnMessage = "Failed to parse ingredient string: "+ ingredientString  
            showwarning(title=None, message=returnMessage)
    return parsedIngredientString



def category_models_fn(category_counts):
    top_X = 20
    category_models = {}
    for category, ingredient_count in category_counts.items():
        tmp = sorted(ingredient_count.items(), key=lambda x: x[1], reverse=True)[:top_X]
        #print('Category: {}\n{}\n'.format(category,tmp))
        for ingredient,ingredient_count in tmp:
            if ingredient not in category_models:
                # Initialize dict if ingredient is detected for the first time
                category_models[ingredient] = {}
                # Keep track of how many times each ingredient is mapped to a category
                if category not in category_models[ingredient]:
                    category_models[ingredient][category] = ingredient_count/len(tmp)
            else:
                if category not in category_models[ingredient]:
                    category_models[ingredient][category] = ingredient_count/len(tmp)
    return category_models

def predict_category(list_of_ingredients,category_models, top_X):
    list_of_sorted_categories = []
    category_score =  {}
    for ingredient in list_of_ingredients:
        # Ensure the ingredient is available in the model storage
        if ingredient in category_models:
            ingredient_categories = category_models[ingredient]
            for category, score in ingredient_categories.items():
                if category not in category_score:
                    category_score[category] = 0
                print('Ingredient: {}, category: {}, score: {}'.
                      format(ingredient, category, score))
                category_score[category] += score
    list_of_sorted_categories = sorted(category_score.items(), key=lambda x: x[1], reverse=True)
    #return list_of_sorted_categories[:top_X]
    try:
        return list_of_sorted_categories[0][0]
    except:
        return ''

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Zedible')
        
        self['background']='#9bc2ac'
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
        self.mainFile.insert(INSERT,"/Users/edbrown/Desktop/Zedible Algo/inputs/Master Db (v3).csv")
        sub_help_text = 'Comma seperated file with 2 columns: Supplier Database Name EN, Main Database Name EN.\n\
The file must have a headerline.'
        substitue_text = 'Substitutions Database File'
        [self.subDBframe,self.subFile] = self.textFieldWithButton(self,substitue_text,sub_help_text)
        self.subFile.insert(INSERT,'/Users/edbrown/Desktop/Zedible Algo/inputs/substitutions.csv')
        supplier_help_text = "Comma seperated file with 5 columns: Supplier, Product Code, Product Name, Case Size, Ingredients.\n\
The file must have a headerline."
        supplier_text = 'Supplier Database File'
        [self.supplierDBframe, self.supplierFile] = self.textFieldWithButton(self,supplier_text,supplier_help_text)
        self.supplierFile.insert(INSERT,'/Users/edbrown/Desktop/Zedible Algo/inputs/Supplier DB.csv')
        
        default_percentage_help_text="Comma seperated file with 3 columns: E Number, Name EN and Fraction.\n\
The file must have a headerline."
        default_percent_text = 'Default Percentages File'
        [self.defaultDBframe,self.defaultFile] = self.textFieldWithButton(self,default_percent_text,default_percentage_help_text)
        self.defaultFile.insert(INSERT,'/Users/edbrown/Desktop/Zedible Algo/inputs/defaultPercentages2.csv')
        
        auto_sub_products = 'Automatic Sub-ingredient file'
        auto_product_help_text = "Comma seperated file with 3 columns: List of ingredients to replace,CO2 to use and Main DB name.\n\
The file must have a headerline. The list of ingredients needs to be semicolon (;) seperated"
        [self.autoProductDBframe,self.autoProductFile] = self.textFieldWithButton(self,auto_sub_products,auto_product_help_text)
        self.autoProductFile.insert(INSERT,'/Users/edbrown/Desktop/Zedible Algo/inputs/autoIngredientReplacements.csv')
        launch_text = 'Run'
        self.launch_button = tk.Button(
            self,
            text=launch_text,
            command= self.go
        )

        auto_category = 'Reference Supplier Product to Cateogry Matching File'
        auto_category_help_text = "Comma seperated file with 6 columns: Supplier, Product Code, Product Name, Case Size, Ingredients and Category.\n\
The file must have a headerline."
        [self.autoCategoryDBframe,self.autoCategoryFile] = self.textFieldWithButton(self,auto_category,auto_category_help_text)
        self.autoCategoryFile.insert(INSERT,'/Users/edbrown/Desktop/Zedible Algo/inputs/Harvey & Brockless Supplier data (Anna Fe).xlsx')
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
        self.autoCategoryDBframe.pack(expand=False,side = TOP, padx=5, pady=5,fill="x")      

        runLabel = Label(self,text='Output is saved into the same directory as the supplier database.\n\
Generated files are:\n\
fraction_history_YYMMDD.csv listing the minimum, mean and maximum fraction of items in the supplier database\n\
output_Db_YYMMDD.csv listing the updated supplier database with CO2/kg and calculational data',anchor='w',justify='left')
        runLabel.pack(expand=True,fill='x',side = TOP,anchor='s',padx=5)
        self.progress_bar = ttk.Progressbar(self,orient='horizontal',mode='indeterminate',length=720)
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
        autoCategoryFileStr = self.autoCategoryFile.get(0.0,"end-1c")
        try:
            self.autoProduct_dataframe = read_file(autoProductFileStr,0,[0,1,2],['Ingredients','CO2','Name'])
        except:
            showwarning(title=None, message="Failed to ingredient list replacement database")
            self.progress_bar.stop()   

        try:
            self.supplier_dataframe = read_file(supplierFileStr,0,[0,1,2,3,4],['Supplier','Product Code','Product Name','Case Size','Ingredients'])
        except:
            showwarning(title=None, message="Failed to load supplier database")
            self.progress_bar.stop()   
        
        try:     
            self.master_dataframe = read_file(mainFileStr,0,[0,1,2,4],['Categorie','Name DE','Name EN','kg CO2 / kg (ohne Flug)'])
        except:
            showwarning(title=None, message="Failed to load main database")
            self.progress_bar.stop()               
        
        try:        
            self.userDB = read_file(subFileStr,0,[0,1],['SupplierDB','MainDB'])
        except:
            showwarning(title=None, message="Failed to load substitutions database")
            self.progress_bar.stop()    
        
        try:
            self.default_percentagaes_dataframe = read_file(defaultFileStr,0,[0,1,2],['E_Number','Item','Fraction'])
        except:
            showwarning(title=None, message="Failed to load default percentages database")
            self.progress_bar.stop()  

        #try:
        self.autoCategory_dataframe = read_file(autoCategoryFileStr,0,[0,1,2,3,4,5,6],['Supplier','Product Code','Product Name','Ingredients','CalcIngredients','CO2perKg','Category'])
        #except:
        #    showwarning(title=None, message="Failed to load autocategory database")
        #    self.progress_bar.stop()  

        self.supplier_dataframe = self.supplier_dataframe.apply(lambda x: self.lowerCase(x)) 
        self.master_dataframe = self.master_dataframe.apply(lambda x: self.lowerCase(x))  
        self.default_percentagaes_dataframe = self.default_percentagaes_dataframe.apply(lambda x: self.lowerCase(x)) 
        self.userDB = self.userDB.apply(lambda x: self.lowerCase(x)) 
        self.autoProduct_dataframe = self.autoProduct_dataframe.apply(lambda x: self.lowerCase(x)) 
        self.autoCategory_dataframe = self.autoCategory_dataframe.apply(lambda x: self.lowerCase(x)) 

    def process_ingredients(self,parsedIngredientDict):
        product = Products(parsedIngredientDict,self.master_dataframe,self.userDB,self.default_percentagaes_dataframe,self.autoProduct_dataframe)  
        return product

    # This function takes each group and then calculates the word frequency for the ingredients
    # and stores it in the category_counts dict
    def category_counts_fn(self,x):
        self.category_counts[x.name] = {}
        #print('Category: {}, category size: {}'.format(x.name, len(x.name)))
        for row in x:
            for ingredient in row:
                #print('Row:',row)
                for ingredient in row:
                    if ingredient not in self.category_counts[x.name]:
                        self.category_counts[x.name][ingredient] = 1
                    else:
                        self.category_counts[x.name][ingredient] += 1 # Increase count for this ingredient

    @staticmethod
    def lowerCase(inputVar):
        return [var.lower() if isinstance(var,str) else var for var in inputVar]


    def go(self):
        try:
            self.loadFiles()
        except:
            self.progress_bar.stop()
            showwarning(title=None, message="Failed to load one or more of the input files")
            return

        processThread = threading.Thread(target=self.process_data)
        processThread.start()

    def process_data(self):   

        date_time = datetime.now().strftime("%m_%d_%Y_%H%M%S")

        list_all_missing = list() 
        # parse the ingredients
        self.supplier_dataframe['Ingredients_cleaned'] = self.supplier_dataframe['Ingredients'].map(lambda x: clean_ingredients(x))
        self.autoCategory_dataframe['Ingredients_cleaned'] = self.autoCategory_dataframe['Ingredients'].map(lambda x: clean_ingredients(x))

        # convert the ingredients into Master DB ingredients
        self.supplier_dataframe['Products'] = self.supplier_dataframe['Ingredients_cleaned'].map(lambda x: self.process_ingredients(x))
        self.autoCategory_dataframe['Products'] = self.autoCategory_dataframe['Ingredients_cleaned'].map(lambda x: self.process_ingredients(x))
        
        # extract main db ingredients
        self.supplier_dataframe['MasterDB_Ingredients'] = self.supplier_dataframe['Products'].map(lambda x: x.databaseIngredients) 
        self.supplier_dataframe['MasterDB_Ingredients_noSub'] = self.supplier_dataframe['Products'].map(lambda x: x.databaseIngredients_noSub) 
        self.supplier_dataframe['MasterDB_Ingredients'] = self.supplier_dataframe['Products'].map(lambda x: x.databaseIngredients) 
        self.autoCategory_dataframe['MasterDB_Ingredients_noSub'] = self.autoCategory_dataframe['Products'].map(lambda x: x.databaseIngredients_noSub)

        self.category_counts = {}
        #tmp = self.autoCategory_dataframe.groupby('MasterDB_Categories')['MasterDB_Ingredients'].apply(category_counts_fn)
        #for this_category in category_names:
        #    category_counts[this_category] = category_counts_fn(self.autoCategory_dataframe,this_category)
        self.autoCategory_dataframe.groupby('Category')['Ingredients_cleaned'].apply(self.category_counts_fn)
        #tmp = self.supplier_dataframe.groupby('Category')['Ingredients_normalized'].apply(lambda x: category_counts_fn(x,category_names))
        
        category_models = category_models_fn(self.category_counts)
        top_X = 5

        # Ingredients_cleaned ignores subs automatically. 
        self.supplier_dataframe['Category'] = self.supplier_dataframe['MasterDB_Ingredients_noSub'].map(lambda x: predict_category(x,category_models,top_X))


        # Calc C02
        self.supplier_dataframe['CO2perKg'] = self.supplier_dataframe['Products'].map(lambda x: x.totalCO2)
        self.supplier_dataframe['missingName'] = self.supplier_dataframe['Products'].map(lambda x: x.missingIngredients)
        self.supplier_dataframe['Calculation'] = self.supplier_dataframe['Products'].map(lambda x: x.calculateIngredients)
        
        saveDir = os.path.dirname(os.path.abspath(self.supplierFile.get(0.0,"end-1c")))
        saveName = os.path.join(saveDir,'output_Db_'+date_time+'.csv')
        self.supplier_dataframe.to_csv(saveName,sep=',',\
            columns=['Supplier','Product Code','Product Name','Ingredients','Calculation','CO2perKg','Category'])

        #main = self.supplier_dataframe['Products'].map(lambda x: x.databaseIngredients)
        #matched = self.supplier_dataframe['Products'].map(lambda x: x.matchedIngredients)

        list_all_missing = [j for sub in self.supplier_dataframe['missingName'] for j in sub]
        #list_all_matches = [j for sub in self.supplier_dataframe['Products'].map(lambda x: x.autoIngredients) for j in sub]
        
        # compute CO2 
        self.supplier_dataframe['CO2perKg'] = self.supplier_dataframe['Ingredients']
        
        for product in self.supplier_dataframe['Products']:
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


        print("date and time:",date_time)


        

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
        self.progress_bar.stop()
        #unique_matches_list = list(set(list_all_matches))
        #count = [ list_all_matches.count(match_name) for match_name in unique_matches_list ]
        #match_count = {'Count':count}
        #unique_matches_dataframe = pd.DataFrame(data=match_count, index = unique_matches_list)
        #unique_matches_dataframe.index.name = 'Match'
        #saveDir = os.path.dirname(os.path.abspath(self.supplierFile.get(0.0,"end-1c")))
        #saveName = os.path.join(saveDir,'unqiue_matched_'+date_time+'.csv')
        #unique_matches_dataframe.to_csv(saveName,sep=',')

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
            ('xlsx files','*.xlsx'),
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

