from __future__ import print_function

import sys
import pprint
import numpy as np
import cplex
from cplex.exceptions import CplexError
from sympy.physics.units.dimensions import current

# CDN providers
global V 
V=3
# Mobile operators
global M
M=1
# Objects
global Objects  
Objects=20
# Rows of the Grid
global Rows 
Rows=1
# Columns of the Grid
global Cols
Cols=3
global slots_number
slots_number=1

# Defines objects popularity weights pw[o]
pw=[0 for o in range(Objects)]
# Defines request rate r[i][o][row][m]. This is for the entire simulation
sim_r=[[[[[0 for m in range(M)]for row in range(Rows)] for o in range(Objects)] for i in range(V)] for s in range(slots_number)]
# Defines request rate from others r[i][n][o]
sim_rt=[[[[0 for o in range(Objects)] for n in range(V)] for i in range(V)] for s in range(slots_number)]
# Defines request rate r[i][o][row][m]. This is updated at each slot
r=[[[[0 for m in range(M)]for row in range(Rows)] for o in range(Objects)] for i in range(V)] 

# Defines benefit b[i][o][row][col][m]   
b=[[[[[[0 for m in range(M)] for col in range(Cols)]for rowD in range(Rows)] for rowS in range(Rows)] for o in range(Objects)] for i in range(V)]    
# Defines benefit psi[i][n][o][row][col]   
psi=[[[[0 for col in range(Cols)] for row in range(Rows)] for n in range(V)]for i in range(V)] 
# Defines benefit h[i][n][o][row][col]   
h=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for n in range(V)]for i in range(V)] 
# Defines solution_values[i][o][row][col]   
x=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for i in range(V)] 
# Defines solution_values[i][o][row][col] without sharing
x_ns=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for i in range(V)] 
# x_names[i][o][row][col]
x_names=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for i in range(V)] 
# x_ns_names[i][o][row][col]
x_ns_names=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for i in range(V)] 
# Defines w[i][n][o][row][col]   
w=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for n in range(V)]for i in range(V)] 
# Defines w_names[i][n][o][row][col]
w_names=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for n in range(V)]for i in range(V)] 
# Defines y[i][n][o][row][col]   
y=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for n in range(V)]for i in range(V)] 
# y_names[i][n][o][row][col]
y_names=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)] for n in range(V)]for i in range(V)] 
# Defines c[i][row][col] unit cost    
c=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)] 
# Defines s[o] size of object o   
s=[0 for o in range(Objects)]

# Defines benefit_coefficients dictionary for ns
b1_coeff_ns={}
c1_coeff_ns={}
# Defines benefit_coefficients dictionary
b1_coeff={}
b2_coeff={}
b3_coeff={}
# Defines c1_coefficients dictionary
c1_coeff={}
c2_coeff={}

# Defines constraintA_bound[i][row][col]
constraintA_bound=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
# Defines constraintA_coeff[i][row][col] when sharing
constraintA_coeff=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
# Defines constraintA_coeff[i][row][col] when not sharing
constraintA_coeff_ns=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
# Defines constraintB_bound[i][o]
constraintB_bound=[[1 for o in range(Objects)] for i in range(V)]
# Defines constraintB_coeff[i][o] when sharing
constraintB_coeff=[[0 for o in range(Objects)] for i in range(V)]
# Defines constraintB_coeff[i][o] when not sharing
constraintB_coeff_ns=[[0 for o in range(Objects)] for i in range(V)]
# Defines constraintC_bound[i][o]
constraintC_bound=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)]for n in range(V)]for i in range(V)]
# Defines constraintC_coeff[i][o]
constraintC_coeff=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(Objects)]for n in range(V)]for i in range(V)]


def initialize_objects_size():    
    """ s[o]:  Objects size"""
    for o in range(Objects):
        s[o]=5    


def initialize_benefit_b():    
    """ Benefit b[i][o][rowS][rowD][col][m]: """
    
    benefit_edge=10
    for i in range(V):
        for o in range(Objects):
            for rowS in range (Rows):
                for rowD in range (Rows):
                    for col in range (Cols):
                        for m in range (M):
                            distance=abs(rowD-rowS)*max(col,1)
                            if distance==0:
                                b[i][o][rowS][rowD][col][m]=benefit_edge
                            else:
                                benefit =(i+benefit_edge*0.9)/distance
                                b[i][o][rowS][rowD][col][m]=max(1,benefit)
    
    
def initialize_benefit_psi():    

    """ psi[i][n][row][col] """
    
    benefit_edge=10
    for i in range(V):
        for n in range(V):
            for row in range (Rows):
                for col in range (Cols):
                    if col==0:
                        psi[i][n][row][col]=benefit_edge
                    else:
                        benefit =benefit_edge*0.9/col
                        psi[i][n][row][col]=max(1,benefit)
                    
                        

def initialize_benefit_h():    
   
    """ h[i][n][o][row][col] """
    benefit_edge=1   
    for i in range(V):
        for n in range(V):
            for o in range(Objects):
                for row in range (Rows):
                    for col in range (Cols):
                        if col==0:
                            h[i][n][o][row][col]=benefit_edge
                        else:
                            benefit =benefit_edge*0.9/col
                            h[i][n][o][row][col]=max(1,benefit)
    
   
     
def initialize_placement_cost():     
     
    """ c[i][row][col] Placement COST """
    cost_edge=2
    for i in range(V):
        for row in range (Rows):
            for col in range (Cols):
                if col==0:
                    c[i][row][col]=cost_edge
                else:
                    cost =cost_edge*0.9/col
                    c[i][row][col]=max(1,cost)
               


def initialize_constraintA_bounds():

    """  constraintA_bound[i][row][col] """ 
    edge_sorage_limit=5
    for i in range(V):
        for row in range (Rows):
            for col in range (Cols):
                constraintA_bound[i][row][col]=edge_sorage_limit+edge_sorage_limit*col

                    
def initialize_simulator():
    build_variables_names()
    initialize_objects_size()
    initialize_benefit_b()
    initialize_benefit_psi()
    initialize_benefit_h()
    initialize_placement_cost()
    initialize_constraintA_bounds() 
    initialize_objects_weights()
    build_simulation_request_rates()

def build_simulation_request_rates():
    """" Requests for entire simulation """
    #   Requests to cdn i
    lamda_r=[[[0 for m in range(M)]for row in range(Rows)] for i in range(V)] 
    for i in range(V):
        for row in range(Rows):
            for m in range(M):
                lamda_r[i][row][m]=50+m
                
    for i in range(V):
        for row in range(Rows):
            for m in range(M):
#                 print("i-row-m:",i,row,m)
    
                requests_array=np.random.poisson(lamda_r[i][row][m],slots_number)
                sim_requests=requests_array.tolist()
#                 pprint.pprint(sim_requests)
                for slot in range(slots_number):
#                     print("***** slot :",slot)
                    for o in range(Objects):
                        sim_r[slot][i][o][row][m]=int(round(sim_requests[slot]*pw[o]))
#                         print("R :",sim_r[slot][i][o][row][m])
    
    #   Requests from cdn i to cdn n 
    for slot in range(slots_number):  
        for i in range(V):   
            for o in range(Objects):
                requests=0
                for row in range(Rows):
                    for m in range(M):
                        requests=requests+sim_r[slot][i][o][row][m]
                for n in range(V):
                    if n!=i:
                        sim_rt[slot][i][n][o]=requests/(V-1)   
                
                     
def initialize_objects_weights():    
    """ initializes objects' popularity weights according to zipf distribution"""
    zipf_parameter = 2.5
    zipf_object_popularity=np.random.zipf(zipf_parameter,Objects)
    popularity_list=zipf_object_popularity.tolist()
    popularity_list_sum=sum(popularity_list) 
    
    for i in range(Objects):
        pw[i]=popularity_list[i]/popularity_list_sum
    
    # pprint.pprint(popularity_list)
    # print("sum",popularity_list_sum)    
#     pprint.pprint(pw)

def build_variables_names():
    """ XNAMES: x_names[i][o][row][col]"""
    index=0
    for i in range(V):
        for o in range(Objects): 
            for row in range(Rows):
                for col in range(Cols):
                    x_names[i][o][row][col]="x["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1
#     print("X names")              
#     pprint.pprint(x_names)      

    """ X_ns_ NAMES: x_ns_names[i][o][row][col]"""
    index=0
    for i in range(V):
        for o in range(Objects): 
            for row in range(Rows):
                for col in range(Cols):
                    x_ns_names[i][o][row][col]="x_ns["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1          
      
    """ w_names: w_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(Objects): 
                for row in range(Rows):
                    for col in range(Cols):
                        w_names[i][n][o][row][col]="w["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1
#     print("W names")              
#     pprint.pprint(w_names)
     
    """YNames: y_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(Objects): 
                for row in range(Rows):
                    for col in range(Cols):
                        y_names[i][n][o][row][col]="y["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1
#     print("Y names")              
#     pprint.pprint(y_names)     


# A: Model when sharing ----------------


def build_model():
             
    """   Benefits  """
    build_b1_benefit()
    build_b2_benefit()
    build_b3_benefit()
    """   Costs  """
    build_c1_cost()   
    build_c2_cost()
#     
    """ Constraints   """  
    build_constraintA()       
    build_constraintB()       
    build_constraintC()  
    

def build_b1_benefit():
    """ B1:  Benefit   """ 
    coef=0
    for i in range(V):
        for o in range(Objects): 
            for rowD in range(Rows):
                for col in range(Cols):
                    coef=0
                    for rowS in range(Rows):
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
                                
#     print("--- B1 Gain coefficients ---")              
#     pprint.pprint(b1_coeff)


def build_b2_benefit():
   
    for i in range(V):
        for o in range(Objects):
            size=s[o] 
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            coef=0
                            benefit=psi[i][n][row][col]
                            coef=size*benefit
                            w_key=w_names[n][i][o][row][col]    
                            b2_coeff[w_key]=str(coef)    
                                                       
                            
   
#     print("--- B2 Gain coefficients ---")              
#     pprint.pprint(b2_coeff)

def build_b3_benefit():
#    r[i][o][row][m]
    for i in range(V):
        for o in range(Objects):
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            
                            for m in range(M):
                                rate=r[n][o][row][m]
                                coef=0
                                benefit=h[i][n][o][row][col]
                                coef=rate*benefit
                                y_key=y_names[n][i][o][row][col]    
                             
                                b3_coeff[y_key]=str(coef)    

    
#     print("--- B3 Gain coefficients ---")              
#     pprint.pprint(b3_coeff)           

def build_c1_cost():
    """ C1:  Cost of placement in owned storage  """
    for i in range(V):
        for o in range(Objects):
            size=s[o] 
            for row in range(Rows):
                for col in range(Cols):
                    coef=0
                    cost=c[i][row][col]
                    coef=size*cost
                    x_key=x_names[i][o][row][col]    
                    c1_coeff[x_key]=str(coef)    
                    for n in range(V):
                        if n!=i:
                        #   w parameters
                            coef=0
                            cost=psi[n][i][row][col]
                            coef=size*cost
                            w_key=w_names[i][n][o][row][col]    
                            c1_coeff[w_key]=str(coef)   
                        #   y parameters
                            coef=0
                            cost=h[n][i][o][row][col]
                            coef=cost
                            y_key=y_names[i][n][o][row][col]    
                            c1_coeff[y_key]=str(coef)  
                                        
#     print("----- C1 Cost coefficients----")
#     pprint.pprint(c1_coeff)
    



    

def build_c2_cost():
    """Cost of placing content from CDN n """
    for i in range(V):
        for o in range(Objects):
            size=s[o] 
            for row in range(Rows):
                for col in range(Cols):
                    cost=c[i][row][col]
                    for n in range(V):
                        if n!=i:
                            coef=0
                            coef=size*cost
                            w_key=w_names[n][i][o][row][col]    
                            c2_coeff[w_key]=str(coef)   
                            
#     print("----- C2 Cost coefficients----")
#     pprint.pprint(c2_coeff)
                                    
def build_constraintA():       
    """
        Constraint A: Capacity constraints
    """
    for i in range(V):
        for row in range(Rows):
            for col in range(Cols):
                global constraintA_coeff
                constraintA_coeff[i][row][col]={}
    
                for o in range(Objects):
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
        for o in range(Objects):
            constraintB_coeff[i][o]={}
            for row in range(Rows):
                for col in range(Cols):
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
            for o in range(Objects):
                for row in range(Rows):
                    for col in range(Cols):
                        for n in range(V):
                            if n!=i:
                                constraintC_coeff[i][n][o][row][col]={}
                                y_key=y_names[i][n][o][row][col]
                                (constraintC_coeff[i][n][o][row][col])[y_key]=1      
                                x_key=x_names[n][o][row][col]
                                (constraintC_coeff[i][n][o][row][col])[x_key]=-1
                                for j in range(V):
                                    if j!=i and j!=n:
                                        w_key=w_names[n][j][o][row][col]
                                        (constraintC_coeff[i][n][o][row][col])[w_key]=-1
                                
#     print("--- constraintC_Bounds --- ")
#     pprint.pprint(constraintC_bound)
#     
#     print("--- constraintC_coeff --- ")
#     pprint.pprint(constraintC_coeff)   







my_obj=[]
my_colnames=[]
my_ub = []
my_lb = []
my_rownames=[]
my_rhs=[]
my_rows=[]

global my_ctype
my_ctype=""
global my_sense
my_sense=""

def build_cplex_model():
    temp_obj_coeff={}
    
    """ B1: Objective function """
    for b1_key,b1_value in b1_coeff.items():
        if b1_key in temp_obj_coeff:
#             print ("B1 key: found")
            current_value=int(temp_obj_coeff[b1_key])
            temp_obj_coeff[b1_key]=current_value+float(b1_value)
        else:
#             print ("B1 key: new key entered"+b1_key)
            temp_obj_coeff[b1_key]=float(b1_value)
            
    """ B2: Objective function """        
    for b2_key,b2_value in b2_coeff.items():
        if b2_key in temp_obj_coeff:
            current_value=int(temp_obj_coeff[b2_key])
            temp_obj_coeff[b2_key]=current_value+float(b2_value)
        else:
            temp_obj_coeff[b2_key]=float(b2_value)
    
    """ B3: Objective function """         
    for b3_key,b3_value in b3_coeff.items():
        if b3_key in temp_obj_coeff:
            current_value=float(temp_obj_coeff[b3_key])
            temp_obj_coeff[b3_key]=current_value+float(b3_value)
        else:
            temp_obj_coeff[b3_key]=float(b3_value)      
#   
    """ C1: Cost function """          
    for c1_key,c1_value in c1_coeff.items():
        if c1_key in temp_obj_coeff:
            current_value=float(temp_obj_coeff[c1_key])
            new_value=current_value-float(c1_value)
            temp_obj_coeff[c1_key]=new_value
#             print ("C1 key: Found "+c1_key)
#             print ("Old Value: "+str(current_value) +" -- New value: "+str(new_value))
        else:
#             print ("Did not found the c1_key. New key entered:"+c1_key)
            value=-1*float(c1_value)
            temp_obj_coeff[c1_key]=value 
     
    """ C2: Cost function """                  
    for c2_key,c2_value in c2_coeff.items():
        if c2_key in temp_obj_coeff:
            current_value=float(temp_obj_coeff[c2_key])
            temp_obj_coeff[c2_key]=current_value-float(c2_value)
        else:
            temp_obj_coeff[c2_key]=-1*float(c2_value)

    """ Prepare the final list"""    
    for key,value in temp_obj_coeff.items():    
        my_obj.append(int(value))  
        my_colnames.append(key)
                 
#     print("my_obj:")                
#     pprint.pprint(my_obj)                
#     print("my_colnames:")                
#     pprint.pprint(my_colnames)                
    
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
        for row in range(Rows):
            for col in range(Cols):
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
        for o in range(Objects):
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

    """ Constraint C set"""
    for i in range(V):
        for o in range(Objects):
            for row in range(Rows):
                for col in range(Cols):
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
                            
                            
#     print("My row names with C")
#     pprint.pprint(my_rownames)
#     print("My constraints rows with B")
#     pprint.pprint(my_rows)
#     print("My rhs with C")
#     pprint.pprint(my_rhs)
                            
    """ My sense """
    global my_sense
    my_sense=""
    index=0
    while index <len(my_rows):
        my_sense=my_sense+"L"
        index=index+1



def populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
                       names=my_colnames)

    prob.linear_constraints.add(lin_expr=my_rows, senses=my_sense,
                                rhs=my_rhs, names=my_rownames)
    

def solver(sim_type,slot):
   
    
    try:
        my_prob = cplex.Cplex()
        if sim_type=="with_sharing":
            handle = populatebyrow(my_prob)
        elif sim_type=="with_no_sharing":
            handle = populatebyrow_ns(my_prob)
            
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
    
    file = open("results.txt","a")
    message="-slot-"+str(slot)+"-"+ sim_type+"-"+ str(my_prob.solution.get_objective_value())

    file.write(message)
    file.close() 
    
    numcols = my_prob.variables.get_num()
    numrows = my_prob.linear_constraints.get_num()
    slack = my_prob.solution.get_linear_slacks()
    solution_values = my_prob.solution.get_values()

#     for j in range(numrows):
#         print("Rows %d:  Slack = %10f" % (j, slack[j]))
    result_set={}
    for j in range(numcols):
        if solution_values[j]==1.0:
            if sim_type=="with_sharing":
                result_set[my_colnames[j]]=solution_values[j]
            elif sim_type=="with_no_sharing":
                result_set[my_colnames_ns[j]]=solution_values[j]
            
            
    pprint.pprint(result_set)
    process_results(result_set)
    
     
def process_results(results_set):
    for key,value in results_set.items():
        if key[0]=="x":
            key1=key.replace("]"," ")
            param=key1.split("[")
            i=int(param[1])
            o=int(param[2])
            r=int(param[3])
            c=int(param[4])
            x[i][o][r][c]=value
#             print (key,x[i][o][r][c])
        if key[0]=="x_ns":
            key1=key.replace("]"," ")
            param=key1.split("[")
            i=int(param[1])
            o=int(param[2])
            r=int(param[3])
            c=int(param[4])
            x_ns[i][o][r][c]=value
#             print (key,x_ns[i][o][r][c])
        if key[0]=="w":
            key1=key.replace("]"," ")
            param=key1.split("[")
            i=int(param[1])
            n=int(param[2])
            o=int(param[3])
            r=int(param[4])
            c=int(param[5])
            w[i][n][o][r][c]=value
#             print (key,w[i][n][o][r][c])
        if key[0]=="y":
            key1=key.replace("]"," ")
            param=key1.split("[")
            i=int(param[1])
            n=int(param[2])
            o=int(param[3])
            r=int(param[4])
            c=int(param[5])
            y[i][n][o][r][c]=value
#             print (key,y[i][n][o][r][c])
        
def load_slot_rates(current_slot):
    #   -------------  rates  -------------------------                  
    for i in range(V):
        for o in range(Objects): 
            for row in range(Rows):
                for m in range(M):
                    r[i][o][row][m]=0
    
    for slot in range(slots_number):
        if slot==current_slot:
            for i in range(V):
                for o in range(Objects): 
                    for row in range(Rows):
                        for m in range(M):
                            r[i][o][row][m]=sim_r[current_slot][i][o][row][m]
                    
 
                        
def reset_model_variables():          
    # variables  
    for i in range(V):
        for o in range(Objects): 
            for row in range(Rows):
                for col in range(Cols):
                    x[i][o][row][col]=0
                    
    for i in range(V):
        for n in range(V):
            for o in range(Objects): 
                for row in range(Rows):
                    for col in range(Cols):
                        w[i][n][o][row][col]=0                
                        y[i][n][o][row][col]=0
                 
    # objective function                  
    my_obj.clear()
    my_colnames.clear()
    my_ub.clear()
    my_lb.clear()
    my_rownames.clear()
    my_rhs.clear()
    my_rows.clear()
    my_sense=""
    my_ctype=""

# ********************************************************    
# B: Model when not sharing 
# ********************************************************    

my_obj_ns=[]
my_colnames_ns=[]
my_ub_ns = []
my_lb_ns = []
my_rownames_ns=[]
my_rhs_ns=[]
my_rows_ns=[]
global my_ctype_ns
my_ctype_ns=""
global my_sense_ns
my_sense_ns=""

 
def reset_model_variables_ns():          
    #  variables  
    for i in range(V):
        for o in range(Objects): 
            for row in range(Rows):
                for col in range(Cols):
                    x_ns[i][o][row][col]=0
   
    # objective function                  
    my_obj_ns.clear()
    my_colnames_ns.clear()
    my_ub_ns.clear()
    my_lb_ns.clear()
    my_rownames_ns.clear()
    my_rhs_ns.clear()
    my_rows_ns.clear()
    my_sense_ns=""
    my_ctype_ns="" 

def build_model_ns():
             
    # Benefits 
    build_b1_benefit_ns()
    #  Costs
    build_c1_cost_ns()
#     #  Constraints
    build_constraintA_ns()       
    build_constraintB_ns()       
    
    
def build_b1_benefit_ns():
    """ B1:  Benefit   """ 
    coef=0
    for i in range(V):
        for o in range(Objects): 
            for rowD in range(Rows):
                for col in range(Cols):
                    coef=0
                    for rowS in range(Rows):
                        for m in range(M):
                            req=r[i][o][rowS][m]
                            gain=b[i][o][rowS][rowD][col][m]
                            coef=coef+req*gain
                            x_key=x_ns_names[i][o][rowD][col]
                            b1_coeff_ns[x_key]=str(coef)
    
#     print ("b1 coeff ns")                        
#     pprint.pprint(b1_coeff_ns)
                            

def build_c1_cost_ns():
    """ C1:  Cost of placement in owned storage  """
    for i in range(V):
        for o in range(Objects):
            size=s[o] 
            for row in range(Rows):
                for col in range(Cols):
                    coef=0
                    cost=c[i][row][col]
                    coef=size*cost
                    x_key=x_ns_names[i][o][row][col]    
                    c1_coeff_ns[x_key]=str(coef)    
                   
#     print ("c1 coeff ns")     
#     pprint.pprint(c1_coeff_ns)
    
def build_constraintA_ns():       
    """
        Constraint A: Capacity constraints
    """
    for i in range(V):
        for row in range(Rows):
            for col in range(Cols):
                global constraintA_coeff_ns
                constraintA_coeff_ns[i][row][col]={}
    
                for o in range(Objects):
                    xcoef=s[o]
                    key=x_ns_names[i][o][row][col]
                    (constraintA_coeff_ns[i][row][col])[key]=xcoef   

def build_constraintB_ns():    
    """ 
     Constraint B:  Store only in one place constraint
    """
    for i in range(V):
        for o in range(Objects):
            constraintB_coeff_ns[i][o]={}
            for row in range(Rows):
                for col in range(Cols):
                    key=x_ns_names[i][o][row][col]
                    (constraintB_coeff_ns[i][o])[key]=1
     

def build_cplex_model_ns():
    temp_obj_coeff_ns={}
    
    """ B1: Objective function """
    for b1_key,b1_value in b1_coeff_ns.items():
        if b1_key in temp_obj_coeff_ns:
#             print ("B1 key: found")
            current_value=int(temp_obj_coeff_ns[b1_key])
            temp_obj_coeff_ns[b1_key]=current_value+float(b1_value)
        else:
#             print ("B1 key: new key entered"+b1_key)
            temp_obj_coeff_ns[b1_key]=float(b1_value)
               
#   
    """ C1: Cost function """          
    for c1_key,c1_value in c1_coeff_ns.items():
        if c1_key in temp_obj_coeff_ns:
            current_value=float(temp_obj_coeff_ns[c1_key])
            new_value=current_value-float(c1_value)
            temp_obj_coeff_ns[c1_key]=new_value
#             print ("C1 key: Found "+c1_key)
#             print ("Old Value: "+str(current_value) +" -- New value: "+str(new_value))
        else:
#             print ("Did not found the c1_key. New key entered:"+c1_key)
            value=-1*float(c1_value)
            temp_obj_coeff_ns[c1_key]=value           
    
    """ Prepare the final list"""    
    for key,value in temp_obj_coeff_ns.items():    
        my_obj_ns.append(int(value))  
        my_colnames_ns.append(key)
                 
#     print("my_obj_ns:")                
#     pprint.pprint(my_obj_ns)                
#     print("my_colnames_ns:")                
#     pprint.pprint(my_colnames_ns)                
    
    """Variables Bounds """
    global my_ctype_ns
    my_ctype_ns=""
    index=0    
    while index <len(my_colnames_ns):
        my_lb_ns.append(0.0)
        my_ub_ns.append(1.0)
        my_ctype_ns = my_ctype_ns+"I"
        index=index+1
    
#     print("my_lb")
#     pprint.pprint(my_lb)
#     print("my_temp_ub")
#     pprint.pprint(my_temp_ub)
#     print("my_ctype")
#     pprint.pprint(my_ctype)

    """ Constraint A set"""
    for i in range(V):
        for row in range(Rows):
            for col in range(Cols):
                constrainta_row=[]
                lista_coeff_key=[]
                lista_coeff_value=[]
                my_rhs_ns.append(constraintA_bound[i][row][col])
                identifier="rowA["+str(i)+"]["+str(row)+"]["+str(col)+"]"
                my_rownames_ns.append(identifier)
                    
                for key,value in constraintA_coeff_ns[i][row][col].items():
                    lista_coeff_key.append(key)
                    lista_coeff_value.append(value)    
                constrainta_row.append(lista_coeff_key)
                constrainta_row.append(lista_coeff_value)
                my_rows_ns.append(constrainta_row)
                

    """ Constraint B set"""
    for i in range(V):
        for o in range(Objects):
            identifier="rowB["+str(i)+"]["+str(o)+"]"
            my_rownames_ns.append(identifier)
            my_rhs_ns.append(constraintB_bound[i][o])
            constraintb_row=[]
            listb_coeff_key=[]
            listb_coeff_value=[]
            for key,value in constraintB_coeff_ns[i][o].items():
                listb_coeff_key.append(key)
                listb_coeff_value.append(value)    
            constraintb_row.append(listb_coeff_key)
            constraintb_row.append(listb_coeff_value)
            my_rows_ns.append(constraintb_row)

#     print("My row names with B")
#     pprint.pprint(my_rownames)
#     print("My constraints rows with B")
#     pprint.pprint(my_rows)
#     print("My rhs with B")
#     pprint.pprint(my_rhs)
            
    """ My sense """
    global my_sense_ns
    my_sense_ns=""
    index=0
    while index <len(my_rows_ns):
        my_sense_ns=my_sense_ns+"L"
        index=index+1

def populatebyrow_ns(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj=my_obj_ns, lb=my_lb_ns, ub=my_ub_ns, types=my_ctype_ns,
                       names=my_colnames_ns)

    prob.linear_constraints.add(lin_expr=my_rows_ns, senses=my_sense_ns,
                                rhs=my_rhs_ns, names=my_rownames_ns)


def simulator():
    
    initialize_simulator()
    slot=0
    
    while slot<slots_number:
        print("************************************")
        print ("         slot :",slot)
        print("************************************")
        
        load_slot_rates(slot)
        
        # simulation with sharing
        print (" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
        print ("   -- simulation with sharing --")
        reset_model_variables()
        build_model() 
        build_cplex_model()
        solver("with_sharing",slot)
        
         
    
        # simulation without sharing
        print()
        print ("   %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
        print ("   -- simulation without sharing --")
        reset_model_variables_ns()
        build_model_ns()
        build_cplex_model_ns() 
        solver("with_no_sharing",slot)
        slot=slot+1

        file = open("results.txt","a")
        message="\n"
        file.write(message)
        file.close()
       
                 
if __name__ == "__main__":
    simulator()
    
    
    
    
    