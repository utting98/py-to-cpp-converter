#The following is a new test method using the AST library to parse nodes in a script and convert those parsed nodes individualy in to cpp
#script, once this method is up to date with the old method it will be fully commented to explain approach, it has been included now for
#any potential contributors to see what new approach is being taken to replace the old line by line string replacement method


import ast
import numpy as np

list_types = []
converted_lines = []

def get_arg_type(arg):
    global list_types
    if isinstance(arg,ast.Num):
        return arg.n
    elif isinstance(arg,ast.List):
        for i in arg.elts:
            list_types.append(get_arg_type(i))
        temp = list_types
        list_types = []
        return temp
    elif isinstance(arg,ast.Str):
        return 'string'

class CallParser(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.arg_types_list = []
    
    def visit_Call(self,node):
        arg_types = []
        for i in node.args:
            a = get_arg_type(i)
            if isinstance(a,str):
                arg_types.append('string')
            elif isinstance(a,float):
                arg_types.append('float')
            elif isinstance(a,int):
                arg_types.append('int')
            elif isinstance(a,list):
                test = []
                for i in a:
                    test.append(type(i))
                if test[1:] == test[:-1]:
                    pass
                else:
                    raise TypeError('Lists in C++ require all element types to be the same, your list was found to have types: %s' % test)
                arg_types.append('vector%s' % str(test[0]).replace("class ","").replace("'",""))
        self.arg_types_list.append(arg_types)
        self.functions.append(node.func.id)

class FunctionParser(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        global converted_lines, function_body, arg_vars
        arg_vars = []
        #@todo add types to args 
        args_string = ''
        for i in node.args.args:
            arg_vars.append(i.arg)
            args_string += i.arg + ', '
        args_string = args_string[:-2]
        
        function_body = []
        for i in node.body:
            if(type(i) == ast.Return):
                line = ReturnParser().visit_Return(i)
                command = []
                command.append('return')
                command.append(line)
                function_body.append(command)
            else:
                function_body.append(general_access_node(i))
        
        function_def = 'auto %s (%s) {' % (node.name, args_string)
        converted_lines.append(function_def)
        converted_lines.append(function_body)
        arg_vars = []
        function_body = []
        return
        #return 'function_def', node.name, arg_vars, function_body

class AssignParser(ast.NodeVisitor):
    global converted_lines
    def visit_Assign(self,node):
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
        if(type_check == list and val_assign[0] == 'BinOp'):
            op_string = val_assign[1]
            eq_string = ''
            for i in op_string:
                eq_string += str(i) + ' '
            eq_string = eq_string[:-1]
            val_assign = eq_string
            if('+' in val_assign):
                #@todo check when sorted definition properly
                for i in reversed(range(0,len(converted_lines))):
                    find_def = '%s = ' %  op_string[0]
                    if(find_def in converted_lines[i]):
                        type_check = converted_lines[i].split(' ')[0]
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
            type_check = 'vector<'*(nest_level+1)+str(type(inside_level))+'>'*(nest_level+1)
            val_assign = str(val_assign).replace('[','{').replace(']','}')
        elif(type_check == str):
            val_assign = '"%s"' % val_assign
            type_check = 'string'
        else:
            pass
        converted_line = str(type_check).replace("<class '",'').replace("'>","") + ' %s = %s;' % (name_assign,val_assign)
        print(converted_line)
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
        elif(type(node.slice) == ast.Slice):
            lower_index = general_access_node(node.slice.lower)
            upper_index = general_access_node(node.slice.upper)
            list_slice.append('slice')
            list_slice.append(name)
            list_slice.append(lower_index)
            list_slice.append(upper_index)
        else:
            pass #@todo ExtSlice
        return list_slice

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
        print('EXPR: ',line)
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
            print(converted_line)
        else:
            #@todo function call in here
            converted_line = None
        return converted_line   
        #return 'func', line
        
class CallParser2(ast.NodeVisitor):
    def visit_Call(self,node):
        func_type = general_access_node(node.func)
        args_list = []
        
        for i in range(0,len(node.args)):
            args_list.append(general_access_node(node.args[i]))
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
        total_block = []
        if_block = []
        total_block.append('if')

        if_block.append(general_access_node(node.test))
        body = []
        for i in node.body:
            body.append(general_access_node(i))

        if_block.append(body)

        elif_block = []
        for i in node.orelse:
            elif_block.append(general_access_node(i))

        total_block.append(if_block)
        total_block.append(elif_block)

        return total_block

class CompareParser(ast.NodeVisitor):
    def visit_Compare(self,node):
        left_arg = general_access_node(node.left)
        
        full_args = []
        full_args.append(left_arg)
        for i in range(0,len(node.ops)):
            full_args.append(node.ops[i])
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
        
        body_block = []
        for i in node.body:
            body_block.append(general_access_node(i))

        return 'for', iterator, condition, body_block

class AttributeParser(ast.NodeVisitor):
    def visit_Attribute(self,node):
        attribute = node.attr
        value = general_access_node(node.value)
        #print('Attribute: ',attribute,value)
        if(attribute=='append'):
            attribute = 'push_back'
        else:
            raise TypeError('Attribute type not handled yet: %s,%s' % (attribute,value))
        converted_line = '%s.%s(' % (value,attribute)
        #return value, attribute
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
        parsed_node = node
    elif(type(node) == ast.Attribute):
        parsed_node = AttributeParser().visit_Attribute(node)
    elif(type(node) == str):
        parsed_node = node
    else:
        raise TypeError('Parser not found for type: %s' % type(node))
        
    return parsed_node

def main(script_to_parse,script_of_function_calls=None):
    global converted_lines
    if(script_of_function_calls!=None):
        file2 = open(script_of_function_calls,'r').read()
        call_parse = ast.parse(file2)
        function_call_parser = CallParser()
        function_call_parser.visit(call_parse)
    else:
        pass
    
    file = open(script_to_parse,'r').read()
    tree = ast.parse(file)
    
    parsed_lines = []
    for node in tree.body:
        line = []
        line_test = general_access_node(node)

        line.append(line_test)
        if(line_test not in converted_lines and line_test != None):
            converted_lines.append(line_test)
        else:
            pass     
      
        parsed_lines.append(line)
    
    #print(ast.dump(tree))
    
    
    
    
    for i in range(0,len(parsed_lines)):
        if(parsed_lines[i]==[]):
            parsed_lines[i] = ['#Parsing Failed']
        else:
            pass
        
    return parsed_lines

if __name__ == '__main__':
    main('Test.py','CallTest.py')



