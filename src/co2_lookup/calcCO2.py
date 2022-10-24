from cmath import nan
from Ingredients import Ingredients
import numpy

def percentStr2Float(string_in: str) -> float: # to make more robust
    if len(string_in) == 0:
        return numpy.nan
    
    while string_in[-1]=='%':
        string_in = string_in[:-1]
    if '-' in string_in:
        splitStr = string_in.split('-')
        returnPercent = numpy.mean([percentStr2Float(subStr) for subStr in splitStr])
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

def calcCO2(dict_in,mainDB,userDB):
    if len(dict_in) == 0:
        return numpy.nan
    percentages = [numpy.nan] * len(dict_in)
    CO2perKG = [numpy.nan] * len(dict_in)
    ingredientList = [Ingredients] * 0
    for i, ingredientStr in enumerate(dict_in):
        ingredient = Ingredients(ingredientStr,mainDB,userDB)
        if len(dict_in[ingredientStr][1]) == 0 or ingredient.found:
            percentValStr = dict_in[ingredientStr][0]
            percentages[i] = percentStr2Float(percentValStr) 
            CO2perKG[i] = ingredient.CO2
            ingredientList.append(ingredient)
        else:
            sub_ingredients = dict_in[ingredientStr][1]
            returnList = calcCO2(sub_ingredients,mainDB,userDB)
            CO2perKG[i] = returnList[0]
            ingredientList.extend(returnList[1])

    CO2NanFix = [val if numpy.isnan(val) else 1 for val in CO2perKG]
    calcPercentages = numpy.multiply(CO2NanFix,percentages)
    # fix percentages
    if any(numpy.isnan(calcPercentages)):
        sumNotNaN = sum([percentVal for percentVal in calcPercentages if not(numpy.isnan(percentVal))])
    else:
        sumNotNaN = 0
    remainderPercent = 1 - sumNotNaN
    if any(numpy.isnan(calcPercentages)):
        unScaledPercentages = [remainderPercent/sum(numpy.isnan(calcPercentages)) if numpy.isnan(percentVal) else percentVal for percentVal in calcPercentages]
    else:
        unScaledPercentages = calcPercentages
    # scale up to 1
    tmpMult = numpy.multiply(unScaledPercentages,CO2NanFix)
    percentageSum = sum(tmpMult[~numpy.isnan(tmpMult)])
    if percentageSum != 1 and percentageSum != 0:
        finalPercentages = unScaledPercentages/percentageSum
    else:
        finalPercentages = unScaledPercentages
    tmpMult = numpy.multiply(finalPercentages,CO2perKG)
    returnCO2 = sum(tmpMult[~numpy.isnan(tmpMult)])
    
    if returnCO2 == 0:
        returnList = [numpy.nan, ingredientList ]
        return returnList
    else:
        returnList = [returnCO2, ingredientList ]
        return returnList


