#script to read python code in to an AST, parse and replace nodes with corresponding
#c++ code

#make relevant imports
import ast
import numpy as np

#parser class for function definitions
class FunctionParser(ast.NodeVisitor):
    def visit_FunctionDef(self, node): #visit the function definition node
        #define relevant globals that require access
        global converted_lines, function_body, arg_vars, list_types, class_args
        arg_vars = [] #list of arguments
        args_string = '' #argument string for conversion
        init_arg = [] #store a list of arguments to initialise, done for use in any class definitions
        
        for i in range(0,len(node.args.args)): #iterate over the node arguments
            arg_val = node.args.args[i].arg #for each arg get the arg name
            init_arg.append(arg_val) #append the arg name to the list of args to initialise
        
        #class arguments usually start with self, self is not required for c++
        #a type won't have been defined in the function call for self, therefore if different number of list types to arguments
        #and first argument is self, remove the argument so the list of types and arguments matches up again
        if((len(init_arg) != len(list_types[0])) and init_arg[0] == 'self'): 
            init_arg.pop(0)
        else:
            pass
        
        #iterate over the arguments to initialise
        for i in range(0,len(init_arg)):
            arg_type = list_types[0][i] #get the types of the first function's arguments
            full_arg = arg_type + ' ' + init_arg[i] #define a full argument string as the type and name
            arg_vars.append(full_arg) #add the full arg definition to list
            args_string += full_arg + ', ' #add the full arag definition to the arg string
        args_string = args_string[:-2] #remove extra ', ' at the end of the line
        list_types.pop(0) #remove the arg types for the arguments that have just been processed
        
        #if the name of the function is a class initialilser run a special case
        if(node.name == '__init__'):
            class_initialiser = [] #block for class initialisation function
            class_initialiser.append('public:') #mark following class variables as public for initalising the object
            class_args = init_arg #set the class args as a copy of the initialiser args
            for i in node.body: #iterate over the body of the initialiser function
                line = general_access_node(i) #classify and convert the line of the function
                splitup = line.split(' ') #split the converted line by space to inspect elements
                #the following is a messy way to initialise class variables, if it is an initialisation the line will be in the
                #style std::string name = "name"; which is incorrect formatting due to how these statements are processed elsewhere
                try:
                    #check if the first argument of splitup (name) is equal to the final element of splitup inside quotations
                    #and without the ; ("name";).
                    if(splitup[1] == ("%s" % splitup[3][:-1]).replace('"','')):
                        #if it is then its a variable declaration, take the converted arg_vars declaration and add a semicolon
                        #it will now be in the form std::string name; (or other appropriate type of variable)
                        string_val = arg_vars[0]+';' 
                        class_initialiser.append(string_val) #append the new string to the block
                        arg_vars.pop(0) #remove the arg_var as it has been declared in block
                    else: #if it doesn't match just append the line
                        class_initialiser.append(line)
                except: #if splitup element access fails just append the line as the above condition will not occur
                    class_initialiser.append(line)
            return class_initialiser #return the initialised class function
        else:
            pass
        
        function_body = [] #define list for the main body of the function
        for i in node.body: #iterte over the nodes in the body of the function
            if(type(i) == ast.Return): #check if the line is a return function
                line = ReturnParser().visit_Return(i) #visit the return parser function
                if(line == None): #if return is a void return
                    function_body.append('return') #add a void return to the body
                else: #if return has arguments
                    return_types = [] #make a list of the types of values being returned
                    for j in range(0,len(line)):  #iterate over the return values listed
                        for i in reversed(range(0,len(function_body))): #iterate backwards over the body of the function (find the latest definitions of the variables)
                            declaration_check = ' %s = ' % line[j] #check for a definition of the variable
                            if(declaration_check not in function_body[i]): #if there is not a definition of the variable on this line of the function body skip it
                                pass
                            else: #if a definition is found isolate they type by taking the first word and add it to the return types list
                                return_types.append(function_body[i].split(' ')[0])
                    #if there is only one return value a normal return can be used 
                    if(len(return_types) == 1):
                        #add the return and the value to the function body
                        function_body.append('return %s;' % line)
                    else: #if multiple values are required generate a structure to return
                        struct_string = 'struct result {' #initialise structure string
                        for i in range(0,len(line)): #iterate over the number of arguments
                            #add (value_type dummy_return_[number];) to the structure string  
                            struct_string += return_types[i] + ' dummy_return_%s; ' % str(i)
                        #remove the extra space, close the struct bracket and end statement for struct definition
                        struct_string = struct_string[:-1] + '};'
                        function_body.append(struct_string) #add the struct definition to the function body
                        return_string = 'return result {' #create string for function returns using the structure just defined
                        for i in range(0,len(line)): #iterate over the return arguments
                            return_string += line[i] + ', ' #add the arguments to the return string
                        return_string = return_string[:-2] + '};' #remove the extra ', ' and close bracket and end return statement
                        function_body.append(return_string) #add the return string to the function body
            else: #if the node is not a return determine the type and convert it then add to function body
                function_body.append(general_access_node(i))
        if('return' in function_body[-1]): #check if the function was ended with a return
            pass
        else: #if no return add one
            function_body.append('return;')
        if(node.name == 'main'): #add a catch to prevent duplicate main functions within the converted script
            raise NameError('A function named "main" cannot be used within a C++ script as it is the default insertion point for the code, please rename this function in your script, this script will fill in a C++ main function automatically')
        else:
            pass
        
        function = [] #block for whole function
        #define the c++ function definition with the function name and the arguments string
        function_def = 'auto %s (%s) {' % (node.name, args_string)
        function.append(function_def) #add the function definition line
        function.append(function_body) #add the function body
        function.append('}') #close the open function brace
        arg_vars = [] #reset arg_vars as it is global
        function_body = [] #reset function body as it is global
        return function #return whole function

#define parser for class definitions
class ClassDefParser(ast.NodeVisitor):
    def visit_ClassDef(self,node): #visit class definition node
        global class_args #access to relevant globals
        class_block = [] #block of lines of converted class
        class_name = node.name #get the name of the class
        class_dec = 'class %s {' % class_name #make a converted class statement
        class_block.append(class_dec) #append the class stement to the block
        
        class_body = [] #make list of body of class statement
        for i in node.body: #iterate over the nodes in the body
            line = general_access_node(i) #convert the line of nodes and return
            class_body.append(line) #append the converted line to the body
        
        class_block.append(class_body) #append the body to the block
        class_block.append('};') #close off the class definition
        
        #@todo these properties
        #print(node.bases)
        #print(node.keywords)
        #print(node.decorator_list)
        return class_block #return the class block

#input classifying and converting function
def input_convert(name,data,type_var): #pass args of the variable, input arg data and the type of variable (pre-determined)
    val_assign = data #set val assign as data
    name_assign = name #set name assign as name
    converted_input = [] #list of converted input lines
    args = val_assign[1] #store the args of the input string
    outstring = args[0] #argument of the input string (line to output to prompt an input)
    outstring = string_or_var(outstring) #check if the outstring is a variable or string question
    outline = 'std::cout << ' + outstring + ';' #output the outstring
    converted_input.append(outline) #store the output line
    var = name_assign #store name of variable under var
    set_var = type_var + ' ' + var +';' #declare the input variable using the previously found type
    converted_input.append(set_var) #append the declaration to the input lines
    if(type_var=='std::string'): #if the type of input is a string
        input_string = 'std::getline (std::cin, %s);' % var #format a getline command to avoid whitespace breaks as this is probably unintended
        converted_input.append(input_string) #append the getline command to the input lines
    else: #if some other var type like float or int
        input_string = 'std::cin >> %s;' % var #use a standard cin command
        converted_input.append(input_string) #append the input command
        clear_in_buffer = 'std::cin.get();' #add a line to clear the input buffer to remove trailing \n for future input
        converted_input.append(clear_in_buffer) #append the clear buffer command
    end_line = 'std::cout << std::endl;' #append command to end line after inputs so next line isn't printed on the same line
    converted_input.append(end_line) #append the end line command to the input conversion
    return converted_input #return the input conversion

#parser class for assign statements, anything with an =
class AssignParser(ast.NodeVisitor):
    def visit_Assign(self,node): #function to visit the assign node
        global converted_lines, arg_vars, class_vars_for_call, called_objs #access to required globals
        for name in node.targets: #iterate over the node targets
            name_assign = general_access_node(name) #get the name, this is the variable the value is assigned to
        if(type(node.value) == ast.BinOp): #check for binary operators in the statement
            val_assign = BinOpParser().visit_BinOp(node.value) #send the node value to the binary operator parser, this will return the arguments swapping out ast operators for c++ operators
            flatten = [] #list for converting any sublists to one 1D array
            for i in val_assign: #iterate over the values
                if isinstance(i,list): #if one of the values is a list
                    for j in i: #iterate the values in that list and append to the flattened array
                        flatten.append(j)
                else: #if not a list just append the values directly
                    flatten.append(i)
            if(flatten!=[]): #if anything was added to the flatten list set the list as the value for the assign
                val_assign = flatten
            else:
                pass
            val_assign = ['BinOp',val_assign] #specify that this was a BinOp assignment 
        else: #if it wasn't a bin op find the type of node and convert the value to appropriate formatting
            val_assign = general_access_node(node.value)
        
        try:
            if(name_assign==("%s" % val_assign)): #if name_assign assign and val assign are the same
                class_vars_for_call.append(val_assign) #store the val in a list of class variables
            else:
                pass
        except:
            pass
        
        type_check = type(val_assign) #find the type data the value assign is
        #this condition will be met if line is assigning an input to a variable
        if(type_check == tuple and val_assign[0] == 'input'):
            converted = input_convert(name_assign,val_assign,'std::string') #convert the input using the function above passing type as string as input was not formatted with int(input()) or float(input())
            return converted #return the conversion
        #this condition met if input wrapped in a type command of int or float or just a standard int/float command
        elif(type_check == tuple and (val_assign[0] == 'int' or val_assign[0] == 'float')):
            if(val_assign[1][0][0] == 'input'): #if an input command wrapped by the function
                converted = input_convert(name_assign,val_assign[1][0],val_assign[0]) #convert input command using var type of the wrapping function
                return converted #return the converted input
            else: #if it's not an input raise a TypeError as it is not handled yet
                #@todo normal int() float() list() str() commands
                raise TypeError('Conversion of arg type not handled %s' % val_assign)
        #if the val_assign is a call to create an object this condition will be met, this method is a bit messy and could potentially do with reworking
        elif(type_check == tuple and any(('class %s {' % val_assign[0]) in x for x in converted_lines)):
            #print(val_assign[0], name_assign, val_assign[1])
            #val_assign will have format (Class_Name,[init_arg,init_arg,...])
            obj_declaration = [] #make list for object declaration
            secondary_class_store = [] #secondary list of class
            assign_obj = '%s %s;' % (val_assign[0],name_assign) #definition of creating object conversion
            obj_declaration.append(assign_obj) #add object declaration to body
            args_obj = val_assign[1] #isolate arguments of the object declaration
            count = 0 #iterator for removing used object args
            recall = False #flag for if this is the second time an object of the same type is being created
            for i in range(0,len(called_objs)): #iterate over list of previously called classes
                if(val_assign[0] == called_objs[i][0]): #check if this object is same type as existing
                    recall = True #mark that this is a recall
                    break #stop iterating
                else:
                    pass
            if(recall==False): #if this is the first time this class has been called
                secondary_class_store.append(val_assign[0]) #append the type to secondary list tracking classes called
                for i in range(0,len(args_obj)): #iterate over the object args
                    if(type(args_obj[i]) == str): #if type of arg is a string
                        args_obj[i] = string_or_var(args_obj[i]) #check if was a string or variable, replace it with variable if variable
                    else:
                        pass
                    secondary_class_store.append(class_vars_for_call[i]) #store the class variable name
                    converted_line = '%s.%s = %s;' % (name_assign,class_vars_for_call[i],args_obj[i]) #initialise class parameters with values
                    count+=1 #increase count of variables from class_vars_for_call used
                    obj_declaration.append(converted_line) #append the converted line to the declaration block of the object
                called_objs.append(secondary_class_store) #append previously called objects with the secondary list of class info
                class_vars_for_call = class_vars_for_call[count:] #omit the used up variables from the class_vars_for_call list
            else: #if the class has been called before
                for j in range(0,len(called_objs)): #iterate over the previously called objects list
                    if(called_objs[j][0] == val_assign[0]): #find the match case for this call
                        for k in range(1,len(called_objs[j])): #iterate over the arguments in that match call
                            #args_obj will take values one less than the corresponding stored argument as the first argument in a called_objs element will be the name of the class
                            #therefore called_objs[j] = ['Class_name',arg1,arg2,...], so for each k the corresponding arg to use is k-1
                            if(type(args_obj[k-1]) == str): #if type of arg is a string
                                args_obj[k-1] = string_or_var(args_obj[k-1]) #check if was a string or variable, replace it with variable if variable
                            else:
                                pass
                            converted_line = '%s.%s = %s;' % (name_assign,called_objs[j][k],args_obj[k-1]) #initialise class parameters with values
                            obj_declaration.append(converted_line) #append the converted line to the object declaration
                        break #break loop as relevant match found
                    else:
                        pass
            return obj_declaration #return the object declaration
        #if the val_assign is a return from the subscript parser this condition will be met
        elif(type_check == tuple and val_assign[0] == 'subscript'):
            #val_assign here will be ('subscript',['index',list_name,index_value])
            args = val_assign[1] #arguments of the assign statement stored
            list_name = args[1] #the name of the list is the argument 1
            type_script = args[0] #the type of subscripting (index/slice) stored
            if(type_script == 'index'): #if it is index subscripting
                subscript = list_name + '[%s]' % args[2] #the subscript formtating is list_name[index_value]
            elif(type_script == 'slice'): #if it is slice subscripting
                subscript = list_name + '[%s:%s]' % (args[2],args[3]) #the subscript formatting is list_name[lower_index:upper_index]
            else: #raise type error as other types are not handled yet
                raise TypeError('Subscript type not yet handled: %s' % type_script)
            
            found = False #flag for if a declaration of list has been found
            #multiple iterating methods will follow this to check different places for declaration of the list
            #check the converted lines so far in reverse order to get the most recent declaration of the list
            for i in reversed(range(0,len(converted_lines))):
                find_def = '%s = ' %  list_name #check for declaration of the list 
                if(find_def in converted_lines[i]): #check if the definition is on the current converted line
                    type_check = converted_lines[i].split(' ')[0] #if declaration match found isolate the type of the list
                    found = True #flag a declaration has been found
                else:
                    pass
            #comparison to be made for if the list was declared in a function definition where the function has not yet been added to converted lines
            function_var = ' %s' % list_name 
            if(arg_vars != [] and found == False): #if the list of arguments for active function is not empty and a match was not yet found
                for i in range(0,len(arg_vars)): #iteratae over the arguments in the function definition
                    if(function_var not in arg_vars[i]):  #if no match for current argument pass
                        pass
                    else: #if match found isolate the type from the argument as the type for the subscript
                        type_check = arg_vars[i].split(' ')[0]
                        found = True #flag a match was found
            else:
                pass
            #comparison to be made for if the list was declared in the body of the function currently being converted as it has not yet been added to converted lines
            if(function_body != [] and found == False):
                #iterate backwards over the lines in the function body to get most recent declaration
                for i in reversed(range(0,len(function_body))):
                    declaration_check = '%s = ' % list_name #expected declaration style of the list
                    #if not match in the line do nothing
                    if(declaration_check not in converted_lines[i]):
                        pass
                    else: #if there is a match isolate the type from the declaration 
                        type_check = converted_lines[i].split(' ')[0]
                        found = True #flag as found
            #default to an auto type if no match is found
            if(found == False):
                type_check = 'auto'
            else:
                #list type will return something like vector<float>, the value from the subscript will therefore be a float
                #need to isolate what is inside the first level of angle brackets
                inner_level = type_check.split('std::vector<',1)[1] #remove the first lot of vector definition
                mirrored = inner_level[::-1].replace('>','',1) #remove the final angle bracket to completely isolate the inner level
                isolated_inner = mirrored[::-1] #re-mirror to get back original value
                type_check = isolated_inner #type is now this isolted inner value
            
            val_assign = subscript #value is the formatted subscript
        
        #check if the name is a tuple, this conidition is met when attempting to set a list subscript to a certain value i.e. list[index] = 3
        elif(type(name_assign) == tuple):
            #name_assign will have the style ('subscript',['index',list_name,index_val])
            args = name_assign[1] #store arguments as the first element
            list_name = args[1] #name of the list is first argument element
            type_script = args[0] #store the type of subscripting
            if(type_script == 'index'): #if index type of subscripting format subscript as list_name[index_value]
                subscript = list_name + '[%s]' % args[2]
            elif(type_script == 'slice'): #if slice type of subscripting format subscript as list_name[lower_index:upper_index]
                subscript = list_name + '[%s:%s]' % (args[2],args[3])
            else: #if not one of these two raise a type error as it's not handled yet
                raise TypeError('Subscript type not yet handled: %s' % type_script)
            #make converted line in the style list_name[index] = val;
            converted_line = subscript + ' = ' + str(val_assign) +';'
            return converted_line #return converted line as it's in different style to other assigns
        #if the type check is a tuple this is a function call return stored to a variable
        elif(type_check == tuple):
            #val assign will be equal to ('func_name',[func_args])
            func_name = val_assign[0] #store the name of the function
            val_assign = val_assign[1] #store the args of the function
            type_check = 'auto' #default to auto type returning
            args = val_assign #set args as the stored values
            for j in range(0,len(args)): #iterate over the args checking if string or variable
                args[j] = string_or_var(args[j]) #stays same if variable overwrites to be in "" if string
                
            out_args = '' #set arguments string
            for i in range(0,len(args)): #iterate over the arguments
                out_args += args[i] + ', ' #add the argument and ', ' to make comma separated string
            out_args = out_args[:-2] #remove the extra ', '
            #call formatted as func_name(func_args)
            val_assign = func_name + '(' + out_args + ')'
        
        #if val_assign is a list and a return of a binary operator string
        elif(type_check == list and val_assign[0] == 'BinOp'):
            #val_assign will be equal to ('BinOp',[list of values and operators])
            op_string = val_assign[1] #store list of arguments
            eq_string = '' #define the string of the equation
            for i in op_string: #iterate over the arguments
                eq_string += str(i) + ' ' #add the argument to the existing string
            eq_string = eq_string[:-1] #remove the extra space at the end of the argument string
            val_assign = eq_string #set val_assign to this formatted string
            
            #a BinOp string could be for a concatenation of a string instead of maths
            #so attempt to determine the type of the first variable in the equation
            found = False #flag for no match
            #iterate backwards over converted lines for most recent definition
            for i in reversed(range(0,len(converted_lines))):
                find_def = ' %s = ' %  op_string[0] #define the string to search for
                if(find_def in converted_lines[i]): #if a match on this line
                    type_check = converted_lines[i].split(' ')[0] #isolate the type from the first word of the line
                    found = True #flag that a matach has been found
                else:
                    pass
            function_var = ' %s' % op_string[0] #string to search for match in function arguments
            #only do this search if the line is in the body of a function that has not yet been completed
            if(arg_vars != [] and found == False): 
                for i in range(0,len(arg_vars)): #iterate over the arguments of the function
                    if(function_var not in arg_vars[i]): #if there is no match for this argument pass
                        pass
                    else: #if there is a match isolate the type from the first word of the argument declaration
                        type_check = arg_vars[i].split(' ')[0]
                        found = True #flag that a match has been found
            else:
                pass
            #if a function body is currently in conversion and not yet appended to converted lines iterate over it to find match
            if(function_body != [] and found == False):
                #iterate backwards through body to get most recent declaration
                for i in reversed(range(0,len(function_body))):
                    declaration_check = '%s = ' % op_string[0] #string to check for in function body
                    if(declaration_check not in converted_lines[i]): #if no match this line do nothing
                        pass
                    else: #if match was found isolate the type as first word of line
                        type_check = converted_lines[i].split(' ')[0]
                        found = True #flag as found
            else:
                pass
                
            if(found == False): #if no match was found default to an auto type
                type_check = 'auto'
            else: #if match don't overwrite
                pass
        #if the type of val_assign is a list then it is a list declaration
        elif(type_check == list):
            #val_assign could be 1D list such as [2,3,4] etc or could be list of lists
            inside_level = val_assign[0] #get the first element of the list to test if it is also a list for declaration purposes
            nest_level = 1 #indicate the level of nesting of the lists (this assumes there is one more list inside at leas, nest level is reduced by one at the end of this block to compensate for overcounting)
            while(type(inside_level) == list): #if the inside level is another list
                inside_level = inside_level[0] #take another inside level
                nest_level+=1 #increase the nesting count of the list
            nest_level-=1 #remove one to compensate for overcounting the nesting level
            #for as many lists are nested repeat std::vector<, for example the list [[2,3,4],[5,6,7]]
            #here would get a type check of std::vector<std::vector<int>>
            type_check = 'std::vector<'*(nest_level+1)+str(type(inside_level))+'>'*(nest_level+1)
            val_assign = str(val_assign).replace('[','{').replace(']','}') #convert list formatting to vector formatting
        #if val_assign is a string
        elif(type_check == str): 
            #check to ensure it is not a bool value
            if(val_assign == 'true' or val_assign == 'false'):
                type_check = 'bool' #set type as bool
            else:
                #val_assign could be equal to 'Hello' for example
                val_assign = '"%s"' % val_assign #add speech marks around the value to allow string formatting
                type_check = 'std::string' #specify the type to declare as std::string
        #for any other standard type, for example val_assign = 3.3, type_check = <class 'float'>
        else: 
            pass
        #define the converted declaration as the type check (if a standard one then remove the <class ' and '> from the string of the type)
        #then the variable name and the value assigned to it, e.g. float test = 7.9
        converted_line = str(type_check).replace("<class '",'').replace("'>","") + ' %s = %s;' % (name_assign,val_assign)

        return converted_line #return the converted line

#define a parser for number nodes
class NumParser(ast.NodeVisitor):
    def visit_Num(self,node): #define function to visit the number node
        return node.n #return the number from the node

#define a parser for a unary operator node
class UnaryOpParser(ast.NodeVisitor):
    def visit_UnaryOp(self,node): #visit the unary operator node
        if(type(node.op) == ast.USub): #if the operator is a '-' to make a negative number
            num = NumParser().visit_Num(node.operand) #get the number (this will be the number without - operator)
            num_with_operator = -1*num #make the number negative
            return num_with_operator #return the negative number
        elif(type(node.op) == ast.UAdd): #if the operator is a '+' to make a positive number
            num = NumParser().visit_Num(node.operand) #get the number
            num_with_operator = np.abs(num) #take the absolute of it to make it positive
            return num_with_operator #return the number

#define a parser for string nodes
class StrParser(ast.NodeVisitor):
    def visit_Str(self,node): #visit the string node
        return node.s #return the string value

#define a parser for list nodes
class ListParser(ast.NodeVisitor):
    def visit_List(self,node): #visit the list node
        list_vals = [] #define list of the values
        for i in node.elts: #for each argument of the list
            #find the type and make any necessary conversions then append to the list values
            #if there is a nested list then the type will revisit this parser, e.g. list_Vals = [] to start
            #then a sub list vals is generated and values appended to it then return that sub list to
            #append to the original list_vals, e.g. [[2,3,4]]
            list_vals.append(general_access_node(i)) 
        
        return list_vals #return the completed list of values

#define a parser for subscript nodes (taking indices or slices of lists)
class SubscriptParser(ast.NodeVisitor):
    def visit_Subscript(self,node): #visit the subscript node
        list_slice = [] #list of parameters of the subscript to format
        name = node.value.id #the variable name the list has
        if(type(node.slice) == ast.Index): #if the type of subscripting is taking an index from the list
            index = general_access_node(node.slice.value) #get the value of the index, could be number or letter if in a loop process
            list_slice.append('index') #mark this was an index process for later conversion
            list_slice.append(name) #add the name to the parameters
            list_slice.append(index) #add the index value to the parameters

        elif(type(node.slice) == ast.Slice): #if type of subscripting is a slice
            lower_index = general_access_node(node.slice.lower) #get the value of the lower index of the list
            upper_index = general_access_node(node.slice.upper) #get the value of the upper index of the list
            list_slice.append('slice') #mark this was a slice for ater conversion
            list_slice.append(name) #add the name to the parameters
            list_slice.append(lower_index) #add the lower index to the parameters
            list_slice.append(upper_index) #add the upper index to the parameters

        else: #need to do extslice type here later
            pass #@todo ExtSlice
        
        return 'subscript',list_slice #return a marking that this is a subscript node and the values

#parser for binary operator nodes
class BinOpParser(ast.NodeVisitor):
    def visit_BinOp(self,node): #visit the binary operator node
        vals = [] #list for values either side of binary operator
        left_val = general_access_node(node.left) #determine the type and get the value of arguments left of the operator
        right_val = general_access_node(node.right) #determine the type and get the value of arguments right of the operator
        
        ast_ops = [ast.Add,ast.Sub,ast.Div,ast.Mult] #list of types of ast operators
        #@todo handle more operators
        c_ops = ['+','-','/','*'] #corresponding list  of C++ operators
        operator = node.op #get operator between the left and right vals
        try: #attempt to find the operator type from the ast operator list
            op_index = ast_ops.index(type(operator))
            operator = c_ops[op_index] #get the corresponding C++ operator
        except: #if no index found then raise a type error to flag that it needs handling
            raise TypeError('Binary operator type not handled yet: %s' % operator)
        vals.append(left_val) #append the left value
        vals.append(operator) #append the new C++ operator 
        vals.append(right_val) #append the right value
        return vals #return the list of values

#define a parser for expression nodes
class ExprParser(ast.NodeVisitor):
    def visit_Expr(self,node): #visit the expression node
        global converted_lines, function_body, arg_vars #allow access to relevant globals
        line = general_access_node(node.value) #determine type and do any conversions for the argument of the expression
        #example line = ('print',[a,b,c])
        function = line[0] #the function of the expression
        #handle different inbuilt functions to convert to C++ versions
        #@todo more of these inbuilts
        if(function == 'print'): #if the expression is a print statement
            function = 'std::cout << ' #replace the function with the std::cout function which will have at least one argument
            args = line[1] #store the arguments of the function
            #iterate over the function arguments, this is to check if the argument is a variable or a string
            for j in range(0,len(args)):
                #print(args)
                args[j] = string_or_var(args[j])

            out_args = '' #string of output arguments
            for i in range(0,len(args)): #iterate over the number of arguments
                out_args += args[i] + ' << ' #add the argument and ' << ' to the output string 
            out_args += 'std::endl' #add an endline to the end of the string
            
            converted_line = function + out_args + ';' #make the converted line std::cout << arg1 << arg2 ... << std::endl;
        
        elif('.' in function): #check if the function is an attribute
            #this means it is an attribute that should have already been resolved
            #an example could be line = ('g.append(',[args_list])
            args = line[1] #store the args as the first element
            for j in range(0,len(args)): #iterate over the arguments
                if(type(args[j]) == str):
                    args[j] = string_or_var(args[j])

                elif(type(args[j]) == list): #if the argument type is a list
                    args[j] = str(args[j]).replace('[','{').replace(']','}') #convert argument to vector notation
                else:
                    pass
            args_string = '' #define a blank string to make string of arguments
            for i in range(0,len(args)): #iterate over the arguments
                args_string += str(args[i]) + ', ' #add the argument and ', ' to the arguments string
            args_string = args_string[:-2] #remoev the extra ', ' from the end
            converted_line = '%s%s);' % (function,args_string) #complete the converted line to gie e.g. g.push_back(9.9)
        else:
            #if made it this far the expression is treated as a function call
            #example line = ('function_name',[function_args])
            args = line[1] #store the arugments of the function call
            for j in range(0,len(args)): #iterate over the arguments
                args[j] = string_or_var(args[j])
                
            out_args = '' #as before format final arguments string as comma separated
            for i in range(0,len(args)):
                out_args += args[i] + ', '
            out_args = out_args[:-2]
            #define the converted line as function_name(funtion_args);
            converted_line = function + '(' + out_args + ')' + ';'

        return converted_line #return the converted line  

#define parser to handle function call nodes
class CallParser2(ast.NodeVisitor):
    def visit_Call(self,node): #visit function call node
        func_type = general_access_node(node.func) #call to get the value of the name of the function being called
        args_list = [] #list for arguments of tbhe function
        for i in range(0,len(node.args)): #iterate over the arguments of the function
            #print(node.args[i])
            args_list.append(general_access_node(node.args[i])) #classify and extract the value of the arguments of the function
        if(func_type == 'len'): #special case for the len function as this is an attribute of .size() in C++, other special conditions can be coded in here
            converted_func = args_list[0] + '.size()' #e.g. if it was len(a) change to a.size()
            return converted_func #return the converted function
        else:
            pass
        return func_type, args_list #if special cases not met return the type of function and arguments list

#define parser to handle return nodes
class ReturnParser(ast.NodeVisitor):
    def visit_Return(self,node): #visit return node
        if(type(node.value) == None): #if it is a void return with no values return None
            return node.value
        else: #if it has values get the types and values it is meant to returning and return them
            args_list = general_access_node(node.value)
            return args_list

#define parser to handle tuple nodes
class TupleParser(ast.NodeVisitor):
    def visit_Tuple(self,node): #visit tuple node
        args_list = [] #define list of arguments
        for i in range(0,len(node.elts)): #iterate over the values in the tuple
            args_list.append(general_access_node(node.elts[i])) #get the type and subsequant value of each argument in the tuple
        return args_list #return a list of arguments

#define parser to handle if statement nodes
class IfParser(ast.NodeVisitor):
    def visit_If(self,node): #visit if statement node
        global converted_lines, top_level_if #have access to relevant globals

        if_block = [] #make a list of the if block
        condition = general_access_node(node.test) #convert the condition of the if statement analysing the node
        condition_string = '' #make a string of the condition statement
        for i in range(0,len(condition)): #iterate over the arguments of the condition, each should have already been converted to an appropriate format
            condition_string += str(condition[i]) + ' ' #add the condition arguments space separated
        condition_string = condition_string[:-1] #remove the extra space at the end
        if(top_level_if): #if this is the first if statement
            statement = 'if (%s) {' % condition_string #format it as opening if with the condition
            top_level_if = False #next if statement is not top level, i.e. there is an elif statement
        else: #if an elif statement is already present
            statement = 'else if (%s) {' % condition_string #format with else if instead
        if_block.append(statement) #append the statement to the if block

        for i in node.body: #iterate over the nodes in the body of the if block
            #there could potentially be more if statements nested inside the main if statement
            #the first nested ifs would need to be if and not elif , hence reset the flag to be top level
            top_level_if = True
            line = general_access_node(i) #convert the node to an appropriate format
            if_block.append(line) #append the line to the if_block
            top_level_if = False #flag top level back to false as nesting has finished
            
        if_block.append('}') #close the if statement block

        #check if the else block contains another if block (this occurs if an elif statement is used)
        if(node.orelse == [] or type(node.orelse[0]) != ast.If): #if no elif statement in if block
            if_block.append('else {') #append an else statement
        else:
            pass
        
        #@todo fix where an else if appears for the first if inside an else block
        #example problem:
        #else {
        #   else if (...) {
        #   
        #   }
        #   else {
        #   
        #   }
        #}
        for i in node.orelse: #iterate over the nodes in the else statement
            try: #if its an elif statement i.test will work else will run except
                i.test
                line = general_access_node(i) #convert line
                if_block.append(line) #add line to if block
            except: #if fails deafult to top level if statement for any statement inside
                top_level_if = True #mark top level
                line = general_access_node(i) #get the type of line and convert
                if_block.append(line) #append the line to the if block
                top_level_if = False #reset top level to false

        #@todo figure out a better way to ensure correct number of closing braces
        if(if_block[-1][-1] == '}'): #check if all if statements got closed off
            pass
        else: #if not close off the final one
            if_block.append('}')

        top_level_if = True #reset top level back to true

        return if_block #return the converted if block

#define parser for compare statement nodes, inside if blocks
class CompareParser(ast.NodeVisitor):
    def visit_Compare(self,node): #visit the compare node
        left_arg = general_access_node(node.left) #store the left value of the argument
        #define the types of ast operators 
        ast_ops = [ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE,ast.Is,ast.IsNot,ast.In,ast.NotIn,ast.And,ast.Or]
        #define the corresponding c++ operators
        c_ops = ['==','!=','<','<=','>','>=','TODO','TODO','TODO','TODO','&&','||']
        
        #@todo handle the is and in operators for c++
        full_args = [] #list of full arguments from the compare statement
        full_args.append(left_arg) #append the left value argument to full arguments
        for i in range(0,len(node.ops)): #iterate over the number of operators for long chains of comparisons
            index = ast_ops.index(type(node.ops[i])) #get the index of match of the ast_ops
            c_op = c_ops[index] #get the corresponding c_op
            full_args.append(c_op) #append the c operator to the args
            value = general_access_node(node.comparators[i]) #get the value being compared to type and value
            if(type(value) == str): #if it is a string
                value = string_or_var(value) #run check to see if it is string or variable
            else:
                pass
            full_args.append(value) #append the value to the full args
        
        return full_args #return the full args

#define parser for name nodes
class NameParser(ast.NodeVisitor):
    def visit_Name(self,node): #visit name node
        name = node.id #get the name id
        return name #return the name

#define parser for for loop nodes
class ForParser(ast.NodeVisitor):
    def visit_For(self,node): #visit the for node
        iterator = general_access_node(node.target) #get the iterator of the loop
        condition = general_access_node(node.iter) #get the condition of the loop
        #e.g. of condition = ('range'[0,list_name.size()]) or number equivalent
        if(condition[0] == 'range'):
            lower_limit = condition[1][0] #lower limit of range
            upper_limit = condition[1][1] #upper limit of range
            #write the condition of the for loop incrementing in the range
            if(upper_limit==0): #if the upper limit is 0, e.g. range(10,0)
                #make the for condition iterate backwards from the "lower" limit (with higher value) to "upper" limit (value 0)
                for_condition = 'for (int %s = %s; %s > %s; %s--) {' % (iterator,lower_limit,iterator,upper_limit,iterator)
            elif(isinstance(upper_limit,int) and isinstance(lower_limit,int) and upper_limit<lower_limit): #if both limits are numbers (not a len function) and upper has lower value than lower
                #make the for condition iterate backwards from the "lower" limit (with higher value) to "upper" limit (lower value)
                for_condition = 'for (int %s = %s; %s > %s; %s--) {' % (iterator,lower_limit,iterator,upper_limit,iterator)
            else: #otherwise assume forwards iteration
                for_condition = 'for (int %s = %s; %s < %s; %s++) {' % (iterator,lower_limit,iterator,upper_limit,iterator)
        elif(condition[0] == 'reversed'):
            #condition will be in format ('reversed',[('range',[0,5])])
            #take limits opposite way round as they are in a reversed function
            upper_limit = condition[1][0][1][0]
            lower_limit = condition[1][0][1][1]
            if(upper_limit==0): #conditions are as above but reversed
                for_condition = 'for (int %s = %s; %s > %s; %s--) {' % (iterator,lower_limit,iterator,upper_limit,iterator)
            elif(isinstance(upper_limit,int) and isinstance(lower_limit,int) and lower_limit>upper_limit): 
                for_condition = 'for (int %s = %s; %s > %s; %s--) {' % (iterator,lower_limit,iterator,upper_limit,iterator)
            else:
                for_condition = 'for (int %s = %s; %s < %s; %s++) {' % (iterator,lower_limit,iterator,upper_limit,iterator)
        else: #if line was for x in list_name, the condition will be (list_name)
            vector = condition[0]
            #format for condition
            for_condition = 'for (auto %s: %s) {' % (iterator,vector)

        body_block = [] #define body of for loop
        body_block.append(for_condition) #append the for condition to the body
        for i in node.body: #for each node in the body
            line = general_access_node(i) #classify and convert the line
            if('std::cout << ' in line): #check if attempting to print something
                splitup = line.split(' << ') #split on the args separator
                for i in range(0,len(splitup)): #iterate over the split args
                    if(splitup[i] == ('"%s"' % iterator)): #check if the arg is the iterator which has falsely been converted in to a string
                        splitup[i] = iterator #if false conversion made switch out for iterator
                        line = ' << '.join(splitup) #rejoin the line
                    else: #if no false string pass
                        pass
            body_block.append(line) #convert the node and append it to the block
        body_block.append('}') #close the for brace
        return body_block #return the body

#define parser for attribute nodes
class AttributeParser(ast.NodeVisitor):
    def visit_Attribute(self,node): #visit the attribute node
        attribute = node.attr #gives the function being applied, e.g for a.append, returns append
        value = general_access_node(node.value) #classify and convert the object being appended
        #print(attribute,value)
        if(attribute=='append'): #if the atrribute is append
            attribute = 'push_back' #replace with vector push_back method
        elif(value=='self'): #if not raise a type error to flag this attribute is not yet handled
            #converted_line = '%s.%s' % (value,attribute)
            return attribute
            #return None
            #raise TypeError('Attribute type not handled yet: %s,%s' % (attribute,value))
        else:
            pass
        
        converted_line = '%s.%s(' % (value,attribute) #define the converted line
        return converted_line #return the converted line

#define parser for while nodes
class WhileParser(ast.NodeVisitor):
    def visit_While(self,node): #visit while node
        while_body = [] #define while block
        condition = general_access_node(node.test) #convert the while condition
        condition_string = '' #define string for the condition
        for i in condition: #iterate over the elements in the condition list
            condition_string+=str(i)+' ' #add the condition element and a space
        condition_string = condition_string[:-1] #remove the extra space
        condition_line = 'while (%s) {' % condition_string #define the while statement
        while_body.append(condition_line) #append the while statement to the block
        for i in node.body: #iterate over nodes in the body of the while loop
            line = general_access_node(i) #classify and convert the node
            while_body.append(line) #append the converted line to the block
        while_body.append('}') #close the while loop
        #@todo handle the orelse node
        return while_body #return the while block

#define parser for AugAssign nodes
class AugAssignParser(ast.NodeVisitor):
    def visit_AugAssign(self,node): #visit AugAssign nodes
        var = general_access_node(node.target) #get the variable value is assigned to
        ast_operators = [ast.Add,ast.Sub,ast.Div,ast.Mult] #define list of ast operators
        c_ops = ['+=','-=','/=','*='] #define corresponding list of c++ operators
        index = ast_operators.index(type(node.op)) #get the index matching the operator
        operator = c_ops[index] #get the correspoding c++ operator to the matched operator
        value = general_access_node(node.value) #classify and convert the value node
        converted_line = '%s %s %s;' % (var,operator,value) #format the aug assign string
        return converted_line #return the converted line

#define parser for name constant nodes
class NameConstantParser(ast.NodeVisitor):
    def visit_NameConstant(self,node): #visit name constant node
        #node.value should be True False or None
        if(node.value == True): #if True return C++ bool true
            return 'true'
        elif(node.value == False): #if false return C++ bool false
            return 'false'
        else: #if none flag not handled yet
            raise TypeError('NameConstant not true or false and not handled : %s' % node.value)

#define function to check if a value is a string or a variable as they are classified the same by the AST
def string_or_var(value):
    global converted_lines, arg_vars, function_body, class_args #have access to relevant globals
    found = False #flag no match found
    #iterate backwards over converted lines looking for a match, backwards to get most recent definition
    for i in reversed(range(0,len(converted_lines))):
        declaration_check = '%s = ' % value #look for declaration of variable
        if(declaration_check not in converted_lines[i]): #if not match pass
            pass
        else: #if match flag a match found
            found = True
            break
    #if there is a function under conversion not yet appended and no match found
    if(arg_vars != [] and found == False):
        for i in range(0,len(arg_vars)): #iterate over the function arguments
            if(value not in arg_vars[i]): #if no match pass
                pass
            else: #if match flag a match was found
                found = True
                break
    else:
        pass
    #if there is a function under conversion not yet appended and no match found
    if(function_body != [] and found == False):
        for i in reversed(range(0,len(function_body))): #iterate backwards over function body to get most recent definition
            declaration_check = '%s = ' % value #look for declaration of variable
            if((converted_lines==[]) or declaration_check not in converted_lines[i]): #if no match pass
                pass
            else: #if match flag that a match was found
                found = True
                break
            
    #if there is an active class check for a match in its declarated arguments
    if(class_args != [] and found == False):
        for i in range(0,len(class_args)): #iterate over class args to check for match
            declaration_check = '%s' % value #look for declaration of variable
            if((class_args==[]) or declaration_check not in class_args[i]): #if no match pass
                pass
            else: #if match flag that a match was found
                found = True
                break
    
    
    if(found==False):
        #print(converted_lines)
        second_declare = ' %s;' % value
        for i in reversed(range(0,len(converted_lines))):
            for j in range(0,len(converted_lines[i])):
                if(second_declare not in converted_lines[i][j]): #if not match pass
                    pass
                else: #if match flag a match found
                    found = True
                    break
    
    if(found == False and value != 'true' and value != 'false'): #if no match default to string
        value = '"%s"' % value
    else:
        pass
    #if match will return the same value therefore a variable, if no match it will put speech marks around for c++ string definition
    return value

#this functions purpose is to receive any node and determine it's type
#once determined the node will be passed to an appropriate parsing function or directly
#handle the node for some simple cases then return the value of the node after it has
#been parsed and converted by the parser it sent it to
def general_access_node(node):
    #check the type of the node and compare to currently handled type
    if(type(node) == ast.FunctionDef):
        #store the value of the return from the parsed node after sending it to be decoded
        parsed_node = FunctionParser().visit_FunctionDef(node)
    elif(type(node) == ast.Assign):
        parsed_node = AssignParser().visit_Assign(node)
    elif(type(node) == ast.Expr):
        parsed_node = ExprParser().visit_Expr(node)
    elif(type(node) == ast.If):
        parsed_node = IfParser().visit_If(node)
    elif(type(node) == ast.For):
        parsed_node = ForParser().visit_For(node)
    elif(type(node) == ast.Num):
        parsed_node = NumParser().visit_Num(node)
    elif(type(node) == ast.Str):
        parsed_node = StrParser().visit_Str(node)
    elif(type(node) == ast.UnaryOp):
        parsed_node = UnaryOpParser().visit_UnaryOp(node)
    elif(type(node) == ast.Subscript):
        parsed_node = SubscriptParser().visit_Subscript(node)
    elif(type(node) == ast.Call):
        parsed_node = CallParser2().visit_Call(node)
    elif(type(node) == ast.Return):
        parsed_node = ReturnParser().visit_Return(node)
    elif(type(node) == ast.Tuple):
        parsed_node = TupleParser().visit_Tuple(node)
    elif(type(node) == ast.List):
        parsed_node = ListParser().visit_List(node)
    elif(type(node) == ast.Compare):
        parsed_node = CompareParser().visit_Compare(node)
    elif(type(node) == ast.Name):
        parsed_node = NameParser().visit_Name(node)
    elif(type(node) == ast.Pass):
        parsed_node = '\n'
    elif(type(node) == ast.Attribute):
        parsed_node = AttributeParser().visit_Attribute(node)
    elif(type(node) == str):
        parsed_node = node
    elif(type(node) == ast.While):
        parsed_node = WhileParser().visit_While(node)
    elif(type(node) == ast.AugAssign):
        parsed_node = AugAssignParser().visit_AugAssign(node)
    elif(type(node) == ast.NameConstant):
        parsed_node = NameConstantParser().visit_NameConstant(node)
    elif(type(node) == ast.ClassDef):
        parsed_node = ClassDefParser().visit_ClassDef(node)
    elif(type(node) == ast.Break):
        parsed_node = 'break;'
    else: #if the type of node does not yet have a parser raise a type error which diesplays the type to know what parser needs to be made next
        raise TypeError('Parser not found for type: %s' % type(node))
    
    return parsed_node #return the parsed/converted node value

#define the main function for parsing and converting a script,takes arguments of the name of a python script and the name of a script with example function calls
def main(script_to_parse,script_of_function_calls=None):
    global converted_lines, list_types #make globals of the converted lines and function argument types
    list_types = [] #define list of function types from script of function calls
    converted_lines = [] #define list of converted C++ lines
    #if a script of cuntion calls has been provided analyse it for types, if not then no functions are defined in the python script
    if(script_of_function_calls!=None):
        file2 = open(script_of_function_calls,'r').read() #open and read the script of function calls specified
        call_parse = ast.parse(file2) #parse the script to make an AST of nodes
        for node in call_parse.body: #iterate over the nodes in the body of the tree
            funcs_args = [] #define list of the arguments of current function in the tree
            for arg in node.value.args: #iterate over the arguments in the function currently active
                arg_val = general_access_node(arg) #get the value of the argument 
                #run through a series of checks to determine the type of the argument provided
                #once a match is found append the appropriate type to the current function's arguments type list
                if isinstance(arg_val,int):
                    funcs_args.append('int')
                elif isinstance(arg_val,float):
                    funcs_args.append('float')
                elif isinstance(arg_val,str):
                    funcs_args.append('std::string')
                elif isinstance(arg_val,list): #if the argument is a list it needs special handling
                    inside_level = arg_val[0] #get the first element of the list to check if it contains more lists
                    nest_level = 1 #increase the nest level by one
                    if isinstance(inside_level,list): #if the first element is a list
                        inside_level = inside_level[0] #take the first element of the sub list
                        nest_level+=1 #increase the nest level by one
                        while(isinstance(inside_level,list)): #if still a sub list then repeat this process until the first non list element is found
                            inside_level = inside_level[0]
                            nest_level+=1
                        type_check = type(inside_level) #get the type of the first non list element
                        
                    else: #if not a list of lists get the type of the first element
                        type_check = type(inside_level)
                    #define the type of list, nest level is used to determine the number of vector commands to nest
                    #for example the list [[2,3,4],[5,6,7]] would have nest_level = 2 and type_check = <class 'int'>
                    #so the below code would format type_list = <std::vector<std::vector<int>>
                    type_list = ('std::vector<'*nest_level)+str(type_check).replace("<class '",'').replace("'>",'') + ('>'*nest_level)
                    funcs_args.append(type_list) #append this vector definition to the function's arguments
            list_types.append(funcs_args) #append the completed funtion arguments type list to the list of type lists
    else: #if no function calls skip this process
        pass
    
    file = open(script_to_parse,'r').read() #open the python file to convert and read it
    tree = ast.parse(file) #make an AST of the nodes within the file
    main = False #flag that a main function has not yet been added to the converted script
    for node in tree.body: #iterate over the nodes in the body of the AST
        line_test = general_access_node(node) #run function to determine the type of the node and convert it accordingly
        #if the line had a function definition it has already been added to converted lines so this condition is added to stop duplicate addition, these are the conditions that will be met if that is true
        #print(line_test[0])
        if(('auto' in line_test[0] and '{' in line_test[0]) or ('class' in line_test[0] and '{' in line_test[0])):
            pass
        else: #if it is not a function definition
            if(main==False): #check if a main has been added yet
                converted_lines.append('int main () {') #if no main start the main function here as function definitions have finished
                main=True #flag that a main has been added
            else: #if main has been added do not add it again
                pass
        #check to see if the returned value has already been added to the converted lines and the return was not a void one
        #if it is not a NoneType return and has not yet been added to converted lines then add it
        #modified to check if the line was just appended to the converted lines list, may cause issue if you write the same line twice in a row, untested
        #if(line_test != converted_lines[len(converted_lines)-1] and line_test != None):
        converted_lines.append(line_test)
        #else: #if it has been addded or is NoneType do nothing
         #   pass
    converted_lines.append('return 0;') #add a return for the c++ main function
    converted_lines.append('}') #close the main function
    #below are checks to see what include statements are needed for the c++ code
    #each one will chec for an instance of a function and if a match is found the appropriate
    #include statement will be inserted in to the top of the converted lines list
    if(('std::cout' in line for line in converted_lines) or ('std::cin' in line for line in converted_lines)):
        converted_lines.insert(0,'#include <iostream>')
    else:
        pass
    if('std::string' in line for line in converted_lines):
        converted_lines.insert(0,'#include <string>')
    else:
        pass
    if('std::vector' in line for line in converted_lines):
        converted_lines.insert(0,'#include <vector>')
    return converted_lines #return the list of converted c++ lines

#function to check if line is list or list of lists and convert in to flattened data
def walk(e):
    if(type(e) == list): #if the line is a list
        for v2 in e: #iterate over list elements
            for v3 in walk(v2): #iterate over sub list elements (which will iterate further if another sublist)
                yield v3 #yield the non list element
    else: #if line not a list
        yield e #return the line

#function to write the parsed data to an output .cpp file
def write_file(data,name_of_output='Output.cpp'):
    file = open(name_of_output,'w+') #open an output file to the specified path for writing/creation
    indentation_level=0 #default indentation level is 0
    public_open = False
    flatten = [] #create a list of flattened line data
    for line in walk(data): #call walk function on converted data
        flatten.append(line) #append the flattened line to the flattened data

    for line in flatten: #iterate over the lines in the flattened data
        #print(line,indentation_level)
        if(public_open==True and ('auto' in line or '};' in line)):
            indentation_level-=1
            public_open=False
        else:
            pass
        open_brace_count = line.count('{') #count number of open brackets on the line
        close_brace_count = line.count('}') #count number of closing brackets on the line
        if(open_brace_count>close_brace_count):
            #if more open brackets than close, the code following (not including) this line
            #will require indentation, as such write this line and the increase the indentation level for subsequent lines
            file.write(('\t'*indentation_level)+line+'\n')
            indentation_level+=1
        elif(open_brace_count<close_brace_count):
            #if more close brackets than open brackets, the code following is outside of the
            #function block, as such will need indentation level reduced by one, this includes the closing brace this time
            #hence the reverse order to the condition above
            indentation_level-=1
            file.write(('\t'*indentation_level)+line+'\n')
        elif('public:' in line):
            file.write(('\t'*indentation_level)+line+'\n')
            indentation_level+=1
            public_open = True
        else: #if number of braces equal then do not change indentation level
            file.write(('\t'*indentation_level)+line+'\n')

    file.close() #writing completed so close the file

if __name__ == '__main__':
    top_level_if = True #flag for if statments, method needs revision
    class_vars_for_call = []
    called_objs = []
    print('Beginning Parsing') #inform user parsing has began, precaution incase a large file takes a long time parsing
    converted_data = main('Test.py','CallTest.py') #parse Test.py file, function call examples are listed in CallTest.py, if no function calls do not pass second argument
    print('Parsing Completed') #inform user parsing has finished
    print('Writing File') #inform user output to file has started
    write_file(converted_data,'Test.cpp') #write a file called Test.cpp with the output data, if no name specified will default to Output.cpp
    print('Writing Completed') #inform user writeout completed


