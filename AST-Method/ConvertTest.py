#The following is a new test method using the AST library to parse nodes in a script and convert those parsed nodes individualy in to cpp
#script, once this method is up to date with the old method it will be fully commented to explain approach, it has been included now for
#any potential contributors to see what new approach is being taken to replace the old line by line string replacement method

#script to read python code in to an AST, parse and replace nodes with corresponding c++ code
#make relevant imports
import ast
import numpy as np

#parser class for function definitions
class FunctionParser(ast.NodeVisitor):
    def visit_FunctionDef(self, node): #visit the function definition node
        #define relevant globals that require access
        global converted_lines, function_body, arg_vars, list_types
        arg_vars = [] #list of arguments
        args_string = '' #argument string for conversion
        for i in range(0,len(node.args.args)): #iterate over the node arguments
            arg_val = node.args.args[i].arg #for each arg append the arg name
            arg_type = list_types[0][i] #get the types of the first function's arguments
            full_arg = arg_type + ' ' + arg_val #define a full argument string as the type and name
            arg_vars.append(full_arg) #add the full arg definition to list
            args_string += full_arg + ', ' #add the full arag definition to the arg string
        args_string = args_string[:-2] #remove extra ', ' at the end of the line
        list_types.pop(0) #remove the arg types for the arguments that have just been processed
        
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
                        return_string = 'return result {'
                        for i in range(0,len(line)):
                            return_string += line[i] + ', '
                        return_string = return_string[:-2] + '};'
                        function_body.append(return_string)
            else:
                function_body.append(general_access_node(i))
        
        function_def = 'auto %s (%s) {' % (node.name, args_string)
        converted_lines.append(function_def)
        converted_lines.append(function_body)
        converted_lines.append('}')
        arg_vars = []
        function_body = []
        return

class AssignParser(ast.NodeVisitor):
    def visit_Assign(self,node):
        global converted_lines, arg_vars
        for name in node.targets:
            name_assign = general_access_node(name)
        if(type(node.value) == ast.BinOp):
            val_assign = BinOpParser().visit_BinOp(node.value)
            flatten = []
            for i in val_assign:
                if isinstance(i,list):
                    for j in i:
                        flatten.append(j)
                else:
                    flatten.append(i)
            if(flatten!=[]):
                val_assign = flatten
            else:
                pass
            val_assign = ['BinOp',val_assign]
        else:
            val_assign = general_access_node(node.value)

        type_check = type(val_assign)
        if(type_check == tuple and val_assign[0] == 'subscript'):
            args = val_assign[1]
            list_name = args[1]
            type_script = args[0]
            if(type_script == 'index'):
                subscript = list_name + '[%s]' % args[2]
            elif(type_script == 'slice'):
                subscript = list_name + '[%s:%s]' % (args[2],args[3])
            else:
                raise TypeError('Subscript type not yet handled: %s' % type_script)
            
            found = False
            for i in reversed(range(0,len(converted_lines))):
                find_def = '%s = ' %  list_name
                if(find_def in converted_lines[i]):
                    type_check = converted_lines[i].split(' ')[0]
                    found = True
                else:
                    pass
            function_var = ' %s' % list_name
            if(arg_vars != [] and found == False):
                for i in range(0,len(arg_vars)):
                    if(function_var not in arg_vars[i]):
                        pass
                    else:
                        type_check = arg_vars[i].split(' ')[0]
                        found = True
            else:
                pass
            if(function_body != [] and found == False):
                for i in reversed(range(0,len(function_body))):
                    declaration_check = '%s = ' % list_name
                    if(declaration_check not in converted_lines[i]):
                        pass
                    else:
                        type_check = converted_lines[i].split(' ')[0]
                        found = True
            
            if(found == False):
                type_check = 'auto'
            else:
                inner_level = type_check.split('std::vector<',1)[1]
                mirrored = inner_level[::-1].replace('>','',1)
                isolated_inner = mirrored[::-1]
                type_check = isolated_inner
            
            val_assign = subscript
        
        elif(type(name_assign) == tuple):
            args = name_assign[1]
            list_name = args[1]
            type_script = args[0]
            if(type_script == 'index'):
                subscript = list_name + '[%s]' % args[2]
            elif(type_script == 'slice'):
                subscript = list_name + '[%s:%s]' % (args[2],args[3])
            else:
                raise TypeError('Subscript type not yet handled: %s' % type_script)
            
            converted_line = subscript + ' = ' + str(val_assign) +';'
            return converted_line
        
        elif(type_check == tuple):
            func_name = val_assign[0]
            val_assign = val_assign[1]
            type_check = 'auto'
            #print('TREATED AS STORED FUNCTION CALL: ',func_name)
            args = val_assign
            for j in reversed(range(0,len(args))):
                found = False
                for i in reversed(range(0,len(converted_lines))):
                    declaration_check = '%s = ' % args[j]
                    if(declaration_check not in converted_lines[i]):
                        pass
                    else:
                        found = True
                if(arg_vars != [] and found == False):
                    for i in range(0,len(arg_vars)):
                        if(args[j] not in arg_vars[i]):
                            pass
                        else:
                            found = True
                else:
                    pass
                if(function_body != [] and found == False):
                    for i in reversed(range(0,len(function_body))):
                        declaration_check = '%s = ' % args[j]
                        if(declaration_check not in converted_lines[i]):
                            pass
                        else:
                            found = True
                
                if(found == False):
                    args[j] = '"%s"' % args[j]
                else:
                    pass
                
            out_args = ''
            for i in range(0,len(args)):
                out_args += args[i] + ', '
            out_args = out_args[:-2]
            
            val_assign = func_name + '(' + out_args + ')'
        
        elif(type_check == list and val_assign[0] == 'BinOp'):
            op_string = val_assign[1]
            eq_string = ''
            for i in op_string:
                eq_string += str(i) + ' '
            eq_string = eq_string[:-1]
            val_assign = eq_string
            if('+' in val_assign):
                found = False
                for i in reversed(range(0,len(converted_lines))):
                    find_def = '%s = ' %  op_string[0]
                    if(find_def in converted_lines[i]):
                        type_check = converted_lines[i].split(' ')[0]
                        found = True
                    else:
                        pass
                function_var = ' %s' % op_string[0]
                if(arg_vars != [] and found == False):
                    for i in range(0,len(arg_vars)):
                        #print(arg_vars[i])
                        if(function_var not in arg_vars[i]):
                            pass
                        else:
                            type_check = arg_vars[i].split(' ')[0]
                            found = True
                else:
                    pass
                if(function_body != [] and found == False):
                    for i in reversed(range(0,len(function_body))):
                        declaration_check = '%s = ' % args[j]
                        if(declaration_check not in converted_lines[i]):
                            pass
                        else:
                            type_check = converted_lines[i].split(' ')[0]
                            found = True
                
                if(found == False):
                    type_check = 'float'
                else:
                    pass
            else:
                type_check = 'float'
        elif(type_check == list):
            inside_level = val_assign[0]
            nest_level = 1
            while(type(inside_level) == list):
                inside_level = inside_level[0]
                nest_level+=1
            nest_level-=1
            type_check = 'std::vector<'*(nest_level+1)+str(type(inside_level))+'>'*(nest_level+1)
            val_assign = str(val_assign).replace('[','{').replace(']','}')
        elif(type_check == str):
            val_assign = '"%s"' % val_assign
            type_check = 'std::string'
        else:
            pass
        converted_line = str(type_check).replace("<class '",'').replace("'>","") + ' %s = %s;' % (name_assign,val_assign)
        #print(converted_line)
        return converted_line
        #return ['store', name_assign, val_assign]

class NumParser(ast.NodeVisitor):
    def visit_Num(self,node):
        return node.n

class UnaryOpParser(ast.NodeVisitor):
    def visit_UnaryOp(self,node):
        if(type(node.op) == ast.USub):
            num = NumParser().visit_Num(node.operand)
            num_with_operator = -1*num
            return num_with_operator
        elif(type(node.op) == ast.UAdd):
            num = NumParser().visit_Num(node.operand)
            num_with_operator = np.abs(num)
            return num_with_operator

class StrParser(ast.NodeVisitor):
    def visit_Str(self,node):
        return node.s

class ListParser(ast.NodeVisitor):
    def visit_List(self,node):
        list_vals = []
        for i in node.elts:
            list_vals.append(general_access_node(i))
        
        return list_vals

class SubscriptParser(ast.NodeVisitor):
    def visit_Subscript(self,node):
        list_slice = []
        name = node.value.id
        if(type(node.slice) == ast.Index):
            index = general_access_node(node.slice.value)
            list_slice.append('index')
            list_slice.append(name)
            list_slice.append(index)
            #converted_line = '%s[%s]' % (name,index)
        elif(type(node.slice) == ast.Slice):
            lower_index = general_access_node(node.slice.lower)
            upper_index = general_access_node(node.slice.upper)
            list_slice.append('slice')
            list_slice.append(name)
            list_slice.append(lower_index)
            list_slice.append(upper_index)
            #converted_line = '%s[%s:%s]' % (name,lower_index,upper_index)
        else:
            pass #@todo ExtSlice
        return 'subscript',list_slice
        #return 'subscript',converted_line

class BinOpParser(ast.NodeVisitor):
    def visit_BinOp(self,node):
        vals = []
        left_val = general_access_node(node.left)
        right_val = general_access_node(node.right)
        
        ast_ops = [ast.Add,ast.Sub,ast.Div,ast.Mult]
        c_ops = ['+','-','/','*']
        operator = node.op
        try:
            op_index = ast_ops.index(type(operator))
            operator = c_ops[op_index]
        except:
            raise TypeError('Binary operator type not handled yet: %s' % operator)
        vals.append(left_val)
        vals.append(operator)
        vals.append(right_val)
        return vals

class ExprParser(ast.NodeVisitor):
    def visit_Expr(self,node):
        global converted_lines, function_body, arg_vars
        line = general_access_node(node.value)
        function = line[0]
        #print('EXPR: ',line)
        if(function == 'print'):
            function = 'std::cout << '
            args = line[1]

            for j in range(0,len(args)):
                found = False
                for i in reversed(range(0,len(converted_lines))):
                    declaration_check = '%s = ' % args[j]
                    if(declaration_check not in converted_lines[i]):
                        pass
                    else:
                        found = True
                if(arg_vars != [] and found == False):
                    for i in range(0,len(arg_vars)):
                        if(args[j] not in arg_vars[i]):
                            pass
                        else:
                            found = True
                else:
                    pass
                if(function_body != [] and found == False):
                    for i in reversed(range(0,len(function_body))):
                        declaration_check = '%s = ' % args[j]
                        if(declaration_check not in converted_lines[i]):
                            pass
                        else:
                            found = True
                
                if(found == False):
                    args[j] = '"%s"' % args[j]
                else:
                    pass
                
            out_args = ''
            for i in range(0,len(args)):
                out_args += args[i] + ' << '
            out_args += 'endl'
            
            converted_line = function + out_args + ';'
            #print('converted: ',converted_line)
        elif('.' in function):
            #this means it is an attribute that should have already been resolved
            args = line[1]
            for i in range(0,len(args)):
                if(type(args[i]) == str):
                    found = False
                    for i in reversed(range(0,len(converted_lines))):
                        declaration_check = '%s = ' % args[j]
                        if(declaration_check not in converted_lines[i]):
                            pass
                        else:
                            found = True
                    if(found == False):
                        args[j] = '"%s"' % args[j]
                    else:
                        pass
                else:
                    pass
            args_string = ''
            for i in range(0,len(args)):
                args_string += str(args[i]) + ', '
            args_string = args_string[:-2]
            converted_line = '%s%s);' % (function,args_string)
            #print(converted_line)
        else:
            #print('TREATED AS FUNCTION CALL: ',function)
            args = line[1]
            for j in reversed(range(0,len(args))):
                found = False
                for i in reversed(range(0,len(converted_lines))):
                    declaration_check = '%s = ' % args[j]
                    if(declaration_check not in converted_lines[i]):
                        pass
                    else:
                        found = True
                if(arg_vars != [] and found == False):
                    for i in range(0,len(arg_vars)):
                        if(args[j] not in arg_vars[i]):
                            pass
                        else:
                            found = True
                else:
                    pass
                if(function_body != [] and found == False):
                    for i in reversed(range(0,len(function_body))):
                        declaration_check = '%s = ' % args[j]
                        if(declaration_check not in converted_lines[i]):
                            pass
                        else:
                            found = True
                
                if(found == False):
                    args[j] = '"%s"' % args[j]
                else:
                    pass
                
            out_args = ''
            for i in range(0,len(args)):
                out_args += args[i] + ', '
            out_args = out_args[:-2]
            
            converted_line = function + '(' + out_args + ')' + ';'
            #converted_line = ['expr',converted_line]
            #print(converted_line)
        return converted_line   
        #return 'func', line
        
class CallParser2(ast.NodeVisitor):
    def visit_Call(self,node):
        func_type = general_access_node(node.func)
        args_list = []
        #print(func_type)
        for i in range(0,len(node.args)):
            args_list.append(general_access_node(node.args[i]))
        if(func_type == 'len'):
            converted_func = args_list[0] + '.size()'
            return converted_func
        else:
            pass
        return func_type, args_list

class ReturnParser(ast.NodeVisitor):
    def visit_Return(self,node):
        if(type(node.value) == None):
            return node.value
        else:
            args_list = general_access_node(node.value)
            return args_list

class TupleParser(ast.NodeVisitor):
    def visit_Tuple(self,node):
        args_list = []
        for i in range(0,len(node.elts)):
            args_list.append(general_access_node(node.elts[i]))
        return args_list

class IfParser(ast.NodeVisitor):
    def visit_If(self,node):
        global converted_lines, top_level_if

        if_block = []
        condition = general_access_node(node.test)
        condition_string = ''
        for i in range(0,len(condition)):
            condition_string += str(condition[i]) + ' '
        condition_string = condition_string[:-1]
        if(top_level_if):
            statement = 'if (%s) {' % condition_string
            top_level_if = False
        else:
            statement = 'else if (%s) {' % condition_string
        if_block.append(statement)

        for i in node.body:
            line = general_access_node(i)
            if_block.append(line)
            
        if_block.append('}')

        if('else if' in if_block[0]):
            if_block.append('else {')
        else:
            pass
        for i in node.orelse:
            line = general_access_node(i)

            if_block.append(line)

        #@todo figure out a better way to ensure correct number of closing braces
        if(if_block[-1][-1] == '}'):
            pass
        else:
            if_block.append('}')

        top_level_if = True

        return if_block

class CompareParser(ast.NodeVisitor):
    def visit_Compare(self,node):
        left_arg = general_access_node(node.left)
        ast_ops = [ast.Eq,ast.NotEq,ast.Lt,ast.LtE,ast.Gt,ast.GtE,ast.Is,ast.IsNot,ast.In,ast.NotIn]
        c_ops = ['==','!=','<','<=','>','>=','TODO','TODO','TODO','TODO']
        
        #@todo handle the is and in operators for c++
        
        full_args = []
        full_args.append(left_arg)
        for i in range(0,len(node.ops)):
            index = ast_ops.index(type(node.ops[i]))
            c_op = c_ops[index]
            full_args.append(c_op)
            full_args.append(general_access_node(node.comparators[i]))
        
        return full_args

class NameParser(ast.NodeVisitor):
    def visit_Name(self,node):
        name = node.id
        return name

class ForParser(ast.NodeVisitor):
    def visit_For(self,node):
        iterator = general_access_node(node.target)
        condition = general_access_node(node.iter)
        if(condition[0] == 'range'):
            lower_limit = condition[1][0]
            upper_limit = condition[1][1]
            for_condition = 'for (int %s = %s; %s < %s; %s++) {' % (iterator,lower_limit,iterator,upper_limit,iterator)
        else:
            vector = condition[0]
            for_condition = 'for (auto %s: %s) {' % (iterator,vector)

        body_block = []
        body_block.append(for_condition)
        for i in node.body:
            body_block.append(general_access_node(i))
        body_block.append('}')
        return body_block

class AttributeParser(ast.NodeVisitor):
    def visit_Attribute(self,node):
        attribute = node.attr
        value = general_access_node(node.value)
        
        if(attribute=='append'):
            attribute = 'push_back'
        else:
            raise TypeError('Attribute type not handled yet: %s,%s' % (attribute,value))
        
        converted_line = '%s.%s(' % (value,attribute)
        return converted_line

def general_access_node(node):
    if(type(node) == ast.FunctionDef):
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
        parsed_node = 'continue;'
    elif(type(node) == ast.Attribute):
        parsed_node = AttributeParser().visit_Attribute(node)
    elif(type(node) == str):
        parsed_node = node
    else:
        raise TypeError('Parser not found for type: %s' % type(node))
        
    return parsed_node

def main(script_to_parse,script_of_function_calls=None):
    global converted_lines, list_types
    list_types = []
    converted_lines = []
    
    if(script_of_function_calls!=None):
        file2 = open(script_of_function_calls,'r').read()
        call_parse = ast.parse(file2)
        for node in call_parse.body:
            funcs_args = []
            for arg in node.value.args:
                arg_val = general_access_node(arg)
                if isinstance(arg_val,int):
                    funcs_args.append('int')
                elif isinstance(arg_val,float):
                    funcs_args.append('float')
                elif isinstance(arg_val,str):
                    funcs_args.append('std::string')
                elif isinstance(arg_val,list):
                    inside_level = arg_val[0]
                    nest_level = 1
                    if isinstance(inside_level,list):
                        inside_level = inside_level[0]
                        nest_level+=1
                        while(isinstance(inside_level,list)):
                            inside_level = inside_level[0]
                            nest_level+=1
                        type_check = type(inside_level)
                        
                    else:
                        type_check = type(inside_level)
                    
                    type_list = ('std::vector<'*nest_level)+str(type_check).replace("<class '",'').replace("'>",'') + ('>'*nest_level)
                    funcs_args.append(type_list)
            list_types.append(funcs_args)
    else:
        pass
    
    file = open(script_to_parse,'r').read()
    tree = ast.parse(file)
    main = False
    for node in tree.body:
        line_test = general_access_node(node)
        
        if(line_test != None and 'auto' in line_test and '{' in line_test):
            pass
        else:
            if(main==False):
                converted_lines.append('int main() {')
                main=True
            else:
                pass
        if(line_test not in converted_lines and line_test != None):
            converted_lines.append(line_test)
        else:
            pass
    converted_lines.append('return 0;')
    converted_lines.append('}')
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
    return converted_lines

def write_file(name_of_output,data):
    file = open(name_of_output,'w+')
    indentation_level=0
    for line in data:
        if(type(line) != list and type(line) != tuple):
            
            open_brace_count = line.count('{')
            close_brace_count = line.count('}')
            if(open_brace_count>close_brace_count):
                file.write(('\t'*indentation_level)+line+'\n')
                indentation_level+=1
            elif(open_brace_count<close_brace_count):
                indentation_level-=1
                file.write(('\t'*indentation_level)+line+'\n')
            else:
                file.write(('\t'*indentation_level)+line+'\n')
            
        else:
            array = np.array(line)
            flattened = array.flatten()
            for body_line in flattened:
                if(type(body_line) == list):
                    for i in body_line:
                        
                        open_brace_count = i.count('{')
                        close_brace_count = i.count('}')
                        if(open_brace_count>close_brace_count):
                            file.write(('\t'*indentation_level)+str(i)+'\n')
                            indentation_level+=1
                        elif(open_brace_count<close_brace_count):
                            indentation_level-=1
                            file.write(('\t'*indentation_level)+str(i)+'\n')
                        else:
                            file.write(('\t'*indentation_level)+str(i)+'\n')
                        
                else:
                    open_brace_count = body_line.count('{')
                    close_brace_count = body_line.count('}')
                    if(open_brace_count>close_brace_count):
                        file.write(('\t'*indentation_level)+str(body_line)+'\n')
                        indentation_level+=1
                    elif(open_brace_count<close_brace_count):
                        indentation_level-=1
                        file.write(('\t'*indentation_level)+str(body_line)+'\n')
                    else:
                        file.write(('\t'*indentation_level)+str(body_line)+'\n')
                    
    file.close()

if __name__ == '__main__':
    top_level_if = True
    print('Beginning Parsing')
    converted_data = main('Test.py','CallTest.py')
    print('Parsing Completed')
    print('Writing File')
    write_file('Test.cpp',converted_data)
    print('Writing Completed')


