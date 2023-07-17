from tkinter.messagebox import showwarning
import numpy as np
import pandas
ratioDB = pandas.DataFrame(columns=['SupplierDB','MainDB'])
from Levenshtein import ratio

THRESHOLD = 0.6
DEBUG=True

class Ingredients:
    CO2: float = np.nan
    mainName: str = ''
    mainNameNoSub: str = ''
    category: str = ''
    supplierName: str = ''
    ratioName: str = ''
    matchedName: str = ''
    missingName: str = ''
    autoMatchName: str = ''
    def __init__(self,supplierName: str,\
            mainDB: pandas.DataFrame,\
            userDB: pandas.DataFrame,\
            defaultPercentages: pandas.DataFrame):
        self.mainDB = mainDB
        self.userDB = userDB
        self.defaultPercentages = defaultPercentages
        self.supplierName = supplierName

    @property
    def category(self) -> str:
        if self.mainName != '':
            return self.mainDB['Categorie'][self.mainDB['Name EN']==self.mainName].values[0] 
        else:
            return ''

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
            try:
                CO2perKg = float(self.mainDB['kg CO2 / kg (ohne Flug)'][self.mainDB['Name EN']==self.mainName].values[0]) 
            except:
                print("help")
            return CO2perKg
        else:
            return np.nan

    def isDirectMatch(self,matchString: str,dataBase: pandas.DataFrame,title: str) -> bool:
        directMatch = dataBase[title]==matchString # Name EN
        return any(directMatch)

    def isRatioMatch(self,matchString: str,dataBase: pandas.DataFrame,title: str,) -> bool:
        global ratioDB
        if any(ratioDB['SupplierDB']==matchString):
            self.ratioName = ratioDB['MainDB'][ratioDB['SupplierDB']==matchString].values[0]
            return True
            

        match_found = False
        curScore = 0
        best_match = ''
        for master_ingredient in dataBase["Name EN"]:
            score = ratio(matchString, master_ingredient)
            if score > curScore:
                curScore = score
                best_match =  master_ingredient
                if curScore >= THRESHOLD and curScore:
                    curScore = score
                    match_found = True
                    self.ratioName = master_ingredient
                    if DEBUG and match_found: 
                        print('Score: {:.2f} for {} to {}'.
                            format(score, matchString, master_ingredient))
                    #print('match: {} ~ {}, score: {:.2f}'.format(supplier_ingredient,master_ingredient,score))
        
        if DEBUG and 1 == 0:
            if not match_found:
                print('not matched: supplier ingr: {}, best match: {}, Score: {:.2f}'.
                    format(matchString,best_match, curScore))
        if match_found:
            ratioDB = pandas.concat([ratioDB,pandas.DataFrame({'SupplierDB':matchString,'MainDB':self.ratioName},[1])],ignore_index=True)
        return match_found

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
        #showwarning('Close match',['Identified close match:'+matchString +' to '+closestMatch])
        return closestMatch

    def lookupCO2(self):
        userMainTitle = 'MainDB'
        userSupplierTitle = 'SupplierDB'
        mainDBTitle = 'Name EN'

        # Main DB match
        if self.isDirectMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.supplierName
            self.mainNameNoSub = self.mainName
            return

        # User Match
        if self.isDirectMatch(self.supplierName,self.userDB,userSupplierTitle): 
            self.mainName = self.userDB[userMainTitle][self.userDB[userSupplierTitle] == self.supplierName].values[0]
            if self.isDirectMatch(self.mainName,self.mainDB,mainDBTitle): # check it is actually in mainDB
                return
            ratioMatch = self.isRatioMatch(self.mainName,self.mainDB,mainDBTitle)
            if ratioMatch:
                self.mainName = self.ratioName
                self.autoMatchName = self.ratioName
                #update user sheet for speed.
                return # updatedDB
            else:
                returnMessage = "Substitute name:"+self.mainName+" not found in main database\n\
                    No user substitue made for:"+self.supplierName

                self.mainName = ''
                showwarning(title=None, message=returnMessage)


        if self.isDirectPluralMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.supplierName[:-1]
            self.mainNameNoSub = self.mainName
            return
        
        # User Plural Match
        if self.isDirectPluralMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.userDB[userMainTitle][self.userDB[userSupplierTitle] == self.supplierName[:-1]].values[0]
            self.mainNameNoSub = self.mainName
            if self.isDirectMatch(self.mainName,self.mainDB,mainDBTitle): # check it is actually in mainDB
                return
            else:
                self.mainName = ''
                self.mainNameNoSub = self.mainName


        # Ratio Match
        
        if self.isRatioMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.ratioName
            self.mainNameNoSub = self.mainName

            self.autoMatchName = self.ratioName
            return

        if self.isCloseMatch(self.supplierName,self.mainDB,mainDBTitle):
            self.mainName = self.getCloseMatch(self.supplierName,self.mainDB,mainDBTitle)
            self.mainNameNoSub = self.mainName
            self.autoMatchName = self.mainName
        # it is missing :(


    @staticmethod
    def isPlural(string: str) -> bool:
        if len(string) < 3:
            return False
        else:
            return string[-1] == 's'
