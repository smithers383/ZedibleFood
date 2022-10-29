
import pandas as pd
import numpy
from datetime import datetime
from parseIngredientString import parseIngredientString
from Products import Products
import os

supplier_CSV_path = \
    r"C:\Users\henry\Documents\HJS_Dev\Zedible\Zedible\inputs\Supplier DB.csv"
default_percentages_CSV_path = \
    r"C:\Users\henry\Documents\HJS_Dev\Zedible\Zedible\inputs\defaultPercentages.csv"
master_CSV_path= \
    r"C:\Users\henry\Documents\HJS_Dev\Zedible\Zedible\inputs\Master Db (v3).csv"
user_CSV_path= \
    r"C:\Users\henry\Documents\HJS_Dev\Zedible\Zedible\inputs\user.csv"

ingredientCols=[0,1,2,3,4]

supplier_dataframe = pd.read_csv(supplier_CSV_path,skiprows=1,header=0,delimiter=',',usecols=ingredientCols)
master_dataframe = pd.read_csv(master_CSV_path,delimiter=',',header=0)
user_dataframe = pd.read_csv(user_CSV_path,delimiter=',')
default_percentagaes_dataframe = pd.read_csv(default_percentages_CSV_path,delimiter=',')

# make lower case
user_dataframe['MainDB'] = user_dataframe['MainDB'].str.casefold()
user_dataframe['SupplierDB'] = user_dataframe['SupplierDB'].str.casefold()
master_dataframe['Name EN'] = master_dataframe['Name EN'].str.casefold()
supplier_dataframe['Ingredients'] = supplier_dataframe['Ingredients'].str.casefold()
default_percentagaes_dataframe['Item'] = default_percentagaes_dataframe['Item'].str.casefold()
default_percentagaes_dataframe['E_Number'] = default_percentagaes_dataframe['E_Number'].str.casefold()

# things that are bad
# string seperated by full stops
product = Products(parseIngredientString(supplier_dataframe.Ingredients[101]),master_dataframe,user_dataframe,default_percentagaes_dataframe)
product.totalCO2
#TODO
# need to have a list of preservatives ect that we can assing 0.1% to by default.

date_time = datetime.now().strftime("%m_%d_%Y_%H%M%S")

nTotal = len(supplier_dataframe.Ingredients)
CO2perKG = [float] * nTotal
missing = [str] * nTotal
main = [str] * nTotal
supplier = [str] * nTotal
matched = [str] * nTotal
lastPercent = -1
list_all_missing = list()
for index, ingredientString in supplier_dataframe.Ingredients.items():
    prcentCom= numpy.floor(100*index/nTotal)
    if (prcentCom) % 5 == 0 and prcentCom != lastPercent:
        print("{:.0f}%".format(prcentCom))
        lastPercent = prcentCom
    if isinstance(ingredientString, str):
        if 1 > 0: #try:
            product = Products(parseIngredientString(ingredientString),master_dataframe,user_dataframe,default_percentagaes_dataframe)
            CO2perKG[index] = product.totalCO2
            main[index] = product.databaseIngredients
            supplier[index] = product.supplierIngredients
            matched[index] = product.matchedIngredients
            missing[index] = product.missingIngredients
            list_all_missing.extend(product.missingIngredients)
        else: #except:
            #print(index,nTotal)
            print()
            print("Supplier:"+supplier_dataframe['Supplier'][index])
            print("Product Code:"+supplier_dataframe['Product Code'][index])
            print("Failed to fully process: "+ ingredientString)
print("date and time:",date_time)
unique_missing_list = list(set(list_all_missing))
count = [ list_all_missing.count(missing_name) for missing_name in unique_missing_list ]
missing_data = {'Count':count}
unique_missing_dataframe = pd.DataFrame(data=missing_data, index = unique_missing_list)
unique_missing_dataframe = unique_missing_dataframe.sort_values(by=['Count'],ascending=False)
unique_missing_dataframe.index.name = 'Ingredient'
unique_missing_dataframe.to_csv('unqiue_missing_'+date_time+'.csv',sep=',')

supplier_dataframe['MissingName'] = missing
supplier_dataframe['MatchedName'] = matched
supplier_dataframe['Supplier'] = supplier
supplier_dataframe['Main'] = main
supplier_dataframe['CO2perKG'] = CO2perKG
supplier_dataframe.to_csv('output_'+date_time+'.csv',sep=',')

