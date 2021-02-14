import warnings

global_variable_index = 0

list_of_evaluation_functions = [
"identity",
"add",
"product",
"divide",
]

variable_dictionary = {}

class variable:
    def __init__(self,name = None, backend= None):
        global global_variable_index
        self.variable_index = global_variable_index
        variable_dictionary[self.variable_index] = self
        self.name = name if name is not None else f"variable{self.variable_index}"
        self.named = name is not None
        self.backend = backend
        global_variable_index += 1
        self.required_variables_list = [self.variable_index]
        self.evaluation_function = "identity"
        self.argument_variables = [self.variable_index]
        self.argument_constants = []
        
        #setting all the backend specific stuff
        if(backend is None):
            self.add = sum
            def t(args):
                ret = 1
                for a in args:
                    ret*=a
                return ret
            self.product = t
            self.divide = lambda x,y: x/y

    def give_name(self,name):
        self.name = name
        self.named = True

    @staticmethod
    def __add(a,b,minus=False):
        ret = variable()
        ret.evaluation_function = "add"
        ret.required_variables_list = []
        ret.argument_variables = []
        ret.argument_constants = []
        if(type(a)!=variable and type(b)!=variable):
            raise TypeError("both arguments are not not of type variable")
        if(type(a)==variable):
            ret.required_variables_list += a.required_variables_list
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
            if(b.evaluation_function == "add"):
                ret.argument_variables += b.argument_variables
                if(minus):
                    for c in b.argument_constants:
                        ret.argument_variables.append(-c)
                else:
                    ret.argument_constants += b.argument_constants
            else:
                ret.argument_variables.append(b.variable_index)
                ret.argument_constants.append(not minus)
        else:
            ret.argument_variables.append(None)
            ret.argument_constants.append(-a if minus else a)

        return ret

    def __add__(self,a):
        return variable.__add(self,a)

    def __sub__(self,a):
        return variable.__add(self,a,minus=True)
    
    #TODO: implement system for product variable to hold multiple arguments like add.
    def __mul__(self,a):
        ret = variable()
        if(type(a) != type(self)):
            ret.required_variables_list = self.required_variables_list
            ret.evaluation_function = "product"
            ret.argument_variables = [self.variable_index]
        else:
            ret.required_variables_list = self.required_variables_list + a.required_variables_list
            ret.evaluation_function = "product"
            ret.argument_variables = [self.variable_index,a.variable_index]

        return ret

    def __truediv__(self,a):
        ret = variable()
        if(type(a) != type(self)):
            return self*(1/a) #strongly reconsider this.
        else:
            ret.required_variables_list = self.required_variables_list + a.required_variables_list
            ret.evaluation_function = "divide"
            ret.argument_variables = [self.variable_index,a.variable_index]

        return ret

    #TODO: figure out how to add a to self

    def __rshift__(self,a):
        return assigned_variable(self,a)
        
    def evaluate(self,*args):
        if(type(args[0]) == list or type(args[0]) == tuple):
            if(len(args)>1):
                warnings.warn("the first argument to evaluate was a list, ignoring other arguments")
            args = args[0]
        #TODO: check if all variables were assigned.
        #TODO: lots and lots of optimization.
        if(self.evaluation_function == "identity"):
            for a in args:
                if(a.variable_index == self.variable_index):
                    return a.value
            raise Error(f"the variable {self} was not assigned")
        elif(self.evaluation_function == "add"):
            arglist = []
            for i in range(len(self.argument_variables)):
                if(self.argument_variables[i] is None):
                    arglist.append(self.argument_constants[i])
                else:
                    E = 1 if self.argument_constants[i] else -1
                    E *= variable_dictionary[self.argument_variables[i]].evaluate(args)
                    arglist.append(E)
            return(self.add(arglist))
        elif(self.evaluation_function == "product"):
            arglist = []
            for i in range(len(self.argument_variables)):
                if(self.argument_variables[i] is None):
                    arglist.append(self.argument_constants[i])
                else:
                    E = variable_dictionary[self.argument_variables[i]].evaluate(args)
                    arglist.append(E)
            return(self.product(arglist))
        elif(self.evaluation_function == "divide"):
            arg1 = variable_dictionary[self.argument_variables[0]].evaluate(args)
            arg2 = variable_dictionary[self.argument_variables[1]].evaluate(args)
            return self.divide(arg1, arg2)

    @staticmethod
    def __str(self,brackets=True):
        if(self.named or self.evaluation_function == "identity"):
            return self.name
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
                    s = variable.__str(self.argument_constants[i])
                    if(s[0]!="-" or s[0]!="+"):
                        ret += "+"
                    ret += s
            ret += ")" if brackets else ""
            return ret

        elif(self.evaluation_function == "product"):
            ret = "(" if brackets else ""
            for index in self.argument_variables:
                ret += variable.__str(variable_dictionary[index])
                ret += "×"
            for c in self.argument_constants:
                ret += variable.__str(c)
                ret += "×"
            if(ret[-1] == '×'):
                ret = ret[:-1]
            ret += ")" if brackets else ""
            return ret

        elif(self.evaluation_function == "divide"):
            ret = "(" if brackets else ""
            if(self.argument_variables[0] is not None):
                ret += variable.__str(variable_dictionary[self.argument_variables[0]])
                ret += "/"
                if(len(self.argument_variables) > 1):
                    ret += variable.__str(variable_dictionary[self.argument_variables[1]])
                elif(len(self.argument_constants)>0):
                    ret += variable.__str(self.argument_constants[0])
                else:
                    raise(ValueError("malformed variable object, this should not happen unless you manipulated the object using non-official means."))
            else:
                if(len(self.argument_constants)==0):
                    raise(ValueError("malformed variable object, this should not happen unelss you manipulated the object using non-official means."))
                else:
                    ret += variable.__str(argument_constants[0])
                    ret += "/"
                    ret += variable.__str(variable_dictionary[self.argument_variables[1]])
            ret += ")" if brackets else  ""
            return ret
        return "error"

    def __str__(self):
        return variable.__str(self,False)

class assigned_variable:
    def __init__(self,variable,value):
        if(type(value) == variable):
            raise TypeError("a variable cannot be assigned a variable as a value, I don't know if I will ever support something like this.")
        self.variable_index = variable.variable_index
        self.value = value

if(__name__ == "__main__"):
    a = variable("a")
    b = variable("b")
    c = a+b
    d = a-b
    e = c*d
    f = c/d
    g = d - e + f
    values = [a>>1,b>>3]
    print(a,a.evaluate(values))
    print(b,b.evaluate(values))
    print(c,c.evaluate(values))
    print(d,d.evaluate(values))
    print(e,e.evaluate(values))
    print(f,f.evaluate(values))
    print(g,g.evaluate(values))
