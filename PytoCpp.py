#PytoCPP
#read in and return the parsed python file for processing
def read_file(path):
    print('Parsing Input File') #tell user parsing in progress (if file long may take time)
    file = open(path,'r') #open file from path specified
    lines = [] #define empty list of data
    for line in file: #iterater over lines in file
        newline = line.strip('\n') #remove newline character from line
        lines.append(newline) #store line
    file.close() #close the file as it is finished with
    print('Parsing Completed') #inform user file has been parsed successfuly
    return lines #return line data of file

#check if the line is a comment
def comment_check(line):
    if('#' in line): #primary check for comment character
       new_line = line.replace('\t','') #remove tabs and blank spaces to get raw text
       new_line = new_line.rstrip()
       if(new_line[0]=='#'): #check first character is comment character as not to replace if # found inside string
          converted_line = '//'+new_line[1:] #convert to c++ comment notation
          return converted_line #return converted line
       else: #if # elsewhere in line then line is not a comment
          return False
    else: #if no comment character return line is not a comment
       return False

#check if line is declaration of an integer
def int_check(line):
    if('=' in line and '==' not in line and'[' not in line): #check there is a declaration statement (not comparison)
        splitup = line.split('=') #split the declaration by name and value
        if(splitup[1][0] == '-'): #disregard negative sign if it exists
            if(splitup[1][1:].isdigit()): #check if rest of value is an integer
                converted_line = 'int %s = %s;' % (splitup[0],splitup[1]) #define the string in converted format
                return converted_line #return the converted version of the declaration
            else: #if rest not integers return as such
                return False
        else: #if no negative sign then whole of second element is value
            if(splitup[1].isdigit()): #check if second element an integer
                converted_line = 'int %s = %s;' % (splitup[0],splitup[1]) #define the string in converted format
                return converted_line #return converted format
            else: #if value not integer return as such
                return False    
    else: #if not declaration return line is not integer declaration
        return False

# check if line is declaration of a float
def float_check(line):
    if('=' in line and '==' not in line and '[' not in line): #check there is a declaration statement (not comparison)
        splitup = line.split('=') #split the declaration by name and value
        try: #as integer has already been rules out at this point can just try and float
            float(splitup[1]) #attempt to float the value
            converted_line = 'float %s = %s;' % (splitup[0],splitup[1]) #if made it this far value is float so define converted string
            return converted_line #return the converted line
        except: #if value cannot be floated return that line is not float declaration
            return False
    else: #if not a declaration return line is not a float declaration
        return False

#check if the line is a string declaration
def string_check(line):
    if('=' in line and '==' not in line and '[' not in line):
        if('"' in line or "'" in line): #check if string is defined with single or double quotes
            splitup = line.split('=',1) #splitup the variable name and value
            try:
                str(splitup[1]) #check value is valid string
                #if string starts and ends with single quotes convert to double as required by c++
                if(splitup[1][0]=="'" and splitup[1][len(splitup[1])-1]=="'"):
                    string_format = '"%s"' % splitup[1][1:-1]
                    converted_line = 'string %s = %s;' % (splitup[0],string_format) #make string declaration in double quotes
                else:
                    converted_line = 'string %s = %s;' % (splitup[0],splitup[1]) #if already in double quotes just make string declaration
                return converted_line #return string declaration
            except:
                return False #if making string fails mark line is not a string
        else:
            return False #if no string markers then return not a sstring
    else:
        return False #if no declaration return not a string

#check if print statement in line
def print_check(line):
    if('print(' in line): #check if print function used, bracket to ensure only the function flags positive
        line = line.rstrip() #remove whitespace
        line_separation = line.replace("(","|") #mark bounds of function
        line_separation = line_separation.replace(")","|") #mark bounds of function
        line_split = line_separation.split('|',1) #isolate start of argument
        line_split2 = line_split[1].rsplit('|',1) #isolate end of argument
        try:
            #as with tsring check if single or double quote and enforce double quote if printing string
            if(line_split2[0][0]=="'" and line_split2[0][len(line_split2[1])-1]=="'"):
                string_format = '"%s"' % line_split2[0][1:-1]
                converted_line = "cout << " + string_format + ' << endl;' #make the converted print line
                return converted_line #return the converted line
            else:
                pass
        except:
            pass
        converted_line = line.replace('print(','cout << ')[:-1] #if made it this far then printing variables instead of string
        if(',' in converted_line): #check for comma indicating multiple variables out
            converted_line = converted_line.replace(',',' << ') #convert output for multiple variables in single line
        else:
            pass
        converted_line = converted_line+' << endl;' #complete converted line with end line statement
        return converted_line #return the converted line
    else: #if print not used return thaat line is not print function
        return False

#check if an if statement is in the line
def if_check(line):
    if('if' in line and 'elif' not in line): #if an "if" and not "elif" in the line
        if('True' in line): #convert True to c++ version
            line = line.replace('True','true')
        elif('False' in line): #convert False to c++ version
            line = line.replace('False','false')
        else:
            pass
        condition = line.replace('if(','',1) #isolate the start of the if condition
        condition = condition[:-2] #isolate the end of the if condition
        splitup = condition.split('==') #split the comparison arguments
        try:
            #same checks as string checking
            if(splitup[1][0]=="'" and splitup[1][len(splitup[1])-1]=="'"):
                string_format = '"%s"' % splitup[1][1:-1]
                splitup[1] = string_format
                converted_condition = '=='.join(splitup)
                converted_line = 'if (%s) {' % converted_condition
                return converted_line
            else: #if string in right format then return correctly formatted c++ line
                converted_line = 'if (%s) {' % condition
                return converted_line
        except: #if string fails then other conditions shouldn't need reformatting so just format the if function and return it
            converted_line = 'if (%s) {' % condition
            return converted_line
    else: #if no reference to "if" then mark that it is not in this line
        return False

#check if line contains an else statement
def else_check(line,new_data):
    global indentation_level
    if('else' in line): #if line contains an else statement
        new_data.append(('\t'*indentation_level)+'}\n') #close the previous if statement first
        converted_string = 'else {' #open a new else statement
        return converted_string #return the converted else statement
    else: #if else not in line return it is not found
        return False

#check if an else statement needs closing
def close_else(line,new_data):
    global indentation_level
    previous_tabs = new_data[len(new_data)-1].count('\t') #count the number of tab spaces on the last line
    line_tabs = line.count('\t') #count the number of tab spaces on this line
    if(line_tabs==previous_tabs-1): #if tabs reduced by one
        indentation_level-=1 #decrease indentation level
        new_data.append(('\n'+('\t'*(indentation_level))+'}\n')) #append a close brace to this indentatoin level
    else: #if tabs not reduced do nothing
        pass

#check if the line says pass
def pass_check(line):
    if('pass' in line):
        converted_line = line.replace('pass','') #replace with nothing as else statements can be empty
        return converted_line #return conversion
    else: #if pass not in line mark that it is not
        return False

#check if an elif statement is in the line
def elif_check(line,new_data):
    global indentation_level
    if('elif' in line):
        new_data.append(('\t'*indentation_level)+'}\n') #close the previous if statement
        #fix true and false conditions to c++ version
        if('True' in line):
            line = line.replace('True','true')
        elif('False' in line):
            line = line.replace('False','false')
        else:
            pass
        #isolate the condition of the elif statement
        condition = line.replace('elif(','',1)
        condition = condition[:-2]
        splitup = condition.split('==')
        try: #if a string is in the condition ensure it is formatted appropriately
            if(splitup[1][0]=="'" and splitup[1][len(splitup[1])-1]=="'"):
                string_format = '"%s"' % splitup[1][1:-1]
                splitup[1] = string_format
                converted_condition = '=='.join(splitup)
                converted_line = 'else if (%s) {' % converted_condition
                return converted_line
            else:
                converted_line = 'else if (%s) {' % condition
                return converted_line
        except: #if not then condition will likely be formatted correctly already
            converted_line = 'else if (%s) {' % condition
            return converted_line
    else: #if elif not in line mark this appropriately
        return False

#function to find weather a variable is a string, integer or float
def check_type(variable):
    found_type = False #flag to see if the type is found
    try:
        if(variable[0] == '-'): #disregard negative sign if it exists
            if(variable[1:].isdigit()): #check if rest of value is an integer
                type_found = 'int' #store the type as integer
                found_type = True #mark as found
            else:
                pass
        else: #if no negative sign then whole of second element is value
            if(variable.isdigit()): #check if second element an integer
                type_found = 'int' #store the type as integer
                found_type = True #mark as found
            else:
                pass
    except:
        pass
    if(found_type==False): #if it wasn't integer try to float the value
        try:
            float(variable)
            type_found = 'float' #if succeeded floating store the type as float
            found_type = True #mark type as found
        except:
            pass
    else:
        pass
    if(found_type==False): #if it wasn't int or float check that it works as a string
        try:
            str(variable) #convert value to string, this should always work as the line is string by default
            type_found = 'string' #mark type as a string
            found_type = True #mark the type as found
        except:
            pass
    else:
        pass
    
    if(found_type==True): #if the type was found return it
        return type_found
    else: #if it wasn't raise a type error as type is not supported
        raise TypeError('Error, one or more variables in a function are of a type not yet supported in the conversion, variable: %s caused this error'%variable)
    
#function to check if the line is a function definition
def function_check(line,data,script_data):
    global found_functions
    if('def' in line): #check if definition command in line
        splitup = line.split(' ',1) #split the def command from the function ca;;
        subsplit = splitup[1].split('(',1) #split on the opening brackets of the variable
        function_name = subsplit[0] #the name of the function is the first element of the split
        arguments = subsplit[1][:-2] #the arguments are after the split to the end minus the ):
        arg_list = arguments.split(',') #turn the arguments in to a list 
        for i in range(700,len(script_data)): #loop over the read in script data to find the function 
            if(function_name in script_data[i]):
                function_match = i #store the index of the match
                break
            else:
                pass
        try:
            int(function_match) #check function match found
        except:
            raise NameError('Function name not found, ensure you have commented a call of your function with typical values within this script in the space provided.')
        subsplit2 = script_data[function_match].split('(') #split the call of the function at the bracket
        arguments2 = subsplit2[1][:-2] #as before arguments are to the end of element 1 without )
        try: #series of tests and replacements for if one of the arguments is a list
            #make all square brackets marked with the same symbol
            list_arguments = arguments2.replace('[','|')
            list_arguments = list_arguments.replace(']','|')
            split_arguments = list_arguments.split(',') #split list of arguments on commas
            list_open = False #mark that there is no list open
            final_args = [] #empty list of arguments of function
            for i in range(0,len(split_arguments)): #loop over the split araguments
                if('|' in split_arguments[i] and list_open==False): #if list not open and list marker then open a new list of arguments
                    new_list = [] #define new list for one argument
                    new_element = split_arguments[i].replace('|','') #remove the marker symbol
                    new_list.append(new_element) #add the element to the new list
                    list_open=True #mark a list as opened
                elif('|' in split_arguments[i] and list_open==True): #check if list open and list marker in element
                    new_element = split_arguments[i].replace('|','') #remove the marker
                    new_list.append(new_element) #add the element to the new list
                    final_args.append(new_list) #add the new list to the final argument list as it has been completed
                    list_open=False #mark list as no longer open
                elif(list_open==True): #if list open and it is not the start or end element
                    new_list.append(split_arguments[i]) #add argument to the list
                else: #if a list is not open or due to be opened add the element to the final arguments
                    final_args.append(split_arguments[i])
        except:
            pass
            
        arg_types = [] #list of the types of the arguments for the converted line
        arg_list2 = final_args #rename final arguments
        for i in range(0,len(arg_list2)): #loop over the arguments
            found_type = False #flag to see if type has been identified
            if(isinstance(arg_list2[i],list)): #check if the argument is a list (which will now be formatted from the steps above)
                sub_var_type = [] #make a list of the element types within the list as they all need to be the same for c++
                for j in range(0,len(arg_list2[i])): #loop over the elements inside the list
                    var_type = check_type(arg_list2[i][j]) #test the type of the element
                    sub_var_type.append(var_type) #append it to the list element types list
                if(sub_var_type[1:]==sub_var_type[:-1]): #check if every element of the type list is the same by symmetry as required by c++
                    arg_types.append('vector<%s>'%sub_var_type[0]) #append the appropriate vector type required by c++ as this list's type
                    found_type = True #mark type as found
                else: #if the types in the list are not all the same raise a type error as it is required by c++
                    raise TypeError('Due to the requirements of c++ the elements of a list must all be the same type e.g. a list of floats, a list argument provided does not follow this.')
            if(found_type==False): #if element wasn't a list check the type
                var_type = check_type(arg_list2[i]) #check type of element
                arg_types.append(var_type) #append type to types list
            else:
                pass
        
        function_arguments = [] #make list of final function arguments
        arguments_string = '' #make the arguments string as blank
        for i in range(0,len(arg_types)): #loop over the argument types
            function_arguments.append(arg_types[i]+' '+arg_list[i]) #for each store an element in the function arguments list as "[type] [name]"
            arguments_string=arguments_string+function_arguments[i]+', ' #add the string "[type] [name], " to the total arguments string
        arguments_string = arguments_string[:-2] #remove the extra ", " at the end
        
        converted_line = 'auto %s (%s) {' % (function_name,arguments_string) #make function definition line as auto type for simplicity with the name and arguments filled in as found
        found_functions.append(function_name) #append name of function to global list of found function definitions for later reference
        return converted_line #return the converted function call
    
    else: #if def not in line return that the line is not a function definition
        return False

#check if the line is a simple mathematical statement
def maths_check(line,new_data):
    if('+' in line or '-' in line or '*' in line or '/' in line):
        splitup = line.split('=') #split the stored variable and its equation
        if(splitup[0] not in new_data): #check if the variable name has been previously defined, this method may cause issue if variable names are one letter long as it may flag that the variable is already defined when it actually just has a match due to being a single letter
            line_tabs = line.count('\t') #check the indentation level of the line
            #@todo check if this causes an indentation clash with different indentqtion levels
            #ensure converted line has same indentation level as original and define the variable as a float
            converted_line = ('\t'*line_tabs)+'float %s = %s;' % (splitup[0].replace('\t','').replace(' ',''),splitup[1])
            return converted_line #return gthe c++ line
        else: #if variable has been defined just add a semicolon to the end
            converted_line = line+';'
    else: #if simple operator not in line return that it is not a maths statement
        return False

#function to check if the line is a function return
def return_check(line,new_data):
    if('return' in line):
        splitup = line.split(' ',1) #split the return and its values
        try:
            return_values = splitup[1] #attempt to isolate the values, if this fails the function is a void function so has no return
        except:
            converted_line = line +';\n' #add semicolon and new line to return line
            new_data.append(converted_line) #append the return statement to the converted script
            tabs_count = converted_line.count('\t') #count previous line tabs
            new_data.append((('\t')*(tabs_count-1)+'}\n')) #reduce indentation by one and close the function brace
            return True #any return to not be false
        if(',' in return_values): #if succeeded check if there is multiple return values as this is non-trivial in c++
            return_list = return_values.split(',') #convert the return values in to a list
            for i in reversed(range(0,len(new_data))): #loop backwards through the lines to find the start of the function
                if('auto' in new_data[i]): #function definition line
                    function_start = i #store the index
                else:
                    pass
            var_count=0 #counter for the number of return values found
            result_values = '' #string for the dummy arguments of the result structure
            #@todo need something in place if a var_definition is auto as this is not allowed inside the structure 
            for i in range(function_start,len(new_data)): #loop from the found index to the end of the function
                for j in range(0,len(return_list)): #loop through the list of return values
                    if(return_list[j] in new_data[i]): #if the return value is defined in this line
                        var_count+=1 #add to the variable count
                        var_definition = new_data[i].split(' ')[0] #split line by space and get the first element which is the definition as it is a mathc to the first declaration of the variable
                        var_definition = var_definition.rstrip() #remove white space
                        var_definition = var_definition.replace('\t','') #remove tab space
                        #construct the structure value type string with the names dummy_return_i as it is hard to make it name sensibly
                        result_values = (result_values + var_definition + ' dummy_return_%s' +'; ') % var_count
                    else:
                        pass
            result_values = result_values[:-1] #remove the extra space at the end of the line
            result_structure = 'struct result {%s};' % result_values #construct the result structure with the previously defined arguments
            result_string = '' #define string of the return values
            for i in range(0,len(return_list)): #loop over the number of return arguments found
                result_string = result_string + return_list[i]+', ' #make the return string for the argument of a structure call
            result_string = result_string[:-2] #remove the extra ", " at the end of the line
            return_result = 'return result {%s};' % result_string #make the return statement calling the defined result structure with the initial return values
            tabs_count = line.count('\t') #count previous line tabs
            new_data.append((('\t')*(tabs_count)+result_structure+'\n')) #add the result structure line at the same indentation level
            new_data.append((('\t')*(tabs_count)+return_result+'\n')) #add the return result line at the same indentation level
            new_data.append((('\t')*(tabs_count-1)+'}\n')) #reduce indentation by one and close the function brace
            return True
        else: #if only a single return argument just add semicolon to end
            converted_line = line +';\n' #add semicolon and new line to return line
            new_data.append(converted_line) #append the return statement to the converted script
            tabs_count = converted_line.count('\t') #count previous line tabs
            new_data.append((('\t')*(tabs_count-1)+'}\n')) #reduce indentation by one and close the function brace
            return True #any return to not be false
        
    else: #if return statement not in line mark the line as not a return statement
        return False

#check if there is a function call in the line
def function_call_check(line,new_data):
    global found_functions
    try: #if a function has not been found this division will fail as it will be 1/0 as there should not be a call to a function not yet defined
        1/len(found_functions)
    except: #return false if the division fails
        return False
    for i in range(0,len(found_functions)): #loop over the found functions list
        if(found_functions[i] in line and 'def' not in line): #check if the function name is in the line (and not def so that a match isn't made for the function definition, only the function call)
            if('=' in line): #if storing a return from the function
                splitup = line.split('=') #split on the equals
                if(splitup[0] in new_data):
                    converted_line = '%s=%s;' % (splitup[0],splitup[1]) #if the variable has already been defined then a value can just be stored
                else:
                    converted_line = 'auto %s=%s;' % (splitup[0],splitup[1]) #define a converted line using auto for simplicity of defintion as variable not yet defined
            else: #if not storing the return just add semicolon to the end of the line
                converted_line = line+';'
            return converted_line #return the c++ converted line
        else: #if the function call do nothing to loop over to next one
            pass
    return False #if made it this far no matches were found so return false

#function to check if line is a list definition
def list_check(line):
    #awkward set of comparsons to avoid clashes and only proceed on the declaration of a list
    if('=' in line and '[' in line and ('= [' in line or '=[' in line)):
        splitup = line.split('=',1) #split the list by name and value
        values = splitup[1] #access the values of the list 
        values = values.replace(']','') #remove closing bracket
        values = values.replace('[','') #remove starting bracket
        values = values.split(',') #convert raw comma separated values to a list
        sub_var_type = [] #list to check the types of each element as c++ requires all to be the same
        for i in range(0,len(values)): #iterate over the values
            var_type = check_type(values[i]) #run type check on each value
            sub_var_type.append(var_type) #store the type in the list
        if(sub_var_type[1:]==sub_var_type[:-1]): #check the list is identical by symmetry
            for i in range(0,len(values)): #loop over the values
                if(sub_var_type[0]=='int'): #if the types are all ints convert the value strings to int type values
                    values[i] = int(values[i])
                elif(sub_var_type[0]=='float'): #if the types are all floats convert the value strings to float type values 
                    values[i] = float(values[i])
                else: #if the type is string no conversion needed
                    pass
            #define the converted ddefinition as required by c++ dpecifying vector type and the values
            converted_line = 'vector<%s> %s{ %s };'%(sub_var_type[0],splitup[0],values)
            converted_line = converted_line.replace('[','').replace(']','') #remove the square brackets of the list
            
            return converted_line #return the converted vector definition
        else: #if types are not all the same raise a type error
            raise TypeError('Due to the requirements of c++ the elements of a list must all be the same type e.g. a list of floats, a list argument provided does not follow this.')
    else: #if the set of comparisons not met mark that this line is not a list definition
        return False
        
#function to check if the line contains a for loop
def for_check(line):
    global for_open
    if('for' in line): #check if for is in the line
        for_open = True #mark that a for loop is open
        splitup = line.split(' ') #split the line to get each part of for statement
        iterator = splitup[1] #iterator is defined by this element
        index = splitup.index('in')+1 #find the position of the in and add 1 to get the range
        range_element = splitup[index] #declaration of range given by this index
        isolated_start = False #default flag that the start of the range has not been isolated
        try:
            #if the range command is used split on it to get the arguments
            range_split = range_element.split('range(')[1]
            if(',' in range_split): #if a comma is in place then a start and end point have been specified
                isolated_start_value = range_split.split(',')[0] #the start is isolated by this element
                isolated_start=True #flag start has been isolated
            else:
                pass
        except:
            pass
        
        if('len' in splitup[index]): #check if the length of a list has been used in the for loop iteration
            subsplit = splitup[index].split('len(')[1] #split on len to get the list being compared
            list_to_iterate = subsplit.replace(')','').replace(':','') #remove the close brackets and : to isolate the list name
            converted_len = '%s.size()' % list_to_iterate #replace len(list) with list.size() as the c++ version
            if(isolated_start==True): #if a start value has been isolated make the converted line definition as required by c++ from the specified start to end
                converted_line = 'for (auto %s = %s; %s < %s; %s++) {' % (iterator,isolated_start_value,iterator,converted_len,iterator)
            else: #if a start point has not been isolated then range(number) is argument so default start is 0
                converted_line = 'for (auto %s = 0; %s < %s; %s++) {' % (iterator,iterator,converted_len,iterator)
            return converted_line #return the conversion
        elif('range' in splitup[index]): #check if range has been used in the for loop iteration and len hasn't such that its just range(number)
            subsplit = splitup[index].split('range(')[1] #get the value argument of the range
            range_max = subsplit.replace(')','').replace(':','') #remove the close brackets and : from the value
            #as with len above but for the range max value instead
            if(isolated_start==True):
                converted_line = 'for (auto %s = %s; %s < %s; %s++) {' % (iterator,isolated_start_value,iterator,range_max,iterator)
            else:
                converted_line = 'for (auto %s = 0; %s < %s; %s++) {' % (iterator,iterator,range_max,iterator)
            return converted_line #return the conversion
        else: #if neither for loop is given as for x in list:
            list_to_iterate = splitup[len(splitup)-1].replace(':','') #remove the : from the final element as the list to iterate through
            converted_line = 'for (auto %s : %s) {' % (iterator,list_to_iterate) #write the list iteration as required
            return converted_line #return the conversion
    else: #if for loop not in line return that line is not a for loop
        return False

#function to check if line contains a list append statement
def append_check(line):
    if('append' in line):
        #replace append method with push_back method and remove the tab spaces for later correction
        push_back = line.replace('append','push_back').replace('\t','')
        converted_line = push_back+';' #add semicolon to end statement
        return converted_line #return the conversion
    else: #if append not in line mark the line as not an append statemwnt
        return False

#fuction to check if the line attempts to access an element of a list
def element_access_check(line,new_data):
    if(']=' in line  or '] =' in line): #checks for element access and overwrite
        line = line.replace('\t','') #remove tabs while processing lines
        splitup = line.split('=') #split on the equals to get element acess and value
        update_type = check_type(splitup[1]) #check the type of the value you are trying to overwrite with
        for i in new_data: #iterate through existing lines of converted data
            #check for where the appropriate list is predefined before accessing elements
            if(splitup[0].split('[')[0] in i and 'vector' in i):
                access_type = i.split('<')[1] #get the type of the vector
                isolated_type = access_type.split('>')[0] #remove the second sngle bracket on vector type
                if(isolated_type==update_type): #if the type of the vector is the same as the type that you are trying to overwrite with
                    converted_line = splitup[0] + '=' + splitup[1] + ';' #define the converted overwrite line
                    return converted_line #return the conversion
                else: #if type is not the same raise a type error as overwrite would fail
                    raise TypeError('Due to the requirements of c++ you cannot change an element of a list of type %s to an element of type %s. If you believe this error message to be false then your list may have a name that is contained within another variable.' % (isolated_type,update_type))
            else: #if not pre defined do nothing
                pass
        #if reached this far raise a name error as vector has not been defined
        raise NameError('List %s definition not found' % splitup[0].split('[')[0])
    else: #mark line as not an attempt to access element
        return False

#function to check if line is attempting to store an element of a list under a variable
def store_element_check(line):
    #convoluted set of checks to ensure not clashing with previous list related functions
    if('[' in line and '=[' not in line and '= [' not in line and ']=' not in line and '] =' not in line):
        converted_line='auto %s;' % line.replace('\t','') #define variable type as auto for ease and define conversion
        return converted_line #return the conversion
    else: #if the checks fail mark this line as not an attempt to store a list value under a variable
        return False

#function to iterate over file data and convert line by line to c++
def convert_file(data):
    global open_else, indentation_level, own_data, found_functions, for_open, stored_tabs
    print('Converting Parsed Data') #inform user data being converted incase it takes a while
    new_lines = [] #define list for converted lines
    line_count = 0 #define count of lines for any failed conversion message
    found_functions = [] #define list of function names that have been found
    #check for any reference of strings in file
    if(('str' in x for x in data) or ('"' in x for x in data) or ("'" in x for x in data)):
        new_lines.append('#include <string>\n') #if reference of string found include it for c++
    else: #if no strings do not use include
        pass
    if('print' in x for x in data): #check if reference to print function
        new_lines.append('#include <iostream>\n') #if so include in/out stream for c++
    else: #if no outputs do not use include
        pass
    if('[' in x for x in data): #check if reference to print function
        new_lines.append('#include <vector>\n') #if so include in/out stream for c++
    else: #if no outputs do not use include
        pass
    new_lines.append('using namespace std;\n') #for simplicity provide use the std namespace
    
    indentation_level = 0 #default to 0 indentation
    open_else = False #mark that an else statement is not open
    main = False #mark that a main function has not yet been added
    function_brace_open=False #mark that a function is not open
    for_open = False #mark that a for loop is not open
    stored_tabs = False #mark a stored indentation level for special cases has not been found
    for line in data: #iterate over the data
        function_opened=False #mark that a function was not opened in this line
        line_count+=1 #increase line count, informs user which line of conversion failed if fails
        skip=False #skip flag to do with handling open else statements, functions like the function_opened flag
        line = line.replace('    ','\t') #if indented using quadruple space replace it with tab space

        #check if line is a function definition and if main has been declared yet
        if('def' not in line and main == False and function_brace_open==False):
            new_lines.append('int main() {\n') #initialise main and mark main as defined
            main = True #mark main as initialised
            indentation_level+=1 #increase the indentation level of subsequent lines by 1
        else: 
            function_indicator = function_check(line,data,own_data) #check if the line is a function definition
            if(function_indicator!=False): #if function is defined on this line
                new_lines.append(function_indicator+'\n') #append the converted function definition
                function_opened=True #mark function as opened this iteration
                function_brace_open=True #mark function brace as open as function has not yet been closed off
            else:
                pass
        
        if(for_open==True): #check if for loop is open
            tab_count = new_lines[len(new_lines)-1].count('\t') #count the indentation of the previous line
            if(stored_tabs==False): #if the value has not been stored (the first line after opening the for loop)
                stored_tabs = new_lines[len(new_lines)-1].count('\t') #store the tab count
            else: #if value has been stored compare it to the new value
                #if the new value is less than the sotred or the end of the file has been reached
                if(tab_count<stored_tabs or line_count==len(data)):
                    indentation_level-=1 #reduce the indentation level as for loop is finished
                    new_lines.append(('\t'*indentation_level)+'}\n') #add a close brace to the for loop
                    stored_tabs = False #reset stored tabs back to False
                else:
                    pass
        else:
            pass
        
        #run line through appropriate checking functions to determine type and convert
        comment = comment_check(line)
        integer_declaration = int_check(line)
        float_declaration = float_check(line)
        string_declaration = string_check(line)
        print_out = print_check(line)
        if_condition = if_check(line)
        else_condition = else_check(line,new_lines)
        pass_declaration = pass_check(line)
        elif_condition = elif_check(line,new_lines)
        maths_declaration = maths_check(line,new_lines)
        return_declaration = return_check(line,new_lines)
        function_call = function_call_check(line,new_lines)
        list_declaration = list_check(line)
        for_call = for_check(line)
        append_call = append_check(line)
        element_update = element_access_check(line,new_lines)
        store_declaration = store_element_check(line)
        
        #all functions return false if line is not of that type, if it is add converted line to converted lines list
        if(comment!=False):
            new_lines.append(('\t'*indentation_level)+comment+'\n')
        elif(integer_declaration!=False):
            new_lines.append(('\t'*indentation_level)+integer_declaration+'\n')
        elif(float_declaration!=False):
            new_lines.append(('\t'*indentation_level)+float_declaration+'\n')
        elif(string_declaration!=False):
            new_lines.append(('\t'*indentation_level)+string_declaration+'\n')
        elif(print_out!=False):
            new_lines.append(('\t'*indentation_level)+print_out+'\n')
        elif(if_condition!=False):
            new_lines.append(('\t'*indentation_level)+if_condition+'\n')
        elif(else_condition!=False):
            new_lines.append(('\t'*indentation_level)+else_condition+'\n')
            open_else = True
            skip=True
            indentation_level+=1
        elif(pass_declaration!=False):
            new_lines.append(('\t'*indentation_level)+'\n')
        elif(elif_condition!=False):
            new_lines.append(('\t'*indentation_level)+elif_condition+'\n')
        elif(maths_declaration!=False):
            new_lines.append(('\t'*indentation_level)+maths_declaration+'\n')
        elif(return_declaration!=False):
            function_brace_open=False
        elif(function_call!=False):
            new_lines.append(('\t'*indentation_level)+function_call+'\n')
        elif(list_declaration!=False):
            new_lines.append(('\t'*indentation_level)+list_declaration+'\n')
        elif(for_call!=False):
            new_lines.append(('\t'*indentation_level)+for_call+'\n')
            indentation_level+=1
        elif(append_call!=False):
            new_lines.append(('\t'*indentation_level)+append_call+'\n')
        elif(element_update!=False):
            new_lines.append(('\t'*indentation_level)+element_update+'\n')
        elif(store_declaration!=False):
            new_lines.append(('\t'*indentation_level)+store_declaration+'\n')
        else: #if it is not a known type of line inform user conversion failed on appropriate line and add it commented out with warning that this line has not yet been converted
            if(function_opened == True):
                pass
            else: #if no type could be identifited by existing checks
                #comment out the line marking it as a faile conversion and the line's original value for manual conversion by the user
                new_lines.append(('\t'*indentation_level)+'//Failed conversion - %s\n' % line)
                #inform the user which line of their script failed
                print('Conversion Failed On Line %i' % line_count) 
        
        if(open_else==True and skip==False): #check if an else statement is open and wasn't opened this line
            #similar indentation comparison as above with for loops to check if the else needs closing
            previous_tabs = new_lines[len(new_lines)-1].count('\t')
            line_tabs = line.count('\t')
            if(line_tabs<previous_tabs or line_count==len(data)):
                indentation_level-=1
                new_lines.append(('\t'*indentation_level)+'}\n')
                open_else=False
            else:
                pass
        else:
            pass
        
    while(indentation_level>1): #if the end of the file has been reached and not all braces are closed
        #close a brace then add a new line
        new_lines.append(('\t'*indentation_level)+'}\n')
        #reduce indentation level by 1
        indentation_level-=1
    
    new_lines.append('\treturn 0;\n') #return for main function
    new_lines.append('}') #closing brace of main function
    
    print('Conversion Completed') #inform user conversion has finished
    return new_lines #return the converted data

#function to write converted data to cpp file
def write_file(path,data):
    print('Writing C++ File') #inform user writing has started
    file = open(path,'w+') #open or create specified path and file for writing
    for i in range(0,len(data)): #iterate over data
        file.write(data[i]) #write line of data to file
    file.close() #close file
    print('Writing Completed') #inform user writing has finished
    print('C++ File Generation Finished') #inform user program has finished






"""
please comment all calls to any functions within your file with typical input
values in order to convert them below
"""
#TestFunction(1,[2.2,3.3,4.4],'Hello',2.2)






#messy way to read user inputs to this script and to figure out the argument types for function calls
file = open('PytoCpp.py','r')
own_data = []
for line in file:
    own_data.append(line)
file.close()

parsed_file = read_file('Test.py') #read in file function call
converted_data = convert_file(parsed_file) #data conversion function call
write_file('Test.cpp',converted_data) #write file function call

#print(converted_data) #uncomment this line if you want to see the converted line list













