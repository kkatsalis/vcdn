from __future__ import print_function

import sys
import pprint

import cplex
from cplex.exceptions import CplexError

#***** Example******
# V=1
# Object=10
# k=[[0 for i in range(V)] for o in range(Object)] 
# for i in range(Object):
#     for j in range(V): 
#         k[i][j]="k"+str(i)+","+str(j)
# pprint.pprint (k)

#  B1 coefficients
global V 
V=1
global M
M=2
global Object  
Object=2
global Row 
Row=2

global Col
Col=2

# Defines request rate r[i][o][row][m]
r=[[[[0 for m in range(M)]for row in range(Row)] for o in range(Object)] for i in range(V)] 
# Defines b[i][o][row][col][m]   
b=[[[[[0 for m in range(M)] for col in range(Col)] for row in range(Row)] for o in range(Object)] for i in range(V)]    
# Defines x[i][o][row][col]   
x=[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)] for i in range(V)] 
# x_names[i][o][row][col]
x_names=[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)] for i in range(V)] 
# Defines w[i][n][o][row][col]   
w=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)] for n in range(V)]for i in range(V)] 
# Defines w_names[i][n][o][row][col]
w_names=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)] for n in range(V)]for i in range(V)] 
# Defines y[i][n][o][row][col]   
y=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)] for n in range(V)]for i in range(V)] 
# y_names[i][n][o][row][col]
y_names=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)] for n in range(V)]for i in range(V)] 

# Defines c[i][row][col] unit cost    
c=[[[0 for col in range(Col)] for row in range(Row)] for i in range(V)] 
# Defines s[o] size of object o   
s=[0 for o in range(Object)]
# Defines constraintA_bound[i][row][col]
constraintA_bound=[[[0 for col in range(Col)] for row in range(Row)] for i in range(V)]
# Defines constraintA_coeff[i][row][col]
constraintA_coeff=[[[0 for col in range(Col)] for row in range(Row)] for i in range(V)]
# Defines constraintB_bound[i][o]
constraintB_bound=[[1 for o in range(Object)] for i in range(V)]
# Defines constraintB_coeff[i][o]
constraintB_coeff=[[0 for o in range(Object)] for i in range(V)]
# Defines b1_coefficients dictionary
b1_coeff={}
# Defines c1_coefficients dictionary
c1_coeff={}



def initialize_tables():
    # Defines r[i][o][row][m]: rate of requests
    r[0][0][0][0]=1
    r[0][0][0][1]=2
    r[0][0][1][0]=3
    r[0][0][1][1]=4
    
    r[0][1][0][0]=10
    r[0][1][0][1]=20
    r[0][1][1][0]=30
    r[0][1][1][1]=40
    
    # b[i][o][row][col][m] - row 0 gain
    b[0][0][0][0][0]=4
    b[0][0][0][0][1]=4
    b[0][0][0][1][0]=2
    b[0][0][0][1][1]=2
    
    b[0][1][0][0][0]=4
    b[0][1][0][0][1]=4
    b[0][1][0][1][0]=2
    b[0][1][0][1][1]=2
    
    # b[i][o][row][col][m] - row 1 gain
    b[0][0][1][0][0]=10
    b[0][0][1][0][1]=10
    b[0][0][1][1][0]=5
    b[0][0][1][1][1]=5
    
    b[0][1][1][0][0]=5
    b[0][1][1][0][1]=2
    b[0][1][1][1][0]=2
    b[0][1][1][1][1]=1
    
    # s[o]:  Object size
    s[0]=5
    s[1]=10
    
    # c[i][row][col] COST
    c[0][0][0]=2
    c[0][0][1]=1
    c[0][1][0]=4
    c[0][1][1]=2
    
#     constraintA_bound[i][row][col]
    constraintA_bound[0][0][0]=10
    constraintA_bound[0][0][1]=20
    constraintA_bound[0][1][0]=10
    constraintA_bound[0][1][1]=20

def build_model():
    """ XNAMES: x_names[i][o][row][col]"""
    index=0
    for i in range(V):
        for o in range(Object): 
            for row in range(Row):
                for col in range(Col):
                    x_names[i][o][row][col]="x["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1
    # print("X names")              
    # pprint.pprint(x_names)                
     
    """ WNames: w_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(Object): 
                for row in range(Row):
                    for col in range(Col):
                        w_names[i][n][o][row][col]="w["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1
    # print("W names")              
    # pprint.pprint(w_names)
    
    """YNames: y_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(Object): 
                for row in range(Row):
                    for col in range(Col):
                        y_names[i][n][o][row][col]="y["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1
    # print("Y names")              
    # pprint.pprint(y_names)                
    
    """ B1:  Benefit   """ 
    for i in range(V):
        for o in range(Object): 
            for row in range(Row):
                for col in range(Col):
                    coef=0
                    for m in range(M):
                        req=r[i][o][row][m]
                        gain=b[i][o][row][col][m]
                        coef=coef+(req*gain)
                    key=x_names[i][o][row][col]    
                    b1_coeff[key]=str(coef)    
    
#     print("--- B1 Gain coefficients ---")              
#     pprint.pprint(b1_coeff)
    
    """ C1:  Cost   """
    for i in range(V):
        for o in range(Object):
            size=s[o] 
            for row in range(Row):
                for col in range(Col):
                    coef=0
                    cost=c[i][row][col]
                    coef=size*cost
                    key=x_names[i][o][row][col]    
                    c1_coeff[key]=str(coef)    
    
#     print("----- C1 Cost coefficients----")
#     pprint.pprint(c1_coeff)
  
    """ Constraints   """   
    build_constraintA()       
    build_constraintB()       
    
    """ CPLEX Model """   
    cplex_model()
    
def build_constraintA():       
    """
        Capacity constraints
         constraintA_bound[i][row][col]
         constraintA_coeff[i][row][col]
    """
    for i in range(V):
        for row in range(Row):
            for col in range(Col):
                global constraintA_coeff
                constraintA_coeff[i][row][col]={}
    
                for o in range(Object):
                    xcoef=s[o]
                    key=x_names[i][o][row][col]
                    (constraintA_coeff[i][row][col])[key]=xcoef   
                    for n in range(V):
                        if n!=i:
                            xcoef=s[o]
                            key=w_names[n][i][o][row][col]
                            (constraintA_coeff[i][row][col])[key]=xcoef

            pprint.pprint(constraintA_coeff[i][row][col])

#     print("--- constraintA_Bounds --- ")
#     pprint.pprint(constraintA_bound)
#                                          
#     print("--- constraintA_coeff --- ")
#     pprint.pprint(constraintA_coeff)
     
    
   
def build_constraintB():    
    """ 
     Constraint B:  Store only in one place constraint
         w[i][n][o][row][col]
         y[i][n][o][row][col]
         constraintB_bound[i][o]
         constraintB_coeff[i][o]
    """
    for i in range(V):
        for o in range(Object):
            constraintB_coeff[i][o]={}
            for row in range(Row):
                for col in range(Col):
                    key=x_names[i][o][row][col]
                    (constraintB_coeff[i][o])[key]=1
                    for n in range(V):
                        if n!=i:
                            key=w_names[i][n][o][row][col]
                            (constraintB_coeff[i][o])[key]=1
                            key=y_names[i][n][o][row][col]
                            (constraintB_coeff[i][o])[key]=1                        
    
    print("--- constraintB_Bounds --- ")
    pprint.pprint(constraintB_bound)
    
    print("--- constraintB_coeff --- ")
    pprint.pprint(constraintB_coeff)   
      

my_temp_obj=[]
my_temp_colnames=[]
my_temp_ub = []
my_temp_lb = []
my_temp_ctype=""
my_temp_rownames=[]
my_temp_rhs=[]
my_temp_rows=[]
my_temp_sense=""

def cplex_model():
    
    """ Objective function """
    for b1_key,b1_value in b1_coeff.items():
#         print("b1_coeff-(key:value):"+b1_key+":"+b1_value)
        for c1_key,c1_value in c1_coeff.items():
            if b1_key==c1_key:
                my_temp_obj.append(int(b1_value)-int(c1_value))  
                my_temp_colnames.append(b1_key)
                
    print("my_temp_obj:")                
    pprint.pprint(my_temp_obj)                
    print("my_temp_colnames:")                
    pprint.pprint(my_temp_colnames)                
    
    """Variables Bounds """
    global my_temp_ctype
    my_temp_ctype=""
    index=0    
    while index <len(my_temp_colnames):
        my_temp_lb.append(0.0)
        my_temp_ub.append(1.0)
        my_temp_ctype = my_temp_ctype+"I"
        index=index+1
    
#     print("my_temp_lb")
#     pprint.pprint(my_temp_lb)
#     print("my_temp_ub")
#     pprint.pprint(my_temp_ub)
#     print("my_ctype")
#     pprint.pprint(my_temp_ctype)

    """ Constraint A set"""
    for i in range(V):
        for row in range(Row):
            for col in range(Col):
                constrainta_row=[]
                lista_coeff_key=[]
                lista_coeff_value=[]
                my_temp_rhs.append(constraintA_bound[i][row][col])
                identifier="rowA["+str(i)+"]["+str(row)+"]["+str(col)+"]"
                my_temp_rownames.append(identifier)
                    
                for key,value in constraintA_coeff[i][row][col].items():
                    lista_coeff_key.append(key)
                    lista_coeff_value.append(value)    
                constrainta_row.append(lista_coeff_key)
                constrainta_row.append(lista_coeff_value)
                my_temp_rows.append(constrainta_row)
                

    """ Constraint B set"""
    for i in range(V):
        for o in range(Object):
            identifier="rowB["+str(i)+"]["+str(o)+"]"
            my_temp_rownames.append(identifier)
            my_temp_rhs.append(constraintB_bound[i][o])
            constraintb_row=[]
            listb_coeff_key=[]
            listb_coeff_value=[]
            for key,value in constraintB_coeff[i][o].items():
                listb_coeff_key.append(key)
                listb_coeff_value.append(value)    
            constraintb_row.append(listb_coeff_key)
            constraintb_row.append(listb_coeff_value)
            my_temp_rows.append(constraintb_row)

    print("My row names with B")
    pprint.pprint(my_temp_rownames)
    print("My temp rows with B")
    pprint.pprint(my_temp_rows)
    print("My rhs with B")
    pprint.pprint(my_temp_rhs)

    global my_temp_sense
    my_temp_sense=""
    index=0
    while index <len(my_temp_rows):
        my_temp_sense=my_temp_sense+"L"
        index=index+1

my_obj = [1.0, 2.0, 3.0, 1.0]
my_colnames = ["x1", "x2", "x3", "x4"]
my_ub = [40.0, cplex.infinity, cplex.infinity, 3.0]
my_lb = [0.0, 0.0, 0.0, 2.0]
my_ctype = "CCCI"  
my_rhs = [20.0, 30.0, 0.0]
my_rownames = ["r1", "r2", "r3"]
my_sense = "LLE"

def temp_populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj=my_temp_obj, lb=my_temp_lb, ub=my_temp_ub, types=my_temp_ctype,
                       names=my_temp_colnames)

    prob.linear_constraints.add(lin_expr=my_temp_rows, senses=my_temp_sense,
                                rhs=my_temp_rhs, names=my_temp_rownames)
    
def populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
                       names=my_colnames)

    rows = [[["x1", "x2", "x3", "x4"], [-1.0, 1.0, 1.0, 10.0]],
            [["x1", "x2", "x3"], [1.0, -3.0, 1.0]],
            [["x2", "x4"], [1.0, -3.5]]]

    prob.linear_constraints.add(lin_expr=rows, senses=my_sense,
                                rhs=my_rhs, names=my_rownames)

def solver():
    try:
        my_prob = cplex.Cplex()
        handle = temp_populatebyrow(my_prob)
        my_prob.solve()
    except CplexError as exc:
        print(exc)
        return

    print()
    # solution.get_status() returns an integer code
    print("Solution status = ", my_prob.solution.get_status(), ":", end=' ')
    # the following line prints the corresponding string
    print(my_prob.solution.status[my_prob.solution.get_status()])
    print("Solution value  = ", my_prob.solution.get_objective_value())

    numcols = my_prob.variables.get_num()
    numrows = my_prob.linear_constraints.get_num()

    slack = my_prob.solution.get_linear_slacks()
    x = my_prob.solution.get_values()

    for j in range(numrows):
        print("Row %d:  Slack = %10f" % (j, slack[j]))
    for j in range(numcols):
        print("Column %d:  Value = %10f" % (j, x[j]))

if __name__ == "__main__":
    initialize_tables()
    build_model()
    pprint.pprint(my_temp_ctype)
    solver()
    
    
    
    