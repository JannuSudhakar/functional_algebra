import warnings
import math
import numpy as np

global_variable_index = 0

#Note to Self: things to do while implementing new evaluation functions:
#1 add them to the list_of_evaluation_functions
#2 implement the function either inside or outside variable that will create
#  variables with the new evaluation function
#3 tell the variable.__str function how to deal with it
#4 tell the variable.__evaluate function how to deal with it
#5 tell the variable.__proto_differentiate function how to deal with it
#6 implement the function in the various back ends
#7 go have some coffee
list_of_evaluation_functions = [
"constant",
"identity",
"add",
"product",
"divide",
"pow",
"neg",
"log", #forgive me for not naming this ln, the rest of python calls it log
"exp",
"sin",
"cos",
"tan",
"arcsin",
"arccos",
"arctan",
"arctan2"
]

variable_dictionary = {} #TODO: see if a garbage collector can be written

backend = "vanilla python"

Funcs = {}

Funcs["vanilla python"] = {} #TODO: add more backends
Funcs["numpy"] = {}

#--------------------------backend implementations-----------------------------#
#add implementations:
Funcs["vanilla python"]["add"] = sum
Funcs["numpy"]["add"] = sum

#product implementations:
def t(args):
    ret = 1
    for a in args:
        ret*=a
    return ret
Funcs["vanilla python"]["product"] = t
Funcs["numpy"]["product"] = t

#divide implementations:
Funcs["vanilla python"]["divide"] = lambda x,y: x/y
Funcs["numpy"]["divide"] = np.divide

#pow implementations:
Funcs["vanilla python"]["pow"] = lambda x,y: x**y
Funcs["numpy"]["pow"] = np.power

#neg implementations:
Funcs["vanilla python"]["neg"] = lambda x: -x
Funcs["numpy"]["neg"] = lambda x: -x

#log implementations:
Funcs["vanilla python"]["log"] = math.log
Funcs["numpy"]["log"] = np.log

#exp implementations:
Funcs["vanilla python"]["exp"] = math.exp
Funcs["numpy"]["exp"] = np.exp

#sin implementations:
Funcs["vanilla python"]["sin"] = math.sin
Funcs["numpy"]["sin"] = np.sin

#cos implementations:
Funcs["vanilla python"]["cos"] = math.cos
Funcs["numpy"]["cos"] = np.cos

#tan implementations:
Funcs["vanilla python"]["tan"] = math.tan
Funcs["numpy"]["tan"] = np.tan

#arcsin implementations:
Funcs["vanilla python"]["arcsin"] = math.asin
Funcs["numpy"]["arcsin"] = np.arcsin

#arccos implementations:
Funcs["vanilla python"]["arccos"] = math.acos
Funcs["numpy"]["arccos"] = np.arccos

#arctan implementations:
Funcs["vanilla python"]["arctan"] = math.atan
Funcs["numpy"]["arctan"] = np.arctan

#arctan2 implementations:
Funcs["vanilla python"]["arctan2"] = math.atan2
Funcs["numpy"]["arctan2"] = np.arctan2

#--------------------------backend implementations-----------------------------#

def set_backend(B):
    #TODO: make it throw error if unknown backend is set, figure out how to add
    #custom backends
    global backend
    backend = B

class variable:
    def __init__(self,name = None,**kwargs):
        global global_variable_index
        self.variable_index = global_variable_index
        variable_dictionary[self.variable_index] = self
        self.name = name if name is not None else f"variable{self.variable_index}"
        self.named = name is not None
        global_variable_index += 1
        if("constant" in  kwargs):
            self.required_variables_set = set({})
            self.evaluation_function = "constant"
            self.argument_variables = []
            self.argument_constants = [kwargs["constant"]]
        else:
            self.required_variables_set = {self.variable_index}
            self.evaluation_function = "identity"
            self.argument_variables = [self.variable_index]
            self.argument_constants = []

    def half_hash(self):
        ret = self.evaluation_function + ":"
        for c in self.argument_constants:
            T = type(c)
            if(T != complex and T != int and T != float):
                return None
            ret += str(c)
            ret += ":"
        ret += ":::&^&:::"
        for v in self.argument_variables:
            ret += str(v)
            ret += ":"
        return ret

    def give_name(self,name):
        self.name = name
        self.named = True

    @staticmethod
    def __add_multiple(*args):
        #supports passing an arbitrary number of None in args for convenience reasons
        if(type(args[0]) == list or type(args[0]) == tuple):
            if(len(args)>1):
                warnings.warn("since the first argument was a list or tuple subsequent arguments were ignored")
            args = args[0]
        ret = variable()
        ret.evaluation_function = "add"
        ret.required_variables_set = set()
        ret.argument_variables = []
        atleast_one_variable = False
        for a in args:
            if(a is None):
                continue
            if(type(a) == variable):
                atleast_one_variable = True
                ret.required_variables_set = ret.required_variables_set.union(a.required_variables_set)
                if(a.evaluation_function != "add"):
                    ret.argument_variables.append(a.variable_index)
                    ret.argument_constants.append(1)
                else:
                    ret.argument_variables += a.argument_variables
                    ret.argument_constants += a.argument_constants
            else:
                ret.argument_variables.append(None)
                ret.argument_constants.append(a)
        assert(atleast_one_variable)
        if(len(ret.argument_variables) == 1):
            return variable_dictionary[ret.argument_variables[0]]
        return ret

    @staticmethod
    def __mul(*args):
        #supports passing arbitrary number of None in arguments, this time passing atleast one None will make it return None
        if(type(args[0]) == list or type(args[0]) == tuple):
            if(len(args)>1):
                warnings.warn("since the first argument was a list or tuple subsequent arguments were ignored")
            args = args[0]
        ret = variable()
        ret.evaluation_function = "product"
        ret.required_variables_set = set()
        ret.argument_variables = []
        atleast_one_variable = False
        atleast_one_None = False
        constant = None
        for a in args:
            if(a is None):
                atleast_one_None = True
            if(type(a) == variable):
                atleast_one_variable = True
                if(a.evaluation_function == "constant"):
                    constant = a.argument_constants[0] if constant is None else a.argument_constants[0] * constant
                else:
                    ret.required_variables_set = ret.required_variables_set.union(a.required_variables_set)
                    if(a.evaluation_function != "product"):
                        ret.argument_variables.append(a.variable_index)
                        ret.argument_constants.append(None)
                    else:
                        for i in range(len(a.argument_variables)):
                            if(a.argument_variables[i] is not None):
                                ret.argument_variables.append(a.argument_variables[i])
                                ret.argument_constants.append(a.argument_constants[i])
                            else:
                                constant = a.argument_constants[i] if constant is None else constant * a.argument_constants[i]
            else:
                if(a is None):
                    atleast_one_None = True
                    break
                constant = a if constant is None else a * constant
        if(constant is not None):
            if(len(ret.argument_variables) == 0):
                ret = variable(constant = constant)
            else:
                ret.argument_variables = [None] + ret.argument_variables
                ret.argument_constants = [constant] + ret.argument_constants
        if(atleast_one_None): return None
        assert(atleast_one_variable)
        if(len(ret.argument_variables) == 1):
            return variable_dictionary[ret.argument_variables[0]]
        return ret

    @staticmethod
    def __add(a,b,minus=False):
        ret = variable()
        ret.evaluation_function = "add"
        ret.required_variables_set = set()
        ret.argument_variables = []
        ret.argument_constants = []
        if(type(a)!=variable and type(b)!=variable):
            raise TypeError("both arguments are not not of type variable")
        if(type(a)==variable):
            ret.required_variables_set = ret.required_variables_set.union(a.required_variables_set)
            if(a.evaluation_function=="add"):
                ret.argument_variables += a.argument_variables
                ret.argument_constants += a.argument_constants
            else:
                ret.argument_variables.append(a.variable_index)
                ret.argument_constants.append(True)
        else:
            ret.argument_variables.append(None)
            ret.argument_constants.append(a)

        if(type(b)==variable):
            ret.required_variables_set = ret.required_variables_set.union(b.required_variables_set)
            if(b.evaluation_function == "add"):
                ret.argument_variables += b.argument_variables
                if(minus):
                    for c in b.argument_constants:
                        ret.argument_constants.append(-c)
                else:
                    ret.argument_constants += b.argument_constants
            else:
                ret.argument_variables.append(b.variable_index)
                ret.argument_constants.append(not minus)
        else:
            ret.argument_variables.append(None)
            ret.argument_constants.append(-b if minus else b)

        return ret

    @staticmethod
    def __truediv(a,b):
        if(type(a)!=variable and type(b)!=variable):
            raise TypeError("both arguments are not of type variable")
        ret = variable()
        ret.required_variables_set = set()
        ret.argument_variables = []
        ret.evaluation_function = "divide"
        for c in [a,b]:
            if(type(c) == variable):
                ret.argument_variables.append(c.variable_index)
                ret.required_variables_set = ret.required_variables_set.union(c.required_variables_set)
                ret.argument_constants.append(None)
            else:
                ret.argument_variables.append(None)
                ret.argument_constants.append(c)
        return ret

    @staticmethod
    def __pow(a,b):
        if(type(a)!=variable and type(b)!=variable):
            raise TypeError("both arguments are not of type variable")

        ret = variable()
        ret.required_variables_set = set()
        ret.argument_variables = []
        ret.evaluation_function = "pow"
        for c in [a,b]:
            if(type(c) == variable):
                ret.argument_variables.append(c.variable_index)
                ret.required_variables_set = ret.required_variables_set.union(c.required_variables_set)
                ret.argument_constants.append(None)
            else:
                ret.argument_variables.append(None)
                ret.argument_constants.append(c)
        return ret

    def __add__(self,a):
        return variable.__add(self,a)

    def __radd__(self,a):
        return variable.__add(a,self)

    def __sub__(self,a):
        return variable.__add(self,a,minus=True)

    def __rsub__(self,a):
        return variable.__add(a,self,minus=True)

    def __mul__(self,a):
        return variable.__mul(self,a)

    def __rmul__(self,a):
        return variable.__mul(a,self)

    def __truediv__(self,a):
        return variable.__truediv(self,a)

    def __rtruediv__(self,a):
        return variable.__truediv(a,self)

    def __pow__(self,a):
        return variable.__pow(self,a)

    def __rpow__(self,a):
        return variable.__pow(a,self)

    def __single_argument_variable(self,eval_function):
        ret = variable()
        ret.evaluation_function = eval_function
        ret.required_variables_set = set(self.required_variables_set)
        ret.argument_variables = [self.variable_index]
        return ret

    def __neg__(self):
        return self.__single_argument_variable("neg")

    def log(self):
        return self.__single_argument_variable("log")

    def exp(self):
        return self.__single_argument_variable("exp")

    def sin(self):
        return self.__single_argument_variable("sin")

    def cos(self):
        return self.__single_argument_variable("cos")

    def tan(self):
        return self.__single_argument_variable("tan")

    def arcsin(self):
        return self.__single_argument_variable("arcsin")

    def arccos(self):
        return self.__single_argument_variable("arccos")

    def arctan(self):
        return self.__single_argument_variable("arctan")

    def __rshift__(self,a):
        return assigned_variable(self,a)

    def __proto_differentiate(self,v,arg_derivatives):
        all_None = True
        for ad in arg_derivatives:
            if(ad is not None):
                all_None = False
        if(all_None):
            return None
        if(self.evaluation_function == "identity"):
            if(v.variable_index == self.variable_index):
                return variable(constant=1).variable_index
            else:
                return None
        elif(self.evaluation_function == "constant"):
            return None
        elif(self.evaluation_function == "add"):
            ret = None
            for i in range(len(arg_derivatives)):
                arg_der = arg_derivatives[i]
                if(arg_der is None):
                    continue
                if(ret is None):
                    ret = (1 if self.argument_constants[i] else -1)*arg_der
                else:
                    ret += (1 if self.argument_constants[i] else -1)*arg_der
            return ret.variable_index
        elif(self.evaluation_function == "product"):
            addands = []
            for i in range(len(self.argument_variables)):
                avi = self.argument_variables[i]
                if(avi is not None):
                    av = variable_dictionary[avi]
                    t = [arg_derivatives[index] if index == i else (variable_dictionary[self.argument_variables[index]]  if self.argument_variables[index] is not None else self.argument_constants[index]) for index in range(len(self.argument_variables))]
                    addands.append(variable.__mul(t))
            return variable.__add_multiple(addands).variable_index
        elif(self.evaluation_function == "divide"):
            if(arg_derivatives[0] is None):
                numerator = variable_dictionary[self.argument_variables[0]] if self.argument_variables[0] is not None else self.argument_constants[0]
                denominator = variable_dictionary[self.argument_variables[1]]
                return (-(numerator*arg_derivatives[1])/(denominator**2)).variable_index
            if(arg_derivatives[1] is None):
                denominator = variable_dictionary[self.argument_variables[1]] if self.argument_variables[1] is not None else self.argument_constants[1]
                return (arg_derivatives[0]/denominator).variable_index
            numerator = variable_dictionary[self.argument_variables[0]] if self.argument_variables is not None else self.argument_constants[0]
            denominator = variable_dictionary[self.argument_variables[1]] if self.argument_variables[1] is not None else self.argument_constants[1]
            return ((denominator*arg_derivatives[0] - numerator*arg_derivatives[1])/(denominator**2)).variable_index
        elif(self.evaluation_function == "pow"):
            ret = None
            arg1 = variable_dictionary[self.argument_variables[0]] if self.argument_variables is not None else self.argument_constants[0]
            arg2 = variable_dictionary[self.argument_variables[1]] if self.argument_variables[1] is not None else self.argument_constants[1]
            if(arg_derivatives[0] is not None):
                arg2is1 = False
                if(type(arg2) == variable):
                    if(arg2.evaluation_function == "constant"):
                        if(arg2.argument_constants[0] == 1):
                            arg2is1 = True
                else:
                    arg2is1 = (arg2 == 1)
                arg2is0 = False
                if(type(arg2) == variable):
                    if(arg2.evaluation_function == "constant"):
                        if(arg2.argument_constants[0] == 0):
                            arg2is0 = True
                else:
                    arg2is0 = (arg2 == 0)
                if(arg2is1):
                    ret = arg_derivatives[0]
                elif(not arg2is0):
                    ret = arg2*(arg1**(arg2-1))*arg_derivatives[0]
            if(arg_derivatives[1] is not None):
                t = arg1.log()*self*arg_derivatives[1]
                ret = t if ret is None else ret + t
            return ret.variable_index
        elif(self.evaluation_function == "neg"):
            return (-arg_derivatives[0]).variable_index
        elif(self.evaluation_function == "log"):
            return (arg_derivatives[0]/variable_dictionary[self.argument_variables[0]]).variable_index
        elif(self.evaluation_function == "exp"):
            return (arg_derivatives[0]*self).variable_index
        elif(self.evaluation_function == "sin"):
            return (arg_derivatives[0]*(variable_dictionary[self.argument_variables[0]].cos())).variable_index
        elif(self.evaluation_function == "cos"):
            return (-(arg_derivatives[0]*(variable_dictionary[self.argument_variables[0]].sin()))).variable_index
        elif(self.evaluation_function == "tan"):
            return (arg_derivatives[0]/(variable_dictionary[self.argument_variables[0]].cos()**2)).variable_index
        elif(self.evaluation_function == "arcsin"):
            ret = (1-variable_dictionary[self.argument_variables[0]]**2)**0.5
            ret = arg_derivatives[0]/ret
            return ret.variable_index
        elif(self.evaluation_function == "arccos"):
            ret = (1-variable_dictionary[self.argument_variables[0]]**2)**0.5
            ret = -(arg_derivatives[0]/ret)
            return ret.variable_index
        elif(self.evaluation_function == "arctan"):
            ret = 1+variable_dictionary[self.argument_variables[0]]**2
            ret = arg_derivatives[0]/ret
            return ret.variable_index
        elif(self.evaluation_function == "arctan2"):
            ret = None
            arg1 = variable_dictionary[self.argument_variables[0]] if self.argument_variables is not None else self.argument_constants[0]
            arg2 = variable_dictionary[self.argument_variables[1]] if self.argument_variables[1] is not None else self.argument_constants[1]
            denominator = arg1**2 + arg2**2
            if(arg_derivatives[0] is not None):
                ret = arg2*arg_derivatives[0]
            if(arg_derivatives[1] is not None):
                t = -arg1*arg_derivatives[1]
                ret = t if ret is None else ret + t
            ret = ret/denominator
            return ret.variable_index

        else:
            raise Exception(f"differentiation not implemented for the function {self.evaluation_function}")

    def __differentiate_once(self,v):
        if(type(v) != variable):
            raise TypeError(f"recieved argument of type {type(v)} but expected of type {type(variable)}")
        if(v.evaluation_function != "identity"):
            raise Exception("the variable you are asking to differentiate by is not an independet variable.")
        already_differentiated_variables = {}
        stack = [self.variable_index]
        while(len(stack) > 0):
            curr_var_index = stack.pop()
            if(curr_var_index is None):
                continue
            if(curr_var_index in already_differentiated_variables):
                continue
            curr_var = variable_dictionary[curr_var_index]
            ready_to_differentiate = True
            for av in curr_var.argument_variables:
                if(av is not None and av not in already_differentiated_variables and av != curr_var_index):
                    ready_to_differentiate = False
                    break
            if(not ready_to_differentiate):
                stack.append(curr_var_index)
                stack = stack + curr_var.argument_variables
            else:
                if(curr_var.evaluation_function == "identity"):
                    already_differentiated_variables[curr_var_index] = curr_var_index
                arg_derivatives = []
                for av in curr_var.argument_variables:
                    if(av is None or already_differentiated_variables[av] is None):
                        arg_derivatives.append(None)
                    else:
                        arg_derivatives.append(variable_dictionary[already_differentiated_variables[av]])
                already_differentiated_variables[curr_var_index] = curr_var.__proto_differentiate(v,arg_derivatives)
        return variable_dictionary[already_differentiated_variables[self.variable_index]]

    def differentiate(self,*args):
        #let's just support passing no arguments and getting the same variable back for possible convenience.
        ret = self
        for a in args:
            ret = ret.__differentiate_once(a)
        return ret

    @staticmethod
    def __evaluate(evaluation_function,arg_vars,arg_consts):
        if(evaluation_function == "constant"):
            return arg_consts[0]
        elif(evaluation_function == "identity"):
            return arg_vars[0]
        elif(evaluation_function == "add"):
            arglist = []
            for i in range(len(arg_vars)):
                if(arg_vars[i] is None):
                    arglist.append(arg_consts[i])
                else:
                    E = 1 if arg_consts[i] else -1
                    E *= arg_vars[i]
                    arglist.append(E)
            return Funcs[backend]["add"](arglist)
        elif(evaluation_function == "product"):
            arglist = []
            for i in range(len(arg_vars)):
                if(arg_vars[i] is None):
                    arglist.append(arg_consts[i])
                else:
                    E = arg_vars[i]
                    arglist.append(E)
            return Funcs[backend]["product"](arglist)
        elif(evaluation_function == "divide"):
            arglist = []
            for i in range(2):
                if(arg_vars[i] is not None):
                    arglist.append(arg_vars[i])
                else:
                    arglist.append(arg_consts[i])
            return Funcs[backend]["divide"](arglist[0], arglist[1])
        elif(evaluation_function == "pow"):
            arglist = []
            for i in range(2):
                if(arg_vars[i] is not None):
                    arglist.append(arg_vars[i])
                else:
                    arglist.append(arg_consts[i])
            return Funcs[backend]["pow"](arglist[0], arglist[1])
        elif(evaluation_function == "neg"):
            return Funcs[backend]["neg"](arg_vars[0])
        elif(evaluation_function == "log"):
            return Funcs[backend]["log"](arg_vars[0])
        elif(evaluation_function == "exp"):
            return Funcs[backend]["exp"](arg_vars[0])
        elif(evaluation_function == "sin"):
            return Funcs[backend]["sin"](arg_vars[0])
        elif(evaluation_function == "cos"):
            return Funcs[backend]["cos"](arg_vars[0])
        elif(evaluation_function == "tan"):
            return Funcs[backend]["tan"](arg_vars[0])
        elif(evaluation_function == "arcsin"):
            return Funcs[backend]["arcsin"](arg_vars[0])
        elif(evaluation_function == "arccos"):
            return Funcs[backend]["arccos"](arg_vars[0])
        elif(evaluation_function == "arctan"):
            return Funcs[backend]["arctan"](arg_vars[0])
        elif(evaluation_function == "arctan2"):
            arglist = []
            for i in range(2):
                if(arg_vars[i] is not None):
                    arglist.append(arg_vars[i])
                else:
                    arglist.append(arg_consts[i])
            return Funcs[backend]["arctan2"](arglist[0], arglist[1])

        raise ValueError("the evaluation function seems to be not implemented")

    def evaluate(self,*args):
        if(type(args[0]) == list or type(args[0]) == tuple):
            if(len(args)>1):
                warnings.warn("the first argument to evaluate was a list, ignoring other arguments")
            args = args[0]
        #TODO: lots and lots of optimization.
        if(self.evaluation_function == "constant"):
            return self.argument_constants[0]
        all_required_variables_assigned = True
        assignment_dict = {}
        for vi in self.required_variables_set:
            assignment_dict[vi] = {"assigned": False}
        for a in args:
            if(a.variable_index in assignment_dict):
                if(assignment_dict[a.variable_index]["assigned"]):
                    raise Exception(f"the variable {str(a)} has been assigned twice")
                assignment_dict[a.variable_index]["assigned"] = True
                assignment_dict[a.variable_index]["value"] = a.value
        for vi in assignment_dict:
            if(not assignment_dict[vi]["assigned"]):
                all_required_variables_assigned = False
        assert(all_required_variables_assigned)
        #TODO:check for cycles
        #breadth first search
        pending_variables = [self.variable_index]
        visited_variables = set()
        tracking_dict = {}
        while (len(pending_variables) > 0):
            curr_var_index = pending_variables.pop(0)
            if(curr_var_index is None):
                continue
            curr_var = variable_dictionary[curr_var_index]
            if(curr_var.evaluation_function != "identity"):
                pending_variables += curr_var.argument_variables
            visited_variables.add(curr_var_index)
            if(curr_var_index in visited_variables):
                if(curr_var_index not in tracking_dict):
                    tracking_dict[curr_var_index] = {
                    "from_vars": set(),
                    "to_vars": set(),
                    "total_no_encounters": 0,
                    "curr_no_encounters": 0,
                    "evaluated": False
                    }
                tracking_dict[curr_var_index]["total_no_encounters"] += 1
                tracking_dict[curr_var_index]["from_vars"] = set(curr_var.argument_variables)
                if(None in tracking_dict[curr_var_index]["from_vars"]): tracking_dict[curr_var_index]["from_vars"].remove(None)
                for v in tracking_dict[curr_var_index]["from_vars"]:
                    if(v not in tracking_dict):
                        tracking_dict[v] = {
                        "from_vars": set(),
                        "to_vars": set(),
                        "total_no_encounters": 0,
                        "curr_no_encounters": 0,
                        "evaluated": False
                        }
                    if(curr_var.evaluation_function != "constant" and curr_var.evaluation_function != "identity"):
                        tracking_dict[v]["to_vars"].add(curr_var_index)
            tracking_dict[curr_var_index]["total_no_encounters"] += 1
        stack = list(self.required_variables_set)
        while (len(stack) > 0):
            curr_var_index = stack.pop()
            if(not tracking_dict[curr_var_index]["evaluated"]):
                ready_to_evaluate = True
                curr_var = variable_dictionary[curr_var_index]
                for tv in tracking_dict[curr_var_index]["from_vars"]:
                    if(not (tracking_dict[tv]["evaluated"] or curr_var.evaluation_function == "constant" or curr_var.evaluation_function == "identity")):
                        ready_to_evaluate = False
                        break
                if(ready_to_evaluate):
                    arg_vars = []
                    for av in curr_var.argument_variables:
                        if(av is None):
                            arg_vars.append(None)
                        else:
                            if(av not in self.required_variables_set):
                                arg_vars.append(tracking_dict[av]["evaluated_value"])
                            else:
                                arg_vars.append(assignment_dict[av]["value"])
                            tracking_dict[av]["curr_no_encounters"] += 1
                            if(tracking_dict[av]["curr_no_encounters"] == tracking_dict[av]["total_no_encounters"]):
                                tracking_dict[av]["evaluated_value"] = None #clearing space :)
                    tracking_dict[curr_var_index]["evaluated_value"] = variable.__evaluate(curr_var.evaluation_function,arg_vars,curr_var.argument_constants)
                    tracking_dict[curr_var_index]["evaluated"] = True
                    stack = stack + list(tracking_dict[curr_var_index]["to_vars"])
                else:
                    stack.append(curr_var_index)
                    stack = stack + list(tracking_dict[curr_var_index]["from_vars"])
        return tracking_dict[self.variable_index]['evaluated_value']

    @staticmethod
    def __print_graph(a,indents):
        indent_text = ""
        for indent in indents:
            indent_text += str(indent)
            indent_text += "."
        print(indent_text,end="")
        print(a)
        print(indent_text,end="")
        print(f"variable index: {a.variable_index}, name: {a.name}, named: {a.named}")
        indent_text += "--"
        print(indent_text,end="")
        print("evaluation_function: ",a.evaluation_function)
        print(indent_text,end="")
        print("argument_variables: ",a.argument_variables)
        print(indent_text,end="")
        print("argument_constants: ",a.argument_constants,'\n')
        if(a.evaluation_function == "identity"):
            return
        for b in a.argument_variables:
            if b is not None:
                variable.__print_graph(variable_dictionary[b],indents+[a.variable_index])

    def print_graph(self):
        variable.__print_graph(self,[])

    @staticmethod
    def __str(self,brackets=True): #I guess its a bad idea to name the argument self, but I won't change it rn
        if(self.named or self.evaluation_function == "identity"):
            return self.name
        if(self.evaluation_function == "constant"):
            return ":" + str(self.argument_constants[0]) + ":"
        elif(self.evaluation_function == "add"):
            ret = "(" if brackets else ""
            for i in range(len(self.argument_variables)):
                if(self.argument_variables[i] is not None):
                    if(self.argument_constants[i]):
                        ret += "" if i==0 else "+"
                    else:
                        ret += "-"
                    ret += variable.__str(variable_dictionary[self.argument_variables[i]])
                else:
                    s = str(self.argument_constants[i])
                    if(s[0]!="-" or s[0]!="+"):
                        ret += "+" if i!=0 else ""
                    ret += s
            ret += ")" if brackets else ""
            return ret

        elif(self.evaluation_function == "product"):
            ret = "(" if brackets else ""
            for i in range(len(self.argument_variables)):
                if(i>0):
                    ret += "×"
                if(self.argument_variables[i] is not None):
                    ret += variable.__str(variable_dictionary[self.argument_variables[i]])
                else:
                    ret += str(self.argument_constants[i])
            ret += ")" if brackets else ""
            return ret

        elif(self.evaluation_function == "divide"):
            ret = "(" if brackets else ""
            sstrs = []
            for i in range(2):
                if(self.argument_variables[i] is not None):
                    var = variable_dictionary[self.argument_variables[i]]
                    sstrs.append(variable.__str(var))
                else:
                    sstrs.append(str(self.argument_constants[i]))
            ret += sstrs[0]
            ret += "/"
            ret += sstrs[1]
            ret += ")" if brackets else  ""
            return ret
        elif(self.evaluation_function == "pow"):
            ret = "(" if brackets else ""
            sstrs = []
            for i in range(2):
                if(self.argument_variables[i] is not None):
                    var = variable_dictionary[self.argument_variables[i]]
                    sstrs.append(variable.__str(var))
                else:
                    sstrs.append(str(self.argument_constants[i]))
            ret += sstrs[0]
            ret += "**"
            ret += sstrs[1]
            ret += ")" if brackets else ""
            return ret
        elif(self.evaluation_function == "neg"):
            ret = "(-" if brackets else "-"
            ret += variable.__str(variable_dictionary[self.argument_variables[0]])
            ret += ")" if brackets else  ""
            return ret
        elif(self.evaluation_function == "log"):
            return f"log({variable.__str(variable_dictionary[self.argument_variables[0]],brackets=False)})"
        elif(self.evaluation_function == "exp"):
            return f"exp({variable.__str(variable_dictionary[self.argument_variables[0]],brackets=False)})"
        elif(self.evaluation_function == "sin"):
            return f"sin({variable.__str(variable_dictionary[self.argument_variables[0]],brackets=False)})"
        elif(self.evaluation_function == "cos"):
            return f"cos({variable.__str(variable_dictionary[self.argument_variables[0]],brackets=False)})"
        elif(self.evaluation_function == "tan"):
            return f"tan({variable.__str(variable_dictionary[self.argument_variables[0]],brackets=False)})"
        elif(self.evaluation_function == "arcsin"):
            return f"arcsin({variable.__str(variable_dictionary[self.argument_variables[0]],brackets=False)})"
        elif(self.evaluation_function == "arccos"):
            return f"arccos({variable.__str(variable_dictionary[self.argument_variables[0]],brackets=False)})"
        elif(self.evaluation_function == "arctan"):
            return f"arctan({variable.__str(variable_dictionary[self.argument_variables[0]],brackets=False)})"
        elif(self.evaluation_function == "arctan2"):
            sstrs = []
            for c in range(2):
                if(self.argument_variables[c] is None):
                    sstrs.append(str(self.argument_constants))
                else:
                    sstrs.append(variable.__str(variable_dictionary[self.argument_variables[c]],brackets=False))
            return f"arctan2({sstrs[0]},{sstrs[1]})"

        return f"__str not implemented for the evaluation_function {self.evaluation_function}"

    def __str__(self):
        return variable.__str(self,False)

class assigned_variable:
    def __init__(self,variable,value):
        if(variable.evaluation_function == "constant"):
            raise Exception("cannot assign a value to a constant variable")
        if(variable.evaluation_function != "identity"):
            raise Exception("tried to create an assigned variable object assigning a value to a variable that is not a leaf variable")
        if(value is None):
            raise ValueError("the value you are trying to assign to the variable is None, this is not allowed as a matter of design.")
        if(type(value) == variable):
            raise TypeError("a variable cannot be assigned a variable as a value, I don't know if I will ever support something like this.")
        self.variable_index = variable.variable_index
        self.value = value

#---------------------------------functions-------------------------------------
def exp(x):
    return x.exp()

def sin(x):
    return x.sin()

def cos(x):
    return x.cos()

def tan(x):
    return x.tan()

def arccos(x):
    return x.arccos()

def arcsin(x):
    return x.arcsin()

def arctan(x):
    return x.arctan()

def arctan2(y,x):
    if(type(x) != variable and type(y) != variable):
        raise TypeError("neither argument is of type variable")
    ret = variable()
    ret.evaluation_function = "arctan2"
    ret.required_variables_set = set()
    ret.argument_variables = []
    ret.argument_constants = []
    for c in [y,x]:
        if(type(c)==variable):
            ret.required_variables_set = ret.required_variables_set.union(c.required_variables_set)
            ret.argument_variables.append(c.variable_index)
            ret.argument_constants.append(None)
        else:
            ret.argument_variables.append(None)
            ret.argument_constants.append(c)
    return ret

if(__name__ == "__main__"):
    a = variable("a")
    b = variable("b")
    c = a+b+10
    d = 9-a+b
    e = c*d
    f = c/d
    g = d - e + f
    h = 89/g
    i = variable(constant = 19)
    j = h + i
    values = [a>>1,b>>3]
    print(a,a.evaluate(values))
    print(b,b.evaluate(values))
    print(c,c.evaluate(values))
    print(d,d.evaluate(values))
    print(e,e.evaluate(values))
    print(f,f.evaluate(values))
    print(g,g.evaluate(values))
    print(h,h.evaluate(values))
    print(i,i.evaluate(values))
    print(j,j.evaluate(values))
    print("---------------------")
    print("---------------------")
    A = variable("A")
    B = variable("B")
    C = variable("C")
    D = A.log()
    E = (A**1)*(A**1) + 2*A*B*D + B**2 + C
    F = E.differentiate(A)
    G = E.differentiate(B)
    H = E.differentiate(A,B)
    I = E.differentiate(A,A)
    print(A)
    print(B)
    print(C)
    print(D)
    print(E)
    print(F)
    print(G)
    print(H)
    print(I)
