
import pandas as pd
import numpy
from datetime import datetime
from parseIngredientString import parseIngredientString
from Products import Products

supplierDb = 'Supplier DB.csv'
ingredientCols=[0,1,2,3,4]
supplierSkipRows = 0
pdIngredients = pd.read_csv(supplierDb,skiprows=1,header=0,delimiter=',',usecols=ingredientCols)
masterPdHeaders=['Kategorie','Name DE','Name EN','CO2perKg']
pdMaster = pd.read_csv('Master Db (v3).csv',delimiter=',',header=0)
pdUser = pd.read_csv('user.csv',delimiter=',')

defaultPercentagaes = pd.read_csv('defaultPercentages.csv',delimiter=',')

# make lower case
pdUser['Item'] = pdUser['Item'].str.casefold()
pdUser['SupplierDB'] = pdUser['SupplierDB'].str.casefold()
pdMaster['Name EN'] = pdMaster['Name EN'].str.casefold()
pdIngredients['Ingredients'] = pdIngredients['Ingredients'].str.casefold()
defaultPercentagaes['Item'] = defaultPercentagaes['Item'].str.casefold()
defaultPercentagaes['E_Number'] = defaultPercentagaes['E_Number'].str.casefold()

# things that are bad
# string seperated by full stops

#TODO
# need to have a list of preservatives ect that we can assing 0.1% to by default.

date_time = datetime.now().strftime("%m_%d_%Y_%H%M%S")

nTotal = len(pdIngredients.Ingredients)
CO2perKG = [float] * nTotal
missing = [str] * nTotal
main = [str] * nTotal
supplier = [str] * nTotal
matched = [str] * nTotal
lastPercent = -1
for index, ingredientString in pdIngredients.Ingredients.items():
    prcentCom= numpy.floor(100*index/nTotal)
    if (prcentCom) % 5 == 0 and prcentCom != lastPercent:
        print("{:.0f}%".format(prcentCom))
        lastPercent = prcentCom
    if isinstance(ingredientString, str):
        try:
            product = Products(parseIngredientString(ingredientString),pdMaster,pdUser,defaultPercentagaes)
            CO2perKG[index] = product.totalCO2
            main[index] = product.databaseIngredients
            supplier[index] = product.supplierIngredients
            matched[index] = product.matchedIngredients
            missing[index] = product.missingIngredients
        except:
            #print(index,nTotal)
            print()
            print("Supplier:"+pdIngredients['Supplier'][index])
            print("Product Code:"+pdIngredients['Product Code'][index])
            print("Failed to fully process: "+ ingredientString)
print("date and time:",date_time)

pdIngredients['MissingName'] = missing
pdIngredients['MatchedName'] = matched
pdIngredients['Supplier'] = supplier
pdIngredients['Main'] = main
pdIngredients['CO2perKG'] = CO2perKG
pdIngredients.to_csv('output_Db_'+date_time+'.csv',sep=',')

