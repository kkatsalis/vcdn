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
V=2
global M
M=1
global Object  
Object=2
global Row 
Row=2
global Col
Col=2

# Defines request rate r[i][o][row][m]
r=[[[[0 for m in range(M)]for row in range(Row)] for o in range(Object)] for i in range(V)] 
# Defines request rate from others r[i][n][o]
rt=[[[0 for o in range(Object)] for n in range(V)] for i in range(V)] 
# Defines benefit b[i][o][row][col][m]   
b=[[[[[[0 for m in range(M)] for col in range(Col)]for rowD in range(Row)] for rowS in range(Row)] for o in range(Object)] for i in range(V)]    
# Defines benefit psi[i][n][o][row][col]   
psi=[[[[0 for col in range(Col)] for row in range(Row)] for n in range(V)]for i in range(V)] 
# Defines benefit h[i][n][o][row][col]   
h=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)] for n in range(V)]for i in range(V)] 
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
# Defines constraintC_bound[i][o]
constraintC_bound=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)]for n in range(V)]for i in range(V)]
# Defines constraintC_coeff[i][o]
constraintC_coeff=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Object)]for n in range(V)]for i in range(V)]

# Defines benefit_coefficients dictionary
b1_coeff={}
b2_coeff={}
b3_coeff={}
# Defines c1_coefficients dictionary
c1_coeff={}
c2_coeff={}
c3_coeff={}


def initialize_tables():
    # Defines r[i][o][row][m]: rate of requests

#     Operator 0
    r[0][0][0][0]=10
    r[0][0][1][0]=10
    r[0][1][0][0]=30
    r[0][1][1][0]=30

#     Operator 1
#     r[0][0][0][1]=2
#     r[0][0][1][1]=2
#     r[0][1][0][1]=40
#     r[0][1][1][1]=40
    
    
#     rt[i][n][o]
    rt[0][1][0]=10
    rt[0][1][1]=20
   
    rt[1][0][0]=330
    rt[1][0][1]=440
    
#     rt[0][2][0]=1
#     rt[0][2][1]=2
#     rt[1][2][0]=1
#     rt[1][2][1]=2
#     
#     rt[2][0][0]=5
#     rt[2][0][1]=4
#     rt[2][1][0]=3
#     rt[2][1][1]=8
    
    # b[i][o][rowS][rowD][col][m] - row 0 gain
    # Mobile operator 0  
#      obj[0],rowS=0, m=0
    b[0][0][0][0][0][0]=4
    b[0][0][0][0][1][0]=4
    b[0][0][0][1][0][0]=2
    b[0][0][0][1][1][0]=2
#      rowS=1
    b[0][0][1][0][0][0]=2
    b[0][0][1][0][1][0]=2
    b[0][0][1][1][0][0]=1
    b[0][0][1][1][1][0]=1
    
#      obj=1, rowS=0
    b[0][1][0][0][0][0]=4
    b[0][1][0][0][1][0]=4
    b[0][1][0][1][0][0]=2
    b[0][1][0][1][1][0]=2
#      obj=1, rowS=1
    b[0][1][1][0][0][0]=2
    b[0][1][1][0][1][0]=2
    b[0][1][1][1][0][0]=1
    b[0][1][1][1][1][0]=1
    
    # Mobile operator 1    
#     #obj[0],rowS=0, m=1
#     b[0][0][0][0][0][1]=8
#     b[0][0][0][0][1][1]=6
#     b[0][0][0][1][0][1]=4
#     b[0][0][0][1][1][1]=2
# #      obj[0],rowS=1, m=1
#     b[0][0][1][0][0][1]=10
#     b[0][0][1][0][1][1]=8
#     b[0][0][1][1][0][1]=6
#     b[0][0][1][1][1][1]=4
#     
# #      obj[1],rowS=0, m=1
#     b[0][1][0][0][0][1]=5
#     b[0][1][0][0][1][1]=2
#     b[0][1][0][1][0][1]=10
#     b[0][1][0][1][1][1]=20
# #      obj[1],rowS=1, m=1
#     b[0][1][1][0][0][1]=5
#     b[0][1][1][0][1][1]=2
#     b[0][1][1][1][0][1]=20
#     b[0][1][1][1][1][1]=10
    # s[o]:  Object size
    s[0]=5
    s[1]=10
    
    
#     psi[i][n][row][col]
#   i=0 
    psi[0][1][0][0]=3
    psi[0][1][0][1]=3
    psi[0][1][1][0]=3
    psi[0][1][1][1]=3
    

    # i=1
    psi[1][0][0][0]=5
    psi[1][0][0][1]=5
    psi[1][0][1][0]=5
    psi[1][0][1][1]=5
    
#     psi[0][2][0][0]=5
#     psi[0][2][0][1]=1
#     psi[0][2][1][0]=10
#     psi[0][2][1][1]=4
#     psi[1][2][0][0]=4
#     psi[1][2][0][1]=2
#     psi[1][2][1][0]=4
#     psi[1][2][1][1]=2
#     # i=2
#     psi[2][0][0][0]=20
#     psi[2][0][0][1]=10
#     psi[2][0][1][0]=30
#     psi[2][0][1][1]=5
#     
#     psi[2][1][0][0]=40
#     psi[2][1][0][1]=20
#     psi[2][1][1][0]=45
#     psi[2][1][1][1]=15
    
    
#   h[i][n][o][row][col]
    #  i=0,o=0   
    h[0][1][0][0][0]=3   
    h[0][1][0][0][1]=3  
    h[0][1][0][1][0]=3  
    h[0][1][0][1][1]=3 
    
#     h[0][2][0][0][0]=30   
#     h[0][2][0][0][1]=10
#     h[0][2][0][1][0]=32   
#     h[0][2][0][1][1]=11   
       
    #  i=0,o=1   
    h[0][1][1][0][0]=4   
    h[0][1][1][0][1]=4 
    h[0][1][1][1][0]=4   
    h[0][1][1][1][1]=4  
      
#     h[0][2][1][0][0]=40   
#     h[0][2][1][0][1]=1   
#     h[0][2][1][1][0]=22   
#     h[0][2][1][1][1]=13  
    
    #  i=1,o=0   
    h[1][0][0][0][0]=5   
    h[1][0][0][0][1]=5
    h[1][0][0][1][0]=5 
    h[1][0][0][1][1]=5 
      
#     h[1][2][0][0][0]=10   
#     h[1][2][0][0][1]=2 
#     h[1][2][0][1][0]=3   
#     h[1][2][0][1][1]=7   
    #  i=1,o=1   
    h[1][0][1][0][0]=7   
    h[1][0][1][0][1]=7
    h[1][0][1][1][0]=7   
    h[1][0][1][1][1]=7
       
#     h[1][2][1][0][0]=35   
#     h[1][2][1][0][1]=7   
#     h[1][2][1][1][0]=5   
#     h[1][2][1][1][1]=71   
    
    #  i=2,o=0   
    h[1][0][0][0][0]=6   
    h[1][0][0][0][1]=6
    h[1][0][0][1][0]=6  
    h[1][0][0][1][1]=6 
       
#     h[1][2][0][0][0]=10   
#     h[1][2][0][0][1]=2
#     h[1][2][0][1][0]=14   
#     h[1][2][0][1][1]=27   
       
    #  i=2,o=1   
#     h[2][0][1][0][0]=5   
#     h[2][0][1][0][1]=1 
#     h[2][0][1][1][0]=34   
#     h[2][0][1][1][1]=17 
#       
#     h[2][1][1][0][0]=3   
#     h[2][1][1][0][1]=2   
#     h[2][1][1][1][0]=23   
#     h[2][1][1][1][1]=2   
     
     
     
    # c[i][row][col] Placement COST
    c[0][0][0]=2
    c[0][0][1]=1
    c[0][1][0]=4
    c[0][1][1]=2
    
    c[1][0][0]=2
    c[1][0][1]=1
    c[1][1][0]=4
    c[1][1][1]=2
    
#     c[2][0][0]=2
#     c[2][0][1]=1
#     c[2][1][0]=4
#     c[2][1][1]=2
#     constraintA_bound[i][row][col]
    constraintA_bound[0][0][0]=10
    constraintA_bound[0][0][1]=20
    constraintA_bound[0][1][0]=10
    constraintA_bound[0][1][1]=20

    constraintA_bound[1][0][0]=40
    constraintA_bound[1][0][1]=20
    constraintA_bound[1][1][0]=40
    constraintA_bound[1][1][1]=20

#     constraintA_bound[2][0][0]=30
#     constraintA_bound[2][0][1]=10
#     constraintA_bound[2][1][0]=30
#     constraintA_bound[2][1][1]=20    
    
def build_model():
    """ XNAMES: x_names[i][o][row][col]"""
    index=0
    for i in range(V):
        for o in range(Object): 
            for row in range(Row):
                for col in range(Col):
                    x_names[i][o][row][col]="x["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1
#     print("X names")              
#     pprint.pprint(x_names)                
      
    """ w_names: w_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(Object): 
                for row in range(Row):
                    for col in range(Col):
                        w_names[i][n][o][row][col]="w["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1
#     print("W names")              
#     pprint.pprint(w_names)
     
    """YNames: y_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(Object): 
                for row in range(Row):
                    for col in range(Col):
                        y_names[i][n][o][row][col]="y["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1
#     print("Y names")              
#     pprint.pprint(y_names)                
    
    """   Benefits  """
    build_b1_benefit()
    build_b2_benefit()
    build_b3_benefit()

    """   Costs  """
    build_c1_cost()
    build_c2_cost()
    build_c3_cost()
#     
    """ Constraints   """   
    build_constraintA()       
    build_constraintB()       
    build_constraintC()
   


def build_b1_benefit():
    """ B1:  Benefit   """ 
    coef=0
    for i in range(V):
        for o in range(Object): 
            for rowD in range(Row):
                for col in range(Col):
                    coef=0
                    for rowS in range(Row):
                        for m in range(M):
                            req=r[i][o][rowS][m]
                            gain=b[i][o][rowS][rowD][col][m]
                            coef=coef+req*gain
                            x_key=x_names[i][o][rowD][col]
                            b1_coeff[x_key]=str(coef)
                            for n in range(V):
                                if n!=i:
                                    w_key=w_names[i][n][o][rowD][col]
                                    y_key=y_names[i][n][o][rowD][col]
                                    b1_coeff[w_key]=str(coef)
                                    b1_coeff[y_key]=str(coef)
                                    
    print("--- B1 Gain coefficients ---")              
    pprint.pprint(b1_coeff)


def build_b2_benefit():
   
    for i in range(V):
        for o in range(Object):
            size=s[o] 
            for row in range(Row):
                for col in range(Col):
                    for n in range(V):
                        if n!=i:
                            coef=0
                            benefit=psi[i][n][row][col]
                            coef=size*benefit
                            w_key=w_names[n][i][o][row][col]    
                            b2_coeff[w_key]=str(coef)    
   
    print("--- B2 Gain coefficients ---")              
    pprint.pprint(b2_coeff)

def build_b3_benefit():
   
    for i in range(V):
        for o in range(Object):
            for row in range(Row):
                for col in range(Col):
                    for n in range(V):
                        if n!=i:
                            rate=rt[n][i][o]
                            coef=0
                            benefit=h[i][n][o][row][col]
                            coef=rate*benefit
                            y_key=y_names[n][i][o][row][col]    
                            b3_coeff[y_key]=str(coef)    
    
    print("--- B3 Gain coefficients ---")              
    pprint.pprint(b3_coeff)           

   
def build_c1_cost():
    """ C1:  Cost of placement in owned storage  """
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
    
    print("----- C1 Cost coefficients----")
    pprint.pprint(c1_coeff)
    
    

def build_c2_cost():
    """Cost of placing content in CDN n """
    for i in range(V):
        for o in range(Object):
            size=s[o] 
            for row in range(Row):
                for col in range(Col):
                    for n in range(V):
                        if n!=i:
                            coef=0
                            cost=psi[n][i][row][col]
                            coef=size*cost
                            w_key=w_names[i][n][o][row][col]    
                            c2_coeff[w_key]=str(coef)   
                            
    print("----- C2 Cost coefficients----")
    pprint.pprint(c2_coeff)
                             
def build_c3_cost():
    """Cost of asking content from CDN n """
    for i in range(V):
        for o in range(Object):
            for row in range(Row):
                for col in range(Col):
                    for n in range(V):
                        if n!=i:
                            rate=rt[i][n][o]
                            coef=0
                            cost=h[n][i][o][row][col]
                            coef=rate*cost
                            y_key=y_names[i][n][o][row][col]    
                            c3_coeff[y_key]=str(coef)      

    print("----- C3 Cost coefficients----")
    pprint.pprint(c3_coeff)
    
        
def build_constraintA():       
    """
        Constraint A: Capacity constraints
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

#     pprint.pprint(constraintA_coeff[i][row][col])

#     print("--- constraintA_Bounds --- ")
#     pprint.pprint(constraintA_bound)
#                                          
#     print("--- constraintA_coeff --- ")
#     pprint.pprint(constraintA_coeff)
     
    
   
def build_constraintB():    
    """ 
     Constraint B:  Store only in one place constraint
         
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
    
#     print("--- constraintB_Bounds --- ")
#     pprint.pprint(constraintB_bound)
#     
#     print("--- constraintB_coeff --- ")
#     pprint.pprint(constraintB_coeff)   
      
def build_constraintC():
    """ Constraint C: In order to ask for an object from CDN i he needs to have it"""
    for i in range(V):
            for o in range(Object):
                for row in range(Row):
                    for col in range(Col):
                        for n in range(V):
                            if n!=i:
                                constraintC_coeff[i][n][o][row][col]={}
                                y_key=y_names[i][n][o][row][col]
                                (constraintC_coeff[i][n][o][row][col])[y_key]=1      
                                x_key=x_names[n][o][row][col]
                                (constraintC_coeff[i][n][o][row][col])[x_key]=-1
  
#     print("--- constraintC_Bounds --- ")
#     pprint.pprint(constraintC_bound)
#     
#     print("--- constraintC_coeff --- ")
#     pprint.pprint(constraintC_coeff)   



my_obj=[]
my_colnames=[]
my_ub = []
my_lb = []
my_ctype=""
my_rownames=[]
my_rhs=[]
my_rows=[]
my_sense=""

def build_cplex_model():
    temp_obj_coeff={}
    
    """ Objective function """
    for b1_key,b1_value in b1_coeff.items():
        if b1_key in temp_obj_coeff:
            current_value=int(temp_obj_coeff[b1_key])
            temp_obj_coeff[b1_key]=current_value+int(b1_value)
        else:
            temp_obj_coeff[b1_key]=int(b1_value)

#     for b2_key,b2_value in b2_coeff.items():
#         if b2_key in temp_obj_coeff:
#             current_value=int(temp_obj_coeff[b2_key])
#             temp_obj_coeff[b2_key]=current_value+int(b2_value)
#         else:
#             temp_obj_coeff[b1_key]=int(b2_value)
#             
#     for b3_key,b3_value in b3_coeff.items():
#         if b3_key in temp_obj_coeff:
#             current_value=int(temp_obj_coeff[b3_key])
#             temp_obj_coeff[b3_key]=current_value+int(b3_value)
#         else:
#             temp_obj_coeff[b3_key]=int(b3_value)      
#             
#     for c1_key,c1_value in c1_coeff.items():
#         if c1_key in temp_obj_coeff:
#             current_value=int(temp_obj_coeff[c1_key])
#             temp_obj_coeff[c1_key]=current_value-int(c1_value)
#         else:
#             temp_obj_coeff[c1_key]=-1*int(c1_value) 
#     
#     for c2_key,c2_value in c2_coeff.items():
#         if c2_key in temp_obj_coeff:
#             current_value=int(temp_obj_coeff[c2_key])
#             temp_obj_coeff[c2_key]=current_value-int(c2_value)
#         else:
#             temp_obj_coeff[c2_key]=-1*int(c2_value)
#     
#     for c3_key,c3_value in c3_coeff.items():
#         if c3_key in temp_obj_coeff:
#             current_value=int(temp_obj_coeff[c3_key])
#             temp_obj_coeff[c3_key]=current_value-int(c3_value)
#         else:
#             temp_obj_coeff[c3_key]=-1*int(c3_value)            
    
    """ Prepare the final list"""    
    for key,value in temp_obj_coeff.items():    
        my_obj.append(int(value))  
        my_colnames.append(key)
                 
    print("my_obj:")                
    pprint.pprint(my_obj)                
    print("my_colnames:")                
    pprint.pprint(my_colnames)                
    
    """Variables Bounds """
    global my_ctype
    my_ctype=""
    index=0    
    while index <len(my_colnames):
        my_lb.append(0.0)
        my_ub.append(1.0)
        my_ctype = my_ctype+"I"
        index=index+1
    
#     print("my_lb")
#     pprint.pprint(my_lb)
#     print("my_temp_ub")
#     pprint.pprint(my_temp_ub)
#     print("my_ctype")
#     pprint.pprint(my_ctype)

    """ Constraint A set"""
    for i in range(V):
        for row in range(Row):
            for col in range(Col):
                constrainta_row=[]
                lista_coeff_key=[]
                lista_coeff_value=[]
                my_rhs.append(constraintA_bound[i][row][col])
                identifier="rowA["+str(i)+"]["+str(row)+"]["+str(col)+"]"
                my_rownames.append(identifier)
                    
                for key,value in constraintA_coeff[i][row][col].items():
                    lista_coeff_key.append(key)
                    lista_coeff_value.append(value)    
                constrainta_row.append(lista_coeff_key)
                constrainta_row.append(lista_coeff_value)
                my_rows.append(constrainta_row)
                

    """ Constraint B set"""
    for i in range(V):
        for o in range(Object):
            identifier="rowB["+str(i)+"]["+str(o)+"]"
            my_rownames.append(identifier)
            my_rhs.append(constraintB_bound[i][o])
            constraintb_row=[]
            listb_coeff_key=[]
            listb_coeff_value=[]
            for key,value in constraintB_coeff[i][o].items():
                listb_coeff_key.append(key)
                listb_coeff_value.append(value)    
            constraintb_row.append(listb_coeff_key)
            constraintb_row.append(listb_coeff_value)
            my_rows.append(constraintb_row)

#     print("My row names with B")
#     pprint.pprint(my_rownames)
#     print("My constraints rows with B")
#     pprint.pprint(my_rows)
#     print("My rhs with B")
#     pprint.pprint(my_rhs)

    print("Build C")
    """ Constraint C set"""
    for i in range(V):
        for o in range(Object):
            for row in range(Row):
                for col in range(Col):
                    for n in range(V):
                        if n!=i:
                            constraintc_row=[]
                            listc_coeff_key=[]
                            listc_coeff_value=[]
                            my_rhs.append(constraintC_bound[i][n][o][row][col])
                            identifier="rowC["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                            my_rownames.append(identifier)
                            
                            for key,value in constraintC_coeff[i][n][o][row][col].items():
                                listc_coeff_key.append(key)
                                listc_coeff_value.append(value)    
                            constraintc_row.append(listc_coeff_key)
                            constraintc_row.append(listc_coeff_value)
                            my_rows.append(constraintc_row)
                            
                            
    print("My row names with C")
    pprint.pprint(my_rownames)
    print("My constraints rows with B")
    pprint.pprint(my_rows)
    print("My rhs with C")
    pprint.pprint(my_rhs)
                            
    """ My sense """
    global my_sense
    my_sense=""
    index=0
    while index <len(my_rows):
        my_sense=my_sense+"L"
        index=index+1

# my_obj = [1.0, 2.0, 3.0, 1.0]
# my_colnames = ["x1", "x2", "x3", "x4"]
# my_ub = [40.0, cplex.infinity, cplex.infinity, 3.0]
# my_lb = [0.0, 0.0, 0.0, 2.0]
# my_ctype = "CCCI"  
# my_rhs = [20.0, 30.0, 0.0]
# my_rownames = ["r1", "r2", "r3"]
# my_sense = "LLE"

def populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
                       names=my_colnames)

    prob.linear_constraints.add(lin_expr=my_rows, senses=my_sense,
                                rhs=my_rhs, names=my_rownames)
    
# def populatebyrow(prob):
#     prob.objective.set_sense(prob.objective.sense.maximize)
# 
#     prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
#                        names=my_colnames)
# 
#     rows = [[["x1", "x2", "x3", "x4"], [-1.0, 1.0, 1.0, 10.0]],
#             [["x1", "x2", "x3"], [1.0, -3.0, 1.0]],
#             [["x2", "x4"], [1.0, -3.5]]]
# 
#     prob.linear_constraints.add(lin_expr=rows, senses=my_sense,
#                                 rhs=my_rhs, names=my_rownames)

def solver():
    try:
        my_prob = cplex.Cplex()
        handle = populatebyrow(my_prob)
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
    build_cplex_model()
    solver()
    
    
    
    