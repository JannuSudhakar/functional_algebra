global_variable_index = 0

list_of_evaluation_functions = [
"identity",
"add",
"product",
"subtract",
"divide",
]

variable_dictionary = {}

class variable:
    def __init__(self,name = None):
        global global_variable_index
        self.variable_index = global_variable_index
        variable_dictionary[self.variable_index] = self
        self.name = name if name is not None else f"variable{self.variable_index}"
        self.named = name is not None
        global_variable_index += 1
        self.required_variables_list = [self.variable_index]
        self.evaluation_function = "identity"
        self.evaluation_function_argument_variables = [self.variable_index]
        self.evaluation_function_argument_constants = []

    def give_name(self,name):
        self.name = name
        self.named = True

    @staticmethod
    def __add(a,b,minus=False):
        ret = variable()
        ret.evaluation_function = "add"
        ret.required_variables_list = []
        ret.evaluation_function_argument_variables = []
        ret.evaluation_function_argument_constants = []
        if(type(a)!=variable and type(b)!=variable):
            raise TypeError("both arguments are not not of type variable")
        if(type(a)==variable):
            ret.required_variables_list += a.required_variables_list
            if(a.evaluation_function=="add"):
                ret.evaluation_function_argument_variables += a.evaluation_function_argument_variables
                ret.evaluation_function_argument_constants += a.evaluation_function_argument_constants
            else:
                ret.evaluation_function_argument_variables.append(a.variable_index)
                ret.evaluation_function_argument_constants.append(True)
        else:
            ret.evaluation_function_argument_variables.append(None)
            ret.evaluation_function_argument_constants.append(a)

        if(type(b)==variable):
            if(b.evaluation_function == "add"):
                ret.evaluation_function_argument_variables += b.evaluation_function_argument_variables
                if(minus):
                    for c in b.evaluation_function_argument_constants:
                        ret.evaluation_function_argument_variables.append(-c)
                else:
                    ret.evaluation_function_argument_constants += b.evaluation_function_argument_constants
            else:
                ret.evaluation_function_argument_variables.append(b.variable_index)
                ret.evaluation_function_argument_constants.append(not minus)
        else:
            ret.evaluation_function_argument_variables.append(None)
            ret.evaluation_function_argument_constants.append(-a if minus else a)

        return ret

    def __add__(self,a):
        return variable.__add(self,a)

    def __sub__(self,a):
        # ret = variable()
        # if(type(a) != type(self)):
        #     return self + (-a)
        # else:
        #     ret.required_variables_list = self.required_variables_list + a.required_variables_list
        #     ret.evaluation_function = "subtract"
        #     ret.evaluation_function_argument_variables = [self.variable_index,a.variable_index]
        #
        # return ret
        return variable.__add(self,a,minus=True)

    def __mul__(self,a):
        ret = variable()
        if(type(a) != type(self)):
            ret.required_variables_list = self.required_variables_list
            ret.evaluation_function = "product"
            ret.evaluation_function_argument_variables = [self.variable_index]
        else:
            ret.required_variables_list = self.required_variables_list + a.required_variables_list
            ret.evaluation_function = "product"
            ret.evaluation_function_argument_variables = [self.variable_index,a.variable_index]

        return ret

    def __truediv__(self,a):
        ret = variable()
        if(type(a) != type(self)):
            return self*(1/a)
        else:
            ret.required_variables_list = self.required_variables_list + a.required_variables_list
            ret.evaluation_function = "divide"
            ret.evaluation_function_argument_variables = [self.variable_index,a.variable_index]

        return ret

    #TODO: figure out how to add a to self

    def __or__(self,a):
        return assigned_variable(self,a)

    @staticmethod
    def __str(self,brackets=True):
        if(self.named or self.evaluation_function == "identity"):
            return self.name
        elif(self.evaluation_function == "add"):
            ret = "(" if brackets else ""
            for i in range(len(self.evaluation_function_argument_variables)):
                if(self.evaluation_function_argument_variables[i] is not None):
                    if(self.evaluation_function_argument_constants[i]):
                        ret += "" if i==0 else "+"
                    else:
                        ret += "-"
                    ret += variable.__str(variable_dictionary[self.evaluation_function_argument_variables[i]])
                else:
                    s = variable.__str(self.evaluation_function_argument_constants[i])
                    if(s[0]!="-" or s[0]!="+"):
                        ret += "+"
                    ret += s
            ret += ")" if brackets else ""
            return ret

        elif(self.evaluation_function == "product"):
            ret = "(" if brackets else ""
            for index in self.evaluation_function_argument_variables:
                ret += variable.__str(variable_dictionary[index])
                ret += "×"
            for c in self.evaluation_function_argument_constants:
                ret += variable.__str(c)
                ret += "×"
            if(ret[-1] == '×'):
                ret = ret[:-1]
            ret += ")" if brackets else ""
            return ret

        elif(self.evaluation_function == "divide"):
            ret = "(" if brackets else ""
            if(self.evaluation_function_argument_variables[0] is not None):
                ret += variable.__str(variable_dictionary[self.evaluation_function_argument_variables[0]])
                ret += "/"
                if(len(self.evaluation_function_argument_variables) > 1):
                    ret += variable.__str(variable_dictionary[self.evaluation_function_argument_variables[1]])
                elif(len(self.evaluation_function_argument_constants)>0):
                    ret += variable.__str(self.evaluation_function_argument_constants[0])
                else:
                    raise(ValueError("malformed variable object, this should not happen unless you manipulated the object using non-official means."))
            else:
                if(len(self.evaluation_function_argument_constants)==0):
                    raise(ValueError("malformed variable object, this should not happen unelss you manipulated the object using non-official means."))
                else:
                    ret += variable.__str(evaluation_function_argument_constants[0])
                    ret += "/"
                    ret += variable.__str(variable_dictionary[self.evaluation_function_argument_variables[1]])
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
    print(a)
    print(b)
    print(c)
    print(d)
    print(e)
    print(f)
    print(g)
