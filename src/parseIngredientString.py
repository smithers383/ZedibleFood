import numpy


def checkIsPercentage(string_in):
    if len(string_in)<2:
        return False
    if string_in.count('%') > 1 or string_in.count('%') == 0:
        if string_in.count('-') > 0 and all([checkIsPercentage(splitStr) for splitStr in string_in.split('-')]):
            return True
        else:
            return False
    elif string_in.count('%')  == 1:
        return True

def extractPercent(string_in):
    isPercentStr = True
    remainderStrBack = ''
    percentStrBack = ''
    entryBracket = False
    surroudBracket = False
    if string_in[-1] == ',': #rmeove trailing comma
        string_in = string_in[:-1]

    for stringChar in reversed(string_in):
            
        if ((stringChar=='%') or isPercentStr) and \
            (str.isnumeric(stringChar) or \
                (stringChar=='.') or \
                    (stringChar=='%') or \
                        (stringChar=='<') or \
                            (stringChar == '-')):
            isPercentStr = True
            if len(remainderStrBack) > 0 and (remainderStrBack[-1] == ']' or remainderStrBack[-1] == ')'):
               entryBracket = True
        else:
            surroudBracket = entryBracket \
                and isPercentStr \
                and len(remainderStrBack) > 0 \
                and (stringChar == '[' or stringChar == '(')
            isPercentStr = False
        if isPercentStr:
            percentStrBack+=stringChar
        else:
            remainderStrBack+=stringChar
            if surroudBracket:
                remainderStrBack = remainderStrBack[:-2]   
    returnStr =[remainderStrBack[::-1], percentStrBack[::-1]]
    return returnStr

def parseIngredientString(string_in):
    in_bracket_string = ''
    in_bracket = 0
    split_string = ''
    outDict=dict()
    in_bracket_dict = dict()
    percentStr = ''
    processBracket = False
    processString = False
    if not(isinstance(string_in,str)) and numpy.isnan(string_in):
        return outDict
    for i, string_char in enumerate(string_in):
        # handle dodgy chars
        if string_char == '�':
            continue    
        if string_char == '\r':
            string_char = ' '
            continue
        elif string_char == '\n':
            string_char = ',' # assume a split
        elif string_char == ':':
            string_char = ',' # assume a split
        # if open bracket - climb in   
        if string_char == '(' or string_char == '[':
            in_bracket+=1

        if string_char == ')' or string_char == ']':
            in_bracket-=1
            if in_bracket == 0:
                processBracket = True

        # if in a bracket - add string to the bracket
        if processBracket or in_bracket > 0:
            in_bracket_string+=string_char
        else:
            split_string+=string_char

        if i == len(string_in)-1:
            processString = True  
            if in_bracket > 0:
                in_bracket_string+=')'*in_bracket #close the brackets

        if string_char == ',' and in_bracket == 0:
            processString = True
            #remove comma
            split_string = split_string[:-1]

        if processString:
            name = split_string.strip()
            if '%' in split_string:
                nameAndPercentList = extractPercent(split_string)
                name = nameAndPercentList[0].strip() # update name
                if len(percentStr) > 0:
                    Warning("Can't parse "+string_in+" accurately")
                percentStr =nameAndPercentList[1]
                outDict[name] = [percentStr,in_bracket_dict]
            elif len(name) > 0: #no percentage
                outDict[name] = [percentStr,in_bracket_dict]
            #reset
            split_string = ''
            percentStr = ''
            in_bracket_string = ''
            in_bracket_dict = dict()
            processBracket = False
            processString = False

        if processBracket: #bracket has closed before a comma
            # try parse the bracket
            outParse = parseIngredientString(in_bracket_string[1:-1])
            if checkIsPercentage(in_bracket_string) and len(outParse) < 2:
                if len(percentStr) > 0:
                    Warning("Can't parse "+string_in+" accurately")
                nameAndPercentList = extractPercent(in_bracket_string)
                percentStr = nameAndPercentList[1]
            elif not(',' in in_bracket_string): # no items or a percentage probably part of name
                split_string+=in_bracket_string
            else:
                if len(in_bracket_dict) > 0:
                    Warning("Can't parse "+string_in+" accurately")
                in_bracket_dict = parseIngredientString(in_bracket_string[1:-1])
            #reset
            processBracket = False
            in_bracket_string = ''
    return outDict