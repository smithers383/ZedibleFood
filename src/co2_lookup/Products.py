from logging import exception
import numpy
import pandas
from Ingredients import Ingredients
from itertools import compress
import warnings
class Products:


    def __init__(self, \
            ingredientStringDict: dict,\
            mainDB: pandas.DataFrame,\
            userDB: pandas.DataFrame):
        self.ingredientStringDict = ingredientStringDict
        self.mainDB = mainDB
        self.userDB = userDB
        self.calcPercentages = []
        self.ingredients = self.getIngredients()
        self.subProducts = self.getSubProducts()
        
        
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
    def supplierIngredients(self) -> str:
        productName = [item.supplierName for item in self.ingredients if len(self.ingredients) > 0 and len(item.supplierName) > 0]
        calcPercentages = self.calcPercentages
        product = [product+" {:0.1f}%".format(calcPercentages[i]*100) for i, product in enumerate(productName)]

        if self.anySubIngredients:
            subProductsLists = [subProduct.supplierIngredients for subProduct in self.subProducts if len(subProduct.supplierIngredients) > 0 ]
            subProducts = [product for listProducts in subProductsLists for product in listProducts ]
            returnProducts = product+subProducts
        else:
            returnProducts  = product
        
        if len(returnProducts) == 0:
            return ''
        else:
            return returnProducts

    @property
    def percentages(self) -> float:

        percentages = [self.percentStr2Float(self.ingredientStringDict[percentValStr][0])\
            for percentValStr in self.ingredientStringDict]

        return percentages
    
    
    def getIngredients(self):
        return [Ingredients(ingredientStr,self.mainDB,self.userDB) for ingredientStr in self.ingredientStringDict]

    @property
    def anySubIngredients(self):
        return any([len(self.ingredientStringDict[ingredientStr][1])>0 for ingredientStr in self.ingredientStringDict])

    def getSubProducts(self):    
        return [Products(self.ingredientStringDict[ingredient.supplierName][1],self.mainDB,self.userDB)\
             for ingredient in self.ingredients]

       # return [Products(self.ingredientStringDict[ingredient.supplierName][1],self.mainDB,self.userDB)\
       #      if len(self.ingredientStringDict[ingredient.supplierName][1]) > 0 else None for ingredient in self.ingredients]

    @property
    def CO2(self) -> list:
        ingredientCO2 = [subIngredient.CO2 for subIngredient in self.ingredients]
        if not self.anySubIngredients:
            returnCO2 = ingredientCO2
        else:
            subProductCO2 = [product.totalCO2 for product in self.subProducts]       
            returnCO2 = [CO2[0] if not numpy.isnan(CO2[0]) else CO2[1] \
                for CO2 in zip(ingredientCO2,subProductCO2)]          
        return returnCO2
    
    @property
    def totalCO2(self) -> float:
        calcPercentages = numpy.zeros(len(self.CO2))
        if len(self.CO2) == 0: # no data
            self.calcPercentages = calcPercentages
            return numpy.nan
        isGoodCO2 = ~numpy.isnan(self.CO2)
        validPercentages = list(compress(self.percentages,isGoodCO2))
        goodCO2 = list(compress(self.CO2,isGoodCO2))
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
        while string_in[-1]=='%':
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
            returnPercent = float(string_in)/100
        return returnPercent
#        except:
            ##warnings.warn("Can't parse "+string_in+" accurately")
            #return numpy.nan
    

