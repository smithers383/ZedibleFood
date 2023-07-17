from logging import exception
import numpy
import pandas
ratioDB = pandas.DataFrame(columns=['SupplierDB','MainDB'])
from Ingredients import Ingredients
from itertools import compress
import warnings
class Products:

# HJS potential upgrades
# Don't overwrite user percentages - hold them constant unless over 100% themselves
    def __init__(self, \
            ingredientStringDict: dict,\
            mainDB: pandas.DataFrame,\
            userDB: pandas.DataFrame,\
            defaultPercentages: pandas.DataFrame,\
            autoProductDB: pandas.DataFrame,):
        global ratioDB 
        self.ingredientStringDict = ingredientStringDict
        self.mainDB = mainDB
        self.userDB = userDB
        self.autoProductDB = autoProductDB
        self.defaultPercentages = defaultPercentages
        
        
        self.calcPercentages = []
        #self.ingredients = self.getIngredients()
        #self.subProducts = self.getSubProducts()
        
        
    @property
    def matchedIngredients(self) -> str:
        product = [item.foundName for item in self.ingredients if len(self.ingredients) > 0 and len(item.foundName) > 0]
        product += [item.matchedName for item in self.ingredients if len(self.ingredients) > 0 and len(item.matchedName) > 0]
        
        if self.anySubIngredients:
            subProductsLists = [subProduct.matchedIngredients for subProduct in self.subProducts if len(subProduct.matchedIngredients) > 0 ]
            subProducts = [product for listProducts in subProductsLists for product in listProducts ]
            returnProducts = product+subProducts
        else:
            returnProducts  = product
        
        if len(returnProducts) == 0:
            return ''
        else:
            return returnProducts

    @property
    def missingIngredients(self) -> str:
        product = [item.missingName for item in self.ingredients if len(self.ingredients) > 0 and len(item.missingName) > 0]
        if self.anySubIngredients:
            subProductsLists = [subProduct.missingIngredients for subProduct in self.subProducts if len(subProduct.missingIngredients) > 0 ]
            subProducts = [product for listProducts in subProductsLists for product in listProducts ]
            returnProducts = product+subProducts
        else:
            returnProducts  = product
        
        if len(returnProducts) == 0:
            return ''
        else:
            return returnProducts

    @property
    def autoIngredients(self) -> str:
        product = ['"'+item.supplierName+'","'+item.autoMatchName+'"' for item in self.ingredients if len(self.ingredients) > 0 and len(item.autoMatchName) > 0]
        
        if self.anySubIngredients:
            subProductsLists = [subProduct.autoIngredients for subProduct in self.subProducts if len(subProduct.autoIngredients) > 0 ]
            subProducts = [product for listProducts in subProductsLists for product in listProducts ]
            returnProducts = product+subProducts
        else:
            returnProducts  = product
        
        if len(returnProducts) == 0:
            return ''
        else:
            return returnProducts   


    @property
    def databaseIngredients_noSub(self) -> str:

        product = [item.mainNameNoSub for item in self.ingredients if len(self.ingredients) > 0 and len(item.mainNameNoSub) > 0]
        if self.anySubIngredients:
            subProductsLists = [subProduct.databaseIngredients_noSub for subProduct in self.subProducts if len(subProduct.databaseIngredients_noSub) > 0 ]
            subProducts = [product for listProducts in subProductsLists for product in listProducts ]
            returnProducts = product+subProducts
        else:
            returnProducts  = product
        
        if len(returnProducts) == 0:
            return ''
        else:
            return returnProducts
    
    @property
    def databaseIngredients(self) -> str:

        product = [item.mainName for item in self.ingredients if len(self.ingredients) > 0 and len(item.mainName) > 0]
        if self.anySubIngredients:
            subProductsLists = [subProduct.databaseIngredients for subProduct in self.subProducts if len(subProduct.databaseIngredients) > 0 ]
            subProducts = [product for listProducts in subProductsLists for product in listProducts ]
            returnProducts = product+subProducts
        else:
            returnProducts  = product
        
        if len(returnProducts) == 0:
            return ''
        else:
            return returnProducts
        
    @property
    def databaseCategories(self) -> str:

        all_categories = [item.category for item in self.ingredients if len(self.ingredients) > 0 and len(item.category) > 0]
        if self.anySubIngredients:
            subCateogryLists = [subProduct.databaseCategories for subProduct in self.subProducts if len(subProduct.databaseIngredients) > 0 ]
            subCategories = [category_string for listCategories in subCateogryLists for category_string in listCategories ]
            returnCategories = all_categories+subCategories
        else:
            returnCategories  = all_categories
        
        if len(returnCategories) == 0:
            return ''
        else:
            return returnCategories
    @property
    def calculateIngredients(self) -> str:
        if len(self.ingredients) > 0:
            productName = [item.mainName if  len(item.supplierName) > 0 and len(item.mainName) > 0  else item.missingName for item in self.ingredients ]
        else:
            productName = []    

        calcPercentages = self.calcPercentages
        product = [product+" {:0.2f}%".format(calcPercentages[i]*100) for i, product in enumerate(productName)]

        if self.anySubIngredients:
            subProductsLists = [subProduct.calculateIngredients for subProduct in self.subProducts if len(subProduct.calculateIngredients) > 0 ]
            subProducts = [product for listProducts in subProductsLists for product in listProducts ]
            returnProducts = product+['('+' '.join(map(str, subProducts))+')']
        else:
            returnProducts  = product
        
        if len(returnProducts) == 0:
            return ''
        else:
            return returnProducts

    def getDefaultPercentage(self,ingredient: str) -> float:
        matchItem = self.defaultPercentages['Item']==ingredient
        if any(matchItem): # try ingredient
            return self.defaultPercentages['Fraction'][matchItem].values[0]
        match_E_Number= self.defaultPercentages['E_Number']==ingredient
        if any(match_E_Number): # try Enumber
            return self.defaultPercentages['Fraction'][match_E_Number].values[0]
        # try user sub
        if not any(self.userDB['SupplierDB'] == ingredient):
            return numpy.nan
        ingredient = self.userDB['MainDB'][self.userDB['SupplierDB'] == ingredient].values[0]
        matchItem = self.defaultPercentages['Item']==ingredient
        if any(matchItem): # try ingredient
            return self.defaultPercentages['Fraction'][matchItem].values[0]
        match_E_Number= self.defaultPercentages['E_Number']==ingredient
        if any(match_E_Number): # try Enumber
            return self.defaultPercentages['Fraction'][match_E_Number].values[0]
        return numpy.nan

    @property
    def percentages(self) -> float:
        percentages = [numpy.nan] * len(self.ingredientStringDict)
        for i,ingredientStr in enumerate(self.ingredientStringDict):
            supplierPercent = self.ingredientStringDict[ingredientStr][0]
            if len(supplierPercent) > 0:
                percentages[i] = self.percentStr2Float(supplierPercent)
            else:
                # try main name
                percentageVal = self.getDefaultPercentage(self.ingredients[i].mainName)
                if not numpy.isnan(percentageVal):
                    percentages[i] = percentageVal
                    continue
                # try supplier name
                percentageVal = self.getDefaultPercentage(self.ingredients[i].supplierName)
                if not numpy.isnan(percentageVal):
                    percentages[i] = percentageVal
                    continue
        return percentages
    
    
    def getIngredients(self):
        global ratioDB
        ingredientList = [Ingredients(ingredientStr,self.mainDB,self.userDB,self.defaultPercentages) for ingredientStr in self.ingredientStringDict]
        for ingredient in ingredientList:
            ingredient.lookupCO2()
        return ingredientList
    @property
    def anySubIngredients(self):
        return any([len(self.ingredientStringDict[ingredientStr][1])>0 for ingredientStr in self.ingredientStringDict])

    def getSubProducts(self):   
        global ratioDB
        productList = [Products(self.ingredientStringDict[ingredient.supplierName][1],self.mainDB,self.userDB,self.defaultPercentages,self.autoProductDB)\
             for ingredient in self.ingredients]
        for product in productList:
            product.ingredients = product.getIngredients()
            product.subProducts = product.getSubProducts()
        return productList
    @property
    def CO2(self) -> list:
        ingredientCO2 = [subIngredient.CO2 for subIngredient in self.ingredients]
        if not self.anySubIngredients:
            returnCO2 = ingredientCO2
        else:
            subProductCO2 = [product.totalCO2 for product in self.subProducts]       
            returnCO2 = [float(CO2[0]) if not numpy.isnan(float(CO2[0])) else float(CO2[1]) \
                for CO2 in zip(ingredientCO2,subProductCO2)]          
        return returnCO2
    
    @property
    def totalCO2(self) -> float:
        global ratioDB
        # auto sub calculations
        supplierIngredientSet = set([subIngredient.supplierName for subIngredient in self.ingredients])
        mainIngredientSet = set([subIngredient.mainName for subIngredient in self.ingredients])
        
        #isCheese or other auto sub loop
        for line, subCO2, subName in zip(self.autoProductDB['Ingredients'],self.autoProductDB['CO2'],self.autoProductDB['Name']):
            replaceStrList = str.split(line,';')
            isReplace = all([replaceStr in supplierIngredientSet or \
                replaceStr in mainIngredientSet for replaceStr in replaceStrList])
            if isReplace:
                self.calcPercentages = [1.0]
                self.ingredients = [Ingredients(subName,self.mainDB,self.userDB,self.defaultPercentages)]
                self.subProducts = [] # no longer use sub products

                self.ingredientStringDict = dict()
                #print(subCO2)
                #print(supplierIngredientSet)
                return subCO2
        
        #cheeseStringList = {'milk','rennet','salt'}
        #isCheese = all([cheeseString in supplierIngredientSet or \
        #    cheeseString in mainIngredientSet for cheeseString in cheeseStringList])
        #cheeseCO2 = 0.0772
        #if isCheese: # replace with a cheese.
        #    self.calcPercentages = [1.0]
        #    self.ingredients = [Ingredients('Cheese, firm, Danbo, 45 % fidm.',self.mainDB,self.userDB,self.defaultPercentages)]
        #    self.subProducts = [] # no longer use sub products
        #    self.ingredientStringDict = dict()
        #    return cheeseCO2
        calcPercentages = numpy.zeros(len(self.CO2))
        if len(self.CO2) == 0: # no data
            self.calcPercentages = calcPercentages
            return numpy.nan

        isGoodCO2 = ~pandas.isnull(self.CO2)
     
        validPercentages = list(compress(self.percentages,isGoodCO2))
        goodCO2 = numpy.array([float(x) for x in (compress(self.CO2,isGoodCO2))])
        if not any(isGoodCO2):
            self.calcPercentages = calcPercentages
            return numpy.nan
        if all(numpy.isnan(validPercentages)):
            calcPercentages[isGoodCO2] = numpy.ones(len(goodCO2))/float(len(goodCO2))
            self.calcPercentages = calcPercentages
            return numpy.mean(list(goodCO2))
        if all(~numpy.isnan(validPercentages)): # all not nan - scale up to 1 then compute
            calcPercentages[isGoodCO2] = validPercentages/(numpy.sum(validPercentages))
            self.calcPercentages = calcPercentages
            return numpy.sum(numpy.multiply(goodCO2,self.calcPercentages[isGoodCO2]))
        else: # assign the remainder between the remaining nan percentages with valid CO2s
            validNonNanPercentages = list(compress(validPercentages,~numpy.isnan(validPercentages)))
            if numpy.sum(validNonNanPercentages) > 1:
                remainder = 0 # overloaded with percentages - nothing left to assign
                paddedPercentages = [0 if numpy.isnan(percentage) else percentage/(numpy.sum(validNonNanPercentages)) for percentage in validPercentages]
            else:
                remainder = 1 - numpy.sum(validNonNanPercentages)         
                paddedPercentages = [remainder/sum(numpy.isnan(validPercentages)) if numpy.isnan(percentage) else percentage for percentage in validPercentages]
            calcPercentages[isGoodCO2] = paddedPercentages
            self.calcPercentages = calcPercentages
            return numpy.sum(numpy.multiply(goodCO2,paddedPercentages))

    @staticmethod
    def percentStr2Float(string_in: str) -> float: # to make more robust
        if len(string_in) == 0:
            return numpy.nan
        #try:
        while string_in[-1]=='%' or string_in[-1]=='.':
            string_in = string_in[:-1]
            if len(string_in) == 0:
                return numpy.nan
        if '-' in string_in:
            splitStr = string_in.split('-')
            returnPercent = numpy.mean([Products.percentStr2Float(subStr) for subStr in splitStr])
        elif string_in[0] == '<':
            returnPercent = 0.5*float(string_in[1:])/100 # assume half the trace value
        elif string_in[0] == '>':
            returnPercent = float(string_in[1:])/100
        elif string_in.count(',') == 1: # comma instead of full stop
            returnPercent = float(string_in.replace(',','.'))/100
        elif len(string_in) > 3 and string_in[0:3] == 'min':
            returnPercent = float(string_in[4:])/100 # strange min format
        else:
            try:
                returnPercent = float(string_in)/100
            except:
                returnPercent = numpy.nan
        return returnPercent

    

