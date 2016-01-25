# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 17:32:38 2012

License: GPL version 3.0
January 25, 2016
Copyright:

This file is part of AutoPatcher_IG.

    AutoPatcher_IG is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    AutoPatcher_IG is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with AutoPatcher_IG.  If not, see <http://www.gnu.org/licenses/>.

@Author: Brendan Callahan, Alexander A. Chubykin

"""

#===============================================================================
# EQUATION SYNTAX
#===============================================================================
#
#Equivalency expressions must be in the form CHANNEL, OPERATOR, VALUE,
#e.g. A1 >= -40.2   This is because these components are looked for in order.
#Boolean evaluated expressions must be separated by parenthesis, 
#e.g. (A1 >= -40.2) & (B2 <= 51).  Nested Boolean operations are fine.
#Supported Boolean operators are AND '&', OR '|', and XOR '^'.  Note that
#XOR support is not explicitly built into Python, it just uses the != operator 
#to make sure two boolean variables have opposite values.

class LogicParser():
    def __init__(self,diginputin):
        self.digitalInput = diginputin
        self.dict = dict({'A1':lambda:self.digitalInput.getVal(0,0),'A2':lambda:self.digitalInput.getVal(0,1),'A3':lambda:self.digitalInput.getVal(0,2),'A4':lambda:self.digitalInput.getVal(0,3)})
        self.booleanoperators = ['&','|','^']  
    
    #This function is the start of parsing a string.  Pass a string here to evaluate it.
    def parseString(self,stringin):    
        self.string = stringin
        #get rid of any spaces        
        for char in self.string:
            if char == ' ':
                self.string = self.string.replace(char,'')
        return self.evalExpression(self.string)
        
        
    #This is a recursive function that breaks a string down into components based
    #on parenthesis and content, evaluating expressions from the bottom up    
    def evalExpression(self,stringin):
        
        #start going through characters
        for i in range(0,len(stringin)):
            #if the character is a parenthesis, figure out where its corresponding
            #close parenthesis is
            if stringin[i] == '(':
                #print"paren found"
                startparen = i #location of first parenthesis
                endparen = None #location of second parenthesis
                parencount = 1 #keeps track of how many other parenthesis we have passed
                
                for j in range(i+1,len(stringin)): #start counting
                    
                    if stringin[j] == ')': #if the character is a closed parentesis, subtract one
                        parencount -= 1
                    elif stringin[j] == '(': #if it's open, add one
                        parencount += 1
                    
                    if parencount == 0: #once it's at 0, we've found the corresponding close parenthesis
                        endparen = j
                        #print "Inside paren",stringin[startparen+1:endparen]
                        
                        #If we're now at the end of the string (i.e. the parenthesis are
                        #around the expression but do nothing else), recursively evaluate the
                        #interior of the parenthesis by passing that part of the string to this same
                        #function.
                        if endparen == len(stringin)-1:                        
                            return self.evalExpression(stringin[startparen+1:endparen])
                        
                        #Otherwise, evaluate the interior of the parenthesis, then look after
                        #the close parenthesis for a boolean operator.  Finally, pass whatever
                        #comes after the Boolean operator for evaluation, and then return the 
                        #result of the full Boolean expression.
                        else:
                            if stringin [j+1] in self.booleanoperators:
                                if stringin[j+1] == '|':
                                    #print "OR",stringin[startparen+1:endparen],stringin[j+2:len(stringin)]
                                    return self.evalBool('or',self.evalExpression(stringin[startparen+1:endparen]),self.evalExpression(stringin[j+2:len(stringin)]))
                                if stringin[j+1] == '&':
                                    #print "AND",stringin[startparen+1:endparen],stringin[j+2:len(stringin)]                                  
                                    return self.evalBool('and',self.evalExpression(stringin[startparen+1:endparen]),self.evalExpression(stringin[j+2:len(stringin)]))
                                if stringin[j+1] == '^':
                                    #print "XOR",stringin[startparen+1:endparen],stringin[j+2:len(stringin)]
                                    return self.evalBool('xor',self.evalExpression(stringin[startparen+1:endparen]),self.evalExpression(stringin[j+2:len(stringin)]))
            #We have found the start of an equivalency expression.  Equivalency expressions are always
            #detected via a letter - thus, channel names must start with a letter (e.g. A1).
            #These expressions can be evaluated all at once (sans recursion) because it should 
            #not contain parenthesis (as of now)
            elif stringin[i].isalpha():
                #print "alpha found at",i
                
                #Figure out the channel name by looking for further letters or digits...
                startchannelname = i
                while stringin[i].isalpha() or stringin[i].isdigit():
                    i +=1
                channelname = stringin[startchannelname:i]
                #...and retrieve its current value from the dictionary.
                channelval = self.dict.get(channelname)()
                
                #print "Channel",channelname,"value",channelval
                
                #Next, check for the operator that's supposed to follow the expression
                operator = None
                while(True):
                    if stringin[i] == '<' or stringin[i] == '>' or stringin[i] == '=' or stringin[i] == '!':
                        #2 character equivalence operator                       
                        if stringin[i+1] == '=':
                            if stringin[i]+stringin[i+1] == '==':
                                operator = 'isEq'
                                break
                            if stringin[i]+stringin[i+1] == '!=':
                                operator = 'isNotEq'
                                break
                            if stringin[i]+stringin[i+1] == '>=':
                                operator = 'isGreaterOrEq'
                                break
                            if stringin[i]+stringin[i+1] == '<=':
                                operator = 'isLessOrEq'
                                break
                        #one character equivalence operator
                        else:
                            if stringin[i] == '>':
                                operator = 'isGreater'
                                break
                            if stringin[i] == '<':
                                operator = 'isLess'
                                break
                    else:
                        i += 1
                        
                #print "OPERATOR: "+operator
                
                #Finally, find the digit that's supposed to follow the operator.  Negatives and 
                #decimals are ok.
                while(i < len(stringin)):
                    if stringin[i].isdigit() or stringin[i] == '-' or stringin[i] == '.':
                        startdigit = i
                        i+=1
                        break
                    else:
                        i +=1
                        
                if (i < len(stringin)):
                    while stringin[i].isdigit() or stringin[i] == '.':
                        i+=1
                        if i == len(stringin):
                            break
            
                    
                #print stringin[startdigit:i]
                digit = float(stringin[startdigit:i])                        
                  
                #Once we have the channel value, equivalency operator, and digit, 
                #evaluate the expression and return its value.
                if operator == 'isEq':
                    return channelval == digit
                if operator == 'isNotEq':
                    return channelval != digit
                if operator == 'isGreaterOrEq':
                    return channelval >= digit
                if operator == 'isLessOrEq':
                    return channelval <= digit
                if operator == 'isGreater':
                    return channelval > digit
                if operator == 'isLess':
                    return channelval < digit

    def evalBool(self,operator,bool1,bool2):
        if operator == 'or':
            return bool1 or bool2
        if operator == 'and':
            return bool1 and bool2
        if operator == 'xor':
            return bool1 != bool2                    

#parser = LogicParser()   
#string = "(B2 != -50.7)&((A1 >= 30)|(A3>20))"
#parser.parseString(string)