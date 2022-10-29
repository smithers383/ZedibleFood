import numpy as np
import pandas

class Ingredients:
    CO2: float = np.nan
    mainName: str = ''
    supplierName: str = ''
    matchedName: str = ''
    missingName: str = ''
    
    def __init__(self,supplierName: str,\
            mainDB: pandas.DataFrame,\
            userDB: pandas.DataFrame,\
            defaultPercentages: pandas.DataFrame):
        self.mainDB = mainDB
        self.userDB = userDB
        self.defaultPercentages = defaultPercentages
        self.supplierName = supplierName
        self.lookupCO2()

    @property
    def matchedName(self) -> str:
        if self.mainName != self.supplierName  and len(self.mainName) > 0:
            return self.supplierName+'->'+self.mainName
        else:
            return ''
    @property
    def missingName(self) -> str:
        if len(self.mainName) == 0:
            return self.supplierName
        else:
            return ''

    @property
    def foundName(self) -> str:
        if self.mainName == self.supplierName  and len(self.mainName) > 0:
            return self.mainName
        else:
            return ''
    @property
    def found(self) -> bool:
        return not np.isnan(self.CO2)

    @property
    def CO2(self) -> float:
        if not len(self.mainName) == 0:
            CO2perKg = self.mainDB['kg CO2 / kg (ohne Flug)'][self.mainDB['Name EN']==self.mainName].values[0] 
            return CO2perKg
        else:
            return np.nan

    def isDirectMatch(self,matchString: str,dataBase: pandas.DataFrame,title: str) -> bool:
        directMatch = dataBase[title]==matchString # Name EN
        return any(directMatch)
 
    def isDirectPluralMatch(self,matchString: str,dataBase: pandas.DataFrame,title: str) -> bool:
        if self.isPlural(matchString):
            return self.isDirectMatch(matchString[:-1],dataBase,title)
        else:
            return False

    def isCloseMatch(self,matchString: str,dataBase: pandas.DataFrame,title: str) -> bool:
        containtMatch = dataBase[title].str.contains(matchString,regex=False)
        isLong = len(matchString) > 3 
        isMatch = containtMatch.any()
        goodMatch = isLong and isMatch
        return goodMatch
    
    def getCloseMatch(self,matchString: str,dataBase: pandas.DataFrame,title: str) -> str:
        containtMatch = dataBase[title].str.contains(matchString,regex=False)
        closestMatch = min(dataBase[title][containtMatch].values,key=len)
        return closestMatch

    def lookupCO2(self):
        userMainTitle = 'MainDB'
        userSupplierTitle = 'SupplierDB'
        mainDBTitle = 'Name EN'
        # User Match
        if self.isDirectMatch(self.supplierName,self.userDB,userSupplierTitle): 
            try:
                self.mainName = self.userDB[userMainTitle][self.userDB[userSupplierTitle] == self.supplierName].values[0]
            except:
                print("hi")
            return

        # Main DB match
        if self.isDirectMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.supplierName
            return

        if self.isDirectPluralMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.supplierName[:-1]
            return
        
        # User Plural Match
        if self.isDirectPluralMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.userDB[userMainTitle][self.userDB[userSupplierTitle] == self.supplierName[:-1]].values[0]
            return

        if self.isCloseMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.getCloseMatch(self.supplierName,self.mainDB,mainDBTitle)
      
        # it is missing :(


    @staticmethod
    def isPlural(string: str) -> bool:
        if len(string) < 3:
            return False
        else:
            return string[-1] == 's'
