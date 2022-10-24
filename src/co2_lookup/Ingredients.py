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
            userDB: pandas.DataFrame):
        self.mainDB = mainDB
        self.userDB = userDB
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

    def isDirectMatch(self,matchString: str) -> bool:
        directMatch = self.mainDB['Name EN']==matchString
        return any(directMatch)

    def isUserMatch(self,matchString: str) -> bool:
        userMatch = self.userDB['Item'] == matchString
        return any(userMatch)
 
    def isUserPluralMatch(self,matchString: str) -> bool:
        if self.isPlural(matchString):
            return self.isUserMatch(matchString[:-1])
        else:
            return False

    def isDirectPluralMatch(self,matchString: str) -> bool:
        if self.isPlural(matchString):
            return self.isDirectMatch(matchString[:-1])
        else:
            return False

    def isCloseMatch(self,matchString: str) -> bool:
        containtMatch = self.mainDB['Name EN'].str.contains(matchString,regex=False)
        isLong = len(matchString) > 3 
        isMatch = containtMatch.any()
        goodMatch = isLong and isMatch
        return goodMatch
    
    def getCloseMatch(self,matchString: str) -> str:
        containtMatch = self.mainDB['Name EN'].str.contains(matchString,regex=False)
        closestMatch = min(self.mainDB['Name EN'][containtMatch].values,key=len)
        return closestMatch

    def lookupCO2(self):
        if self.isUserMatch(self.supplierName): 
            self.mainName = self.userDB['SupplierDB'][self.userDB['Item'] == self.supplierName].values[0]
            return

        if self.isDirectMatch(self.supplierName):
            self.mainName = self.supplierName
            return

        if self.isDirectPluralMatch(self.supplierName):
            self.mainName = self.supplierName[:-1]
            return

        if self.isUserPluralMatch(self.supplierName):
            self.mainName = self.userDB['SupplierDB'][self.userDB['Item'] == self.supplierName[:-1]].values[0]
            return

        if self.isCloseMatch(self.supplierName):
            self.mainName = self.getCloseMatch(self.supplierName)
      
        # it is missing :(


    @staticmethod
    def isPlural(string: str) -> bool:
        if len(string) < 3:
            return False
        else:
            return string[-1] == 's'
