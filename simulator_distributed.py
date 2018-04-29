from __future__ import print_function

import pprint
import numpy as np
import cplex
from cplex.exceptions import CplexError
import global_variables
from operator import itemgetter
from numpy.core.umath import remainder


"""parameters for all modes"""
# CDN providers
V=global_variables.V
# Mobile operators
M=global_variables.M
# objects_number >10
objects_number=global_variables.objects_number
# Rows of the Grid 
Rows=global_variables.Rows
# Columns of the Grid
Cols=global_variables.Cols
# default_object_size
default_object_size=global_variables.default_object_size
# slots_number
slots_number=global_variables.slots_number
# edge_cost
edge_cost=global_variables.edge_cost
# zipf_parameter
zipf_parameter = global_variables.zipf_parameter
# edge_benefit
edge_benefit=global_variables.edge_benefit
# edge_storage_limit
edge_storage_limit=global_variables.edge_storage_limit

# Defines objects popularity weights pw[o]
pw=[[0 for o in range(objects_number)]for i in range(V)] 
# Defines request rate r[i][o][row][m]. This is for the entire simulation
sim_r=[[[[[0 for m in range(M)]for row in range(Rows)] for o in range(objects_number)] for i in range(V)] for s in range(slots_number)]
# Defines request rate r[i][o][row][m]. This is updated at each slot
r=[[[[0 for m in range(M)]for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 
# Defines benefit b[i][o][row][col][m]   
b=[[[[[[0 for m in range(M)] for col in range(Cols)]for rowD in range(Rows)] for rowS in range(Rows)] for o in range(objects_number)] for i in range(V)]    
# Defines benefit psi[i][n][o][row][col]   
psi=[[[[0 for col in range(Cols)] for row in range(Rows)] for n in range(V)]for i in range(V)] 
# Defines benefit h[i][n][o][row][col]   
h=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
# Defines c[i][row][col] unit cost    
c=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)] 
# Defines s[o] size of object o   
s=[0 for o in range(objects_number)]

capacity_constraint=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]



"""Centralized case"""
x=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)]
w=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
y=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 

x_names=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 
w_names=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
y_names=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 

b1_coeff={}
b2_coeff={}
b3_coeff={}
c1_coeff={}
c2_coeff={}

constraintA_bound=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
constraintA_coeff=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
constraintB_bound=[[1 for o in range(objects_number)] for i in range(V)]
constraintB_coeff=[[0 for o in range(objects_number)] for i in range(V)]
constraintC_bound=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)]for n in range(V)]for i in range(V)]
constraintC_coeff=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)]for n in range(V)]for i in range(V)]

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


"""Without collaboration"""
nc_x=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 
nc_x_names=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 

nc_b1_coeff={}
nc_c1_coeff={}

nc_constraintA_coeff=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
nc_constraintB_coeff=[[0 for o in range(objects_number)] for i in range(V)]

nc_my_obj=[]
nc_my_colnames=[]
nc_my_ub = []
nc_my_lb = []
nc_my_rownames=[]
nc_my_rhs=[]
nc_my_rows=[]
global nc_my_ctype
nc_my_ctype=""
global nc_my_sense
nc_my_sense=""

"""Distributed with collaboration"""
ds1_x=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 
ds3_w=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
ds3_y=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 

ds1_x_names=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 
ds3_w_names=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
ds3_y_names=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)]

ds3_b1_coeff={}
ds3_c1_coeff={}

ds2_capacity_reserved=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]

ds3_constraintA_bound=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
ds3_constraintA_coeff=[[[[0 for col in range(Cols)] for row in range(Rows)] for n in range(V)]for i in range(V)]
ds3_constraintB_bound=[[0 for o in range(objects_number)] for i in range(V)]
ds3_constraintB_coeff=[[0 for o in range(objects_number)] for i in range(V)]
ds3_constraintC_bound=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)]for n in range(V)]for i in range(V)]
ds3_constraintC_coeff=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)]for n in range(V)]for i in range(V)]


ds3_w_number_allocated=[[0 for n in range(V)] for i in range(V)]
ds3_y_number_allocated=[[0 for n in range(V)] for i in range(V)]



ds3_my_obj=[]
ds3_my_colnames=[]
ds3_my_ub = []
ds3_my_lb = []
ds3_my_rownames=[]
ds3_my_rhs=[]
ds3_my_rows=[]
global ds3_my_ctype
ds3_my_ctype=""
global ds3_my_sense
ds3_my_sense=""

ds4_x=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 
ds4_w=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
ds4_y=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
ds4_w_number_allocated=[[0 for n in range(V)] for i in range(V)]
ds4_y_number_allocated=[[0 for n in range(V)] for i in range(V)]


ds5_x=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 
ds5_w=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
ds5_y=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
ds5_x_number_allocated=[0 for i in range(V)]
ds5_w_number_allocated=[[0 for n in range(V)] for i in range(V)]
ds5_y_number_allocated=[[0 for n in range(V)] for i in range(V)]

ds5_x_names=[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for i in range(V)] 
ds5_w_names=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)] 
ds5_y_names=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)] for n in range(V)]for i in range(V)]

ds5_x_fixed=[0 for i in range(V)]
ds5_y_fixed=[[0 for n in range(V) ] for i in range(V)]

ds5_b1_coeff={}
ds5_b2_coeff={}
ds5_b3_coeff={}
ds5_c1_coeff={}
ds5_c2_coeff={}

ds5_constraintA1_bound=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
ds5_constraintA1_coeff=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
ds5_constraintA2_bound=[[[[0 for col in range(Cols)] for row in range(Rows)] for n in range(V)] for i in range(V)]
ds5_constraintA2_coeff=[[[[0 for col in range(Cols)] for row in range(Rows)] for n in range(V)] for i in range(V)]
ds5_constraintB_bound=[[0 for o in range(objects_number)] for i in range(V)]
ds5_constraintB_coeff=[[0 for o in range(objects_number)] for i in range(V)]
ds5_constraintC_bound=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)]for n in range(V)]for i in range(V)]
ds5_constraintC_coeff=[[[[[0 for col in range(Cols)] for row in range(Rows)] for o in range(objects_number)]for n in range(V)]for i in range(V)]


ds5_my_obj=[]
ds5_my_colnames=[]
ds5_my_ub = []
ds5_my_lb = []
ds5_my_rownames=[]
ds5_my_rhs=[]
ds5_my_rows=[]
global ds5_my_ctype
ds5_my_ctype=""
global ds5_my_sense
ds5_my_sense=""


def initialize_objects_size():    
    """ s[o]:  objects_number size"""
    for o in range(objects_number):
        s[o]=default_object_size    

def initialize_b():    
    """ Benefit b[i][o][rowS][rowD][col][m]: """
    
    for i in range(V):
        for o in range(objects_number):
            for rowS in range (Rows):
                for rowD in range (Rows):
                    for col in range (Cols):
                        for m in range (M):
                            distance=abs(rowD-rowS)+col
                            if distance==0:
                                b[i][o][rowS][rowD][col][m]=edge_benefit
                            else:
                                benefit =(edge_benefit*0.9)/distance
                                b[i][o][rowS][rowD][col][m]=max(1,benefit)
    
#     pprint.pprint(b)

    
def initialize_psi():    

    """ psi[i][n][row][col] """
    
    for i in range(V):
        for n in range(V):
            for row in range (Rows):
                for col in range (Cols):
                    value=c[n][row][col]*(1.2+n)
                    psi[i][n][row][col]=value
    
#     pprint.pprint(psi)

def initialize_h():    
   
    """ h[i][n][o][row][col] """
    for i in range(V):
        for n in range(V):
            for o in range(objects_number):
                for rowS in range (Rows):
                    for rowD in range (Rows):
                        for col in range (Cols):
                            avg_b=0
                            for m in range (M):
                                avg_b=avg_b+b[n][o][rowS][rowD][col][m]
                            avg_b=avg_b/M
                            h[i][n][o][rowD][col]=avg_b*0.1
        
    
    
  
     
def initialize_placement_cost():     
     
    """ c[i][row][col] Placement COST """
    
    for i in range(V):
        for row in range (Rows):
            for col in range (Cols):
                if col==0:
                    c[i][row][col]=edge_cost
                else:
                    cost =edge_cost*0.9/col
                    c[i][row][col]=max(1,cost)
     
#     pprint.pprint (c)          


def initialize_capacity_constraints():

    """  constraintA_bound[i][row][col] """ 
    for i in range(V):
        for row in range (Rows):
            for col in range (Cols):
                capacity_constraint[i][row][col]=edge_storage_limit*(col+0.2)
                if i==0 and col==Cols-1:
                    capacity_constraint[i][row][col]=100
                else:
                    capacity_constraint[i][row][col]=20




                        

                    
                        
                        
                        
def initialize_simulator():
    build_variables_names()
    initialize_objects_size()
    initialize_placement_cost()
    initialize_b()
    initialize_psi()
    initialize_h()
    initialize_capacity_constraints() 
    initialize_objects_weights()
    initialize_request_rates()

def initialize_request_rates():
    """" Requests for entire simulation """
    #   Requests to cdn i
    lamda_r=[[[0 for m in range(M)]for row in range(Rows)] for i in range(V)] 
    for i in range(V):
        for row in range(Rows):
            for m in range(M):
                lamda_r[i][row][m]=objects_number*2
                
    for i in range(V):
        for row in range(Rows):
            for m in range(M):
                requests_array=np.random.poisson(lamda_r[i][row][m],slots_number)
                sim_requests=requests_array.tolist()
#                 pprint.pprint(sim_requests)
                for slot in range(slots_number):
#                     print("***** slot :",slot)
                    for o in range(objects_number):
                        sim_r[slot][i][o][row][m]=int(round(sim_requests[slot]*pw[i][o]))  
    
#     pprint.pprint(sim_r)
  
                               
def initialize_objects_weights():    
    """ initializes objects' popularity weights according to zipf distribution. Each cdn has diffrent popularity per object."""
    
    for i in range(V):
        zipf_object_popularity=np.random.zipf(zipf_parameter,objects_number)
        popularity_list_sum=0
        popularity_list=zipf_object_popularity.tolist()
        popularity_list_sum=sum(popularity_list) 
#         pprint.pprint(popularity_list)  
        for o in range(objects_number):
            pw[i][o]=popularity_list[o]/popularity_list_sum
    
          
def build_variables_names():
    """ X_names: x_names[i][o][row][col]"""
    index=0
    for i in range(V):
        for o in range(objects_number): 
            for row in range(Rows):
                for col in range(Cols):
                    x_names[i][o][row][col]="x["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1     

    """ X_ns_ NAMES: nc_x_names[i][o][row][col]"""
    index=0
    for i in range(V):
        for o in range(objects_number): 
            for row in range(Rows):
                for col in range(Cols):
                    nc_x_names[i][o][row][col]="nc_x["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1       
                    
    """ X_ds1_ NAMES: nc_x_names[i][o][row][col]"""
    index=0
    for i in range(V):
        for o in range(objects_number): 
            for row in range(Rows):
                for col in range(Cols):
                    ds1_x_names[i][o][row][col]="ds1_x["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1          
    
    """ X_ds5_ NAMES: nc_x_names[i][o][row][col]"""
    index=0
    for i in range(V):
        for o in range(objects_number): 
            for row in range(Rows):
                for col in range(Cols):
                    ds5_x_names[i][o][row][col]="ds5_x["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1  
    
      
    """ w_names: w_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(objects_number): 
                for row in range(Rows):
                    for col in range(Cols):
                        w_names[i][n][o][row][col]="w["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1
                        
    """ w_ds3_names: ds3_w_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(objects_number): 
                for row in range(Rows):
                    for col in range(Cols):
                        ds3_w_names[i][n][o][row][col]="ds3_w["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1

    """ w_ds5_names: ds3_w_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(objects_number): 
                for row in range(Rows):
                    for col in range(Cols):
                        ds5_w_names[i][n][o][row][col]="ds5_w["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1                    
     
    """YNames: y_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(objects_number): 
                for row in range(Rows):
                    for col in range(Cols):
                        y_names[i][n][o][row][col]="y["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1 
                        
                        
    """Y_dNames: ds3_y_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(objects_number): 
                for row in range(Rows):
                    for col in range(Cols):
                        ds3_y_names[i][n][o][row][col]="ds3_y["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1 
    
    """Y_dNames: ds5_y_names[i][n][o][row][col]"""
    index=0
    for i in range(V):
        for n in range(V):
            for o in range(objects_number): 
                for row in range(Rows):
                    for col in range(Cols):
                        ds5_y_names[i][n][o][row][col]="ds5_y["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                        index=index+1 
    
    

def load_slot_rates(current_slot):                 
    for i in range(V):
        for o in range(objects_number): 
            for row in range(Rows):
                for m in range(M):
                    r[i][o][row][m]=0
    
    for slot in range(slots_number):
        if slot==current_slot:
            for i in range(V):
                for o in range(objects_number): 
                    for row in range(Rows):
                        for m in range(M):
                            r[i][o][row][m]=sim_r[current_slot][i][o][row][m]

# ******************** Case A: Centralized solution ***********************
# Model when collaborating 

def cwc_build_model():
             
    """   Benefits  """
    cwc_build_benefit_b1()
    cwc_build_benefit_b2()
    cwc_build_benefit_b3()
    """   Costs  """
    cwc_build_cost_c1()   
    cwc_build_cost_c2()
#     
    """ Constraints   """  
    cwc_build_constraintA_coeff()
    cwc_build_constraintA_bound()       
    cwc_build_constraintB_coeff()
    cwc_build_constraintB_bound()        
    cwc_build_constraintC_coeff()  
    cwc_build_constraintC_bound() 
    
def cwc_build_benefit_b1():
    """ B1:  Benefit   """ 
    coef=0
    for i in range(V):
        for o in range(objects_number): 
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
                                
def cwc_build_benefit_b2():
   
    for i in range(V):
        for o in range(objects_number):
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

def cwc_build_benefit_b3():
#    r[i][o][row][m]
    for i in range(V):
        for o in range(objects_number):
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            coef=0
                            for m in range(M):
                                rate=r[n][o][row][m]
                                benefit=h[i][n][o][row][col]
                                coef=coef+rate*benefit
                            y_key=y_names[n][i][o][row][col]    
                            b3_coeff[y_key]=str(coef)    
       
def cwc_build_cost_c1():
    """ C1:  Cost of placement in owned storage  """
    for i in range(V):
        for o in range(objects_number):
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
                                           
def cwc_build_cost_c2():
    """Cost of placing content from CDN n """
    for i in range(V):
        for o in range(objects_number):
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
                                                              
def cwc_build_constraintA_coeff():       
    """
        Constraint A: Capacity constraints
    """
    for i in range(V):
        for row in range(Rows):
            for col in range(Cols):
                global constraintA_coeff
                constraintA_coeff[i][row][col]={}
    
                for o in range(objects_number):
                    xcoef=s[o]
                    key=x_names[i][o][row][col]
                    (constraintA_coeff[i][row][col])[key]=xcoef   
                    for n in range(V):
                        if n!=i:
                            xcoef=s[o]
                            key=w_names[n][i][o][row][col]
                            (constraintA_coeff[i][row][col])[key]=xcoef

def cwc_build_constraintA_bound():

    """  constraintA_bound[i][row][col] """ 
    for i in range(V):
        for row in range (Rows):
            for col in range (Cols):
                constraintA_bound[i][row][col]=capacity_constraint[i][row][col]
                
def cwc_build_constraintB_coeff():    
    """ 
     Constraint B:  Store only in one place constraint
         
    """
    for i in range(V):
        for o in range(objects_number):
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

def cwc_build_constraintB_bound():
    for i in range(V):
        for o in range(objects_number):
            constraintB_bound[i][o]=1

    
def cwc_build_constraintC_coeff():
    """ Constraint C: In order to ask for an object from CDN i he needs to have it"""
    for i in range(V):
            for o in range(objects_number):
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

def cwc_build_constraintC_bound():
    for i in range(V):
        for n in range(V):
            for o in range(objects_number):
                for row in range(Rows):
                    for col in range(Cols):
                        constraintC_bound[i][n][o][row][col]=0



def cwc_build_cplex_model():
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
     
#     mmm=0
#     for kkk in my_obj:
#         print("My_COLNAME:",my_colnames[mmm], "My_objective", kkk)
#         mmm = mmm+1
                    
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
        for o in range(objects_number):
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
        for o in range(objects_number):
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
                                          
def cwc_reset_model_variables():          
    # variables  
    for i in range(V):
        for o in range(objects_number): 
            for row in range(Rows):
                for col in range(Cols):
                    x[i][o][row][col]=0
                    
    for i in range(V):
        for n in range(V):
            for o in range(objects_number): 
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



# ******************** Case B: Local solution ***********************



 
def nc_reset_model_variables():          
    #  variables  
    for i in range(V):
        for o in range(objects_number): 
            for row in range(Rows):
                for col in range(Cols):
                    nc_x[i][o][row][col]=0
   
    # objective function                  
    nc_my_obj.clear()
    nc_my_colnames.clear()
    nc_my_ub.clear()
    nc_my_lb.clear()
    nc_my_rownames.clear()
    nc_my_rhs.clear()
    nc_my_rows.clear()
    nc_my_sense=""
    nc_my_ctype="" 

def nc_build_model():
             
    # Benefits 
    nc_build_benefit_b1()
    #  Costs
    nc_build_cost_c1()
#     #  Constraints
    nc_build_constraintA()       
    nc_build_constraintB()       
    
def nc_build_benefit_b1():
    """ B1:  Benefit   """ 
    coef=0
    for i in range(V):
        for o in range(objects_number): 
            for rowD in range(Rows):
                for col in range(Cols):
                    coef=0
                    for rowS in range(Rows):
                        for m in range(M):
                            req=r[i][o][rowS][m]
                            gain=b[i][o][rowS][rowD][col][m]
                            coef=coef+req*gain
                    x_key=nc_x_names[i][o][rowD][col]
                    nc_b1_coeff[x_key]=str(coef)
                         
def nc_build_cost_c1():
    """ C1:  Cost of placement in owned storage  """
    for i in range(V):
        for o in range(objects_number):
            size=s[o] 
            for row in range(Rows):
                for col in range(Cols):
                    coef=0
                    cost=c[i][row][col]
                    coef=size*cost
                    x_key=nc_x_names[i][o][row][col]    
                    nc_c1_coeff[x_key]=str(coef)    
                   
def nc_build_constraintA():       
    """
        Constraint A: Capacity constraints
    """
    for i in range(V):
        for row in range(Rows):
            for col in range(Cols):
                global nc_constraintA_coeff
                nc_constraintA_coeff[i][row][col]={}
    
                for o in range(objects_number):
                    xcoef=s[o]
                    key=nc_x_names[i][o][row][col]
                    (nc_constraintA_coeff[i][row][col])[key]=xcoef   

def nc_build_constraintB():    
    """ 
     Constraint B:  Store only in one place constraint
    """
    for i in range(V):
        for o in range(objects_number):
            nc_constraintB_coeff[i][o]={}
            for row in range(Rows):
                for col in range(Cols):
                    key=nc_x_names[i][o][row][col]
                    (nc_constraintB_coeff[i][o])[key]=1
     
def nc_build_cplex_model():
    temp_obj_coeff_ns={}
    
    """ B1: Objective function """
    for b1_key,b1_value in nc_b1_coeff.items():
        if b1_key in temp_obj_coeff_ns:
#             print ("B1 key: found")
            current_value=int(temp_obj_coeff_ns[b1_key])
            temp_obj_coeff_ns[b1_key]=current_value+float(b1_value)
        else:
#             print ("B1 key: new key entered"+b1_key)
            temp_obj_coeff_ns[b1_key]=float(b1_value)
               
#   
    """ C1: Cost function """          
    for c1_key,c1_value in nc_c1_coeff.items():
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
        nc_my_obj.append(int(value))  
        nc_my_colnames.append(key)
                 
#     print("nc_my_obj:")                
#     pprint.pprint(nc_my_obj)                
#     print("nc_my_colnames:")                
#     pprint.pprint(nc_my_colnames)                
    
    """Variables Bounds """
    global nc_my_ctype
    nc_my_ctype=""
    index=0    
    while index <len(nc_my_colnames):
        nc_my_lb.append(0.0)
        nc_my_ub.append(1.0)
        nc_my_ctype = nc_my_ctype+"I"
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
                nc_my_rhs.append(constraintA_bound[i][row][col])
                identifier="rowA["+str(i)+"]["+str(row)+"]["+str(col)+"]"
                nc_my_rownames.append(identifier)
                    
                for key,value in nc_constraintA_coeff[i][row][col].items():
                    lista_coeff_key.append(key)
                    lista_coeff_value.append(value)    
                constrainta_row.append(lista_coeff_key)
                constrainta_row.append(lista_coeff_value)
                nc_my_rows.append(constrainta_row)
                

    """ Constraint B set"""
    for i in range(V):
        for o in range(objects_number):
            identifier="rowB["+str(i)+"]["+str(o)+"]"
            nc_my_rownames.append(identifier)
            nc_my_rhs.append(constraintB_bound[i][o])
            constraintb_row=[]
            listb_coeff_key=[]
            listb_coeff_value=[]
            for key,value in nc_constraintB_coeff[i][o].items():
                listb_coeff_key.append(key)
                listb_coeff_value.append(value)    
            constraintb_row.append(listb_coeff_key)
            constraintb_row.append(listb_coeff_value)
            nc_my_rows.append(constraintb_row)

#     print("My row names with B")
#     pprint.pprint(my_rownames)
#     print("My constraints rows with B")
#     pprint.pprint(my_rows)
#     print("My rhs with B")
#     pprint.pprint(my_rhs)
            
    """ My sense """
    global nc_my_sense
    nc_my_sense=""
    index=0
    while index <len(nc_my_rows):
        nc_my_sense=nc_my_sense+"L"
        index=index+1



# ******************** Case C: Distributed with collaboration ***********************
def dwc_step3_reset_model_variables():          
    for i in range(V):
        for n in range(V):
            for o in range(objects_number): 
                for row in range(Rows):
                    for col in range(Cols):
                        ds1_x[i][o][row][col]=0
                        ds3_w[i][n][o][row][col]=0                
                        ds3_y[i][n][o][row][col]=0

                 
    

    
def dwc_step1_load_xd_from_nc():  

    for i in range (V):
        for o in range(objects_number):
            for row in range (Rows):
                for col in range (Cols):
                    ds1_x[i][o][row][col]=nc_x[i][o][row][col]
                    if ds1_x[i][o][row][col]>0:
                        print(ds1_x_names[i][o][row][col])
                
    
def dwc_step3_build_model(i):

    dwc_step3_build_b1(i)
    dwc_step3_build_c1(i)
    dwc_step3_build_constraintA_coeff(i)
    dwc_step3_build_constraintA_bound()
    dwc_step3_build_constraintB_coeff(i)
    dwc_step3_build_constraintB_bound(i)
    dwc_step3_build_constraintC_coeff(i)
    dwc_step3_build_constraintC_bound(i)
                                    
                                    
def dwc_object_is_placed_in_xd(i,o):
    for row in range (Rows):
        for col in range (Cols): 
            if ds1_x[i][o][row][col]==1.0:
                return True
    
    return False

def dwc_step3_build_b1(i):
    """ B1:  Benefit   """ 
    coef=0
    ds3_b1_coeff.clear()
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o)==False: 
            for rowD in range(Rows):
                for col in range(Cols):
                    coef=0
                    for rowS in range(Rows):
                        for m in range(M):
                            req=r[i][o][rowS][m]
                            gain=b[i][o][rowS][rowD][col][m]
                            coef=coef+req*gain
                    for n in range(V):
                        if n!=i:
                            ds3_w_key=ds3_w_names[i][n][o][rowD][col]
                            ds3_y_key=ds3_y_names[i][n][o][rowD][col]
                            ds3_b1_coeff[ds3_w_key]=str(coef)
                            ds3_b1_coeff[ds3_y_key]=str(coef)
#     print("ds3_b1_coeff")
#     pprint.pprint(ds3_b1_coeff)
    
    
    
def dwc_step3_build_c1(i):
    ds3_c1_coeff.clear()
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o)==False:
            size=s[o] 
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                        #   w parameters
                            coef=0
                            cost=psi[n][i][row][col]
                            coef=size*cost
                            ds3_w_key=ds3_w_names[i][n][o][row][col]
                            if ds3_w_key in ds3_b1_coeff:    
                                ds3_c1_coeff[ds3_w_key]=str(coef)   
                        #   y parameters
                            coef=0
                            cost=h[n][i][o][row][col]
                            coef=cost
                            ds3_y_key=ds3_y_names[i][n][o][row][col]    
                            if ds3_y_key in ds3_b1_coeff:
                                ds3_c1_coeff[ds3_y_key]=str(coef)  
#     if i==1: 
#         for key in ds3_b1_coeff:
#             print(key,"b1:", ds3_b1_coeff[key], "c1", ds3_c1_coeff[key] )

def dwc_step3_build_constraintA_coeff(i):       
    """
        Constraint A: Capacity constraints coefficients
    """
    for row in range(Rows):
        for col in range(Cols):
            for n in range(V):
                if n!=i:
                    ds3_constraintA_coeff[i][n][row][col]={}
                    for o in range(objects_number):
                        key=ds3_w_names[i][n][o][row][col]
                        if key in ds3_b1_coeff:
                            (ds3_constraintA_coeff[i][n][row][col])[key]=s[o]

#     print("ds3_constraintA_coeff")
#     pprint.pprint(ds3_constraintA_coeff)  
                      
def dwc_step3_build_constraintA_bound():
    
    for i in range (V):     
        for row in range (Rows):
            for col in range (Cols): 
                capacity_reserved=0
                for o in range(objects_number):                      
                    if ds1_x[i][o][row][col]>0:         
                        capacity_reserved=capacity_reserved+s[o]
                ds2_capacity_reserved[i][row][col]=capacity_reserved            
                ds3_constraintA_bound[i][row][col]= constraintA_bound[i][row][col]-ds2_capacity_reserved[i][row][col]           

#     print ("constraintA_ds3_bound")                        
#     pprint.pprint(ds3_constraintA_bound)  
    
def dwc_step3_build_constraintB_coeff(i):    
    """ 
     Constraint B:  Store only in one place constraint
    """
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o)==False: 
            ds3_constraintB_coeff[i][o]={}
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            key=ds3_w_names[i][n][o][row][col]
                            (ds3_constraintB_coeff[i][o])[key]=1
                            key=ds3_y_names[i][n][o][row][col]
                            (ds3_constraintB_coeff[i][o])[key]=1  
        
#     print("ds3_constraintB_coeff")                       
#     pprint.pprint(ds3_constraintB_coeff)

    
def dwc_step3_build_constraintB_bound(i):
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o):
            ds3_constraintB_bound[i][o]=0
        else:
            ds3_constraintB_bound[i][o]=1   
   
#     print ("ds3_constraintB_bound")     
#     pprint.pprint(ds3_constraintB_bound)     
                                                 
def dwc_step3_build_constraintC_coeff(i):
    """ Constraint C: In order to ask for an object from CDN i he needs to have it"""
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o)==False: 
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            ds3_constraintC_coeff[i][n][o][row][col]={}
                            ds3_y_key=ds3_y_names[i][n][o][row][col]
                            (ds3_constraintC_coeff[i][n][o][row][col])[ds3_y_key]=1   
    
#     print("ds3_constraintC_coeff")
#     pprint.pprint(ds3_constraintC_coeff)                        


def dwc_step3_build_constraintC_bound(i):                           
    for n in range(V):
        for o in range (objects_number):
            for row in range (Rows):
                for col in range (Cols):
                    ds3_constraintC_bound[i][n][o][row][col]=int(ds1_x[n][o][row][col])
                      
#     print("ds3_constraintC_bound")
#     pprint.pprint(ds3_constraintC_bound)
    
                        

def dwc_step3_build_cplex_model(i):
    temp_obj_coeff={}
    
    ds3_my_obj.clear()
    ds3_my_colnames.clear()
    ds3_my_ub.clear()
    ds3_my_lb.clear()
    ds3_my_rownames.clear()
    ds3_my_rhs.clear()
    ds3_my_rows.clear()

    
    """ B1: Objective function """
    for b1_key,b1_value in ds3_b1_coeff.items():
        temp_obj_coeff[b1_key]=float(b1_value)
            #   
    """ C1: Cost function """          
    for c1_key,c1_value in ds3_c1_coeff.items():
        current_value=float(temp_obj_coeff[c1_key])
        new_value=current_value-float(c1_value)
        temp_obj_coeff[c1_key]=new_value
        

    """ Prepare the final list"""    
    for key,value in temp_obj_coeff.items():    
        ds3_my_obj.append(int(value))  
        ds3_my_colnames.append(key)
        
#     if i==1:   
#         mmm=0
#         for kkk in ds3_my_obj:
#             print("My_COLNAME:",ds3_my_colnames[mmm], "My_objective", kkk)
#             mmm = mmm+1
                     
#     print("my_obj:")                
#     pprint.pprint(ds3_my_obj)                
#     print("my_colnames:")                
#     pprint.pprint(ds3_my_colnames)                
    
    """Variables Bounds """
    global ds3_my_ctype
    ds3_my_ctype=""
    index=0    
    while index <len(ds3_my_colnames):
        ds3_my_lb.append(0.0)
        ds3_my_ub.append(1.0)
        ds3_my_ctype = ds3_my_ctype+"I"
        index=index+1
    
#     print("my_lb")
#     pprint.pprint(ds3_my_lb)
#     print("my_ub")
#     pprint.pprint(ds3_my_ub)
#     print("my_ctype")
#     pprint.pprint(ds3_my_ctype)

    """ Constraint A set"""
    for row in range(Rows):
        for col in range(Cols):
            for n in range(V):
                if n!=i:
                    constrainta_row=[]
                    lista_coeff_key=[]
                    lista_coeff_value=[]
                    ds3_my_rhs.append(ds3_constraintA_bound[n][row][col])
                    identifier="rowA["+str(n)+"]["+str(row)+"]["+str(col)+"]"
                    ds3_my_rownames.append(identifier)
                    
                    for key,value in ds3_constraintA_coeff[i][n][row][col].items():
                        lista_coeff_key.append(key)
                        lista_coeff_value.append(value)    
                    constrainta_row.append(lista_coeff_key)
                    constrainta_row.append(lista_coeff_value)
                    ds3_my_rows.append(constrainta_row)
   
#     print("ds3_my_rows")
#     pprint.pprint(ds3_my_rownames)
#     pprint.pprint(ds3_my_rows)                

    """ Constraint B set"""
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o)==False:
            identifier="rowB["+str(i)+"]["+str(o)+"]"
            ds3_my_rownames.append(identifier)
            ds3_my_rhs.append(ds3_constraintB_bound[i][o])
            constraintb_row=[]
            listb_coeff_key=[]
            listb_coeff_value=[]
            for key,value in ds3_constraintB_coeff[i][o].items():
                listb_coeff_key.append(key)
                listb_coeff_value.append(value)    
            constraintb_row.append(listb_coeff_key)
            constraintb_row.append(listb_coeff_value)
            ds3_my_rows.append(constraintb_row)

#     print("My row names with B")
#     pprint.pprint(ds3_my_rownames)
#     print("My constraints rows with B")
#     pprint.pprint(ds3_my_rows)
#     print("My rhs with B")
#     pprint.pprint(ds3_my_rhs)

    """ Constraint C set"""
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o)==False:
            for n in range(V):
                if n!=i:
                    for row in range(Rows):
                        for col in range(Cols):
                            constraintc_row=[]
                            listc_coeff_key=[]
                            listc_coeff_value=[]
                            identifier="rowC["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                            ds3_my_rownames.append(identifier)
                            ds3_my_rhs.append(ds3_constraintC_bound[i][n][o][row][col])

                            for key,value in ds3_constraintC_coeff[i][n][o][row][col].items():
                                listc_coeff_key.append(key)
                                listc_coeff_value.append(value)    
                            constraintc_row.append(listc_coeff_key)
                            constraintc_row.append(listc_coeff_value)
                            ds3_my_rows.append(constraintc_row)
                                
                            
#     print("My row names with C")
#     pprint.pprint(ds3_my_rownames)
#     print("My constraints rows with C")
#     pprint.pprint(ds3_my_rows)
#     print("My rhs with C")
#     pprint.pprint(ds3_my_rhs)
                            
    """ My sense """
    global ds3_my_sense
    ds3_my_sense=""
    index=0
    while index <len(ds3_my_rows):
        ds3_my_sense=ds3_my_sense+"L"
        index=index+1





def dwc_step3_calculate_net_benefit(i,result_set):
    
    x_benefit=0
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o)==True: 
            for rowD in range(Rows):
                for col in range(Cols):
                    if ds1_x[i][o][rowD][col]>0:
                        coef=0
                        for rowS in range(Rows):
                            for m in range(M):
                                req=r[i][o][rowS][m]
                                gain=b[i][o][rowS][rowD][col][m]
                                coef=coef+req*gain
                        x_benefit= x_benefit + coef   
    
    x_cost=0
    for o in range(objects_number):
        if dwc_object_is_placed_in_xd(i,o)==True: 
            size=s[o] 
            for row in range(Rows):
                for col in range(Cols):
                    if ds1_x[i][o][row][col]>0:
                        coef=0
                        coef=size*c[i][row][col]
                        x_cost=x_cost+coef                 

    x_net_benefit=x_benefit-x_cost
    
    print("X_NET_BENEFIT: ",x_net_benefit)
    
#     pprint.pprint(ds3_my_obj)
#     pprint.pprint(ds3_my_colnames) 
#     pprint.pprint(result_set)
    
    additional_benefit=0
    for key in result_set:
        if key in ds3_my_colnames:
            index=ds3_my_colnames.index(key)
            additional_benefit = additional_benefit + ds3_my_obj[index]
            
    print("###### ADDITIONAL BENEFIT (B1,C1)", additional_benefit)  
    
    s3_net_benefit=x_net_benefit+additional_benefit
    return s3_net_benefit


def dwc_step4_solve_storage_violations(s3_results_sets):
    
    keys_list=[0 for i in range (V)]
    """Solve Conflicts"""    
    #Step 4-1: for each i list who wants to store objects
    for i in range(V):
        keys_list[i]=[]
        for n in range (V):
            if bool(s3_results_sets[n]):
                for key in s3_results_sets[n].items():
                    if key[0][0:5]=="ds3_w":
                        key1=key[0].replace("]"," ")
                        param=key1.split("[")
                        src=int(param[1])
                        dst=int(param[2])
                        if n==src and dst==i:
                            keys_list[i].append(key[0])
                            
#     pprint.pprint(keys_list) 
    
    #Step 4-2: find how much profit he can contribute
    weights_list=[0 for i in range (V)]
    sorted_weights_list=[0 for i in range (V)]
    
    for i in range(V):
        weights_list[i]=[]
        for n in range (V):
            if n!=i:
                for key in keys_list[i]:
                    for o in range (objects_number):
                        size=s[o]
                        for row in range(Rows):
                            for col in range (Cols):
                                variable=ds3_w_names[n][i][o][row][col]
                                if variable==key:
                                    profit_weight=size*psi[i][n][row][col]
                                    w_tuple=(variable,profit_weight)
                                    weights_list[i].append(w_tuple)
        sorted_weights_list[i]=sorted(weights_list[i],key=itemgetter(1),reverse=True)
#         pprint.pprint(sorted_weights_list[i])

    #Step 4-3: Keep only the ones that are not violationing storage limits
    storage_left=[[[0 for col in range(Cols)] for row in range(Rows)] for i in range(V)]
    for i in range(V):         
        for row in range(Rows):
            for col in range(Cols):
                storage_left[i][row][col]=ds3_constraintA_bound[i][row][col]
    
    for i in range(V):         
        for tmpl in sorted_weights_list[i]:
            key=tmpl[0]
            if key[0:5]=="ds3_w":
                key=key.replace("]"," ")
                param=key.split("[")
                src=int(param[1])
                dst=int(param[2])
                o=int(param[3])
                row=int(param[4])
                col=int(param[5])
                if  storage_left[i][row][col]-s[o]>0:
#                     print(tmpl[0])
                    ds4_w[src][dst][o][row][col]=1
                    ds4_w_number_allocated[src][dst]+=1
                    storage_left[i][row][col]=storage_left[i][row][col]-s[o]                  
                else:
                    print ("=================out of storage-CDN:",i)

def dwc_s4_update_variables_values():
    """"From step3 to step4 only w values were updated"""
    for i in range(V): 
        for o in range(objects_number):
            for row in range(Rows):
                for col in range(Cols):
                    ds4_x[i][o][row][col]=ds1_x[i][o][row][col]
                    for n in range(V): 
                        ds4_y[i][n][o][row][col]=ds3_y[i][n][o][row][col]

def dwc_step5_reset_variables():
    for i in range(V): 
        for o in range(objects_number):
            for row in range(Rows):
                for col in range(Cols):
                    ds5_x[i][o][row][col]=0
                    ds5_x_number_allocated[i]=0
                    for n in range(V): 
                        ds5_w[i][n][o][row][col]=0
                        ds5_w_number_allocated[i][n]=0
                        ds5_y[i][n][o][row][col]=0
                        ds5_y_number_allocated[i][n]=0
                        
    
    

    
    
    
def dwc_step5_fix_requested_x():
    for i in range (V):
        ds5_x_fixed[i]=[]
        for o in range(objects_number):
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            if ds4_y[n][i][o][row][col]>0:
                                ds5_x[i][o][row][col]=1 
                                ds5_x_fixed[i].append(ds5_x_names[i][o][row][col])

def dwc_step5_fix_requested_y():
    
    for i in range (V):
        for n in range(V):
            if n!=i:
                ds5_y_fixed[i][n]=[]
                for o in range(objects_number):
                    for row in range(Rows):
                        for col in range(Cols):     
                            if ds4_y[i][n][o][row][col]>0:
                                ds5_y[i][n][o][row][col]=1 
                                ds5_y_fixed[i][n].append(ds5_y_names[i][n][o][row][col])
                            
    
    
def dwc_step5_build_model(i):

    dwc_step5_build_benefit_b1(i)
    dwc_step5_build_cost_c1(i)
    
    dwc_step5_build_constraintA1_coeff(i)
    dwc_step5_build_constraintA1_bound(i)
    dwc_step5_build_constraintA2_coeff(i)
    dwc_step5_build_constraintA2_bound(i)
    dwc_step5_build_constraintB_coeff_and_bound(i)
    dwc_step5_build_constraintC_coeff_and_bound(i)

    
    
def dwc_step5_check_if_object_is_fixed(i,o):
    
    fixed=False
    for row in range(Rows):
        for col in range(Cols):
            x_name=ds5_x_names[i][o][row][col]
            if x_name in ds5_x_fixed[i]:
                return True
    for row in range(Rows):
        for col in range(Cols):
            for row in range(Rows):
                for n in range(V):
                    if n!=i:
                        y_name=ds5_y_names[i][n][o][row][col] 
                        if y_name in ds5_y_fixed[i][n]:
                            return True
    
    return fixed
    

def dwc_step5_build_benefit_b1(i):
    """ B1:  Benefit   """ 
    coef=0
    ds5_b1_coeff.clear()
    for o in range(objects_number):
        if dwc_step5_check_if_object_is_fixed(i,o)==False: 
            for rowD in range(Rows):
                for col in range(Cols):
                    coef=0
                    for rowS in range(Rows):
                        for m in range(M):
                            req=r[i][o][rowS][m]
                            gain=b[i][o][rowS][rowD][col][m]
                            coef=coef+req*gain
                    ds5_x_key=ds5_x_names[i][o][rowD][col]
                    ds5_b1_coeff[ds5_x_key]=str(coef)
                    for n in range(V):
                        if n!=i:
                            ds5_w_key=ds5_w_names[i][n][o][rowD][col]
                            ds5_y_key=ds5_y_names[i][n][o][rowD][col]
                            ds5_b1_coeff[ds5_w_key]=str(coef)
                            ds5_b1_coeff[ds5_y_key]=str(coef)


def dwc_step5_build_cost_c1(i):
    """ C1:  Cost of placement in owned storage  """
    ds5_c1_coeff.clear()
    for o in range(objects_number):
        if dwc_step5_check_if_object_is_fixed(i,o)==False: 
            size=s[o] 
            for row in range(Rows):
                for col in range(Cols):
                    coef=0
                    cost=c[i][row][col]
                    coef=size*cost
                    ds5_x_key=ds5_x_names[i][o][row][col]
                    ds5_c1_coeff[ds5_x_key]=str(coef)    
                    for n in range(V):
                        if n!=i:
                        #   w parameters
                            coef=0
                            cost=psi[n][i][row][col]
                            coef=size*cost
                            ds5_w_key=ds5_w_names[i][n][o][row][col]    
                            ds5_c1_coeff[ds5_w_key]=str(coef)   
                        #   y parameters
                            coef=0
                            cost=h[n][i][o][row][col]
                            coef=cost
                            ds5_y_key=ds5_y_names[i][n][o][row][col]    
                            ds5_c1_coeff[ds5_y_key]=str(coef)  



def dwc_step5_build_constraintA1_coeff(i):       
    """
        Constraint A: Local Capacity constraints for x that are not fixed
    """
    for row in range(Rows):
        for col in range(Cols):
            global ds5_constraintA1_coeff
            ds5_constraintA1_coeff[i][row][col]={}

            for o in range(objects_number):
                if dwc_step5_check_if_object_is_fixed(i,o)==False: 
                    key=ds5_x_names[i][o][row][col]
                    if key not in ds5_x_fixed[i]:
                        (ds5_constraintA1_coeff[i][row][col])[key]=s[o]   

def dwc_step5_build_constraintA2_coeff(i):       
    """
        Constraint A: Capacity constraints for remote n
    """
    for row in range(Rows):
        for col in range(Cols):
            global ds5_constraintA2_coeff
            for n in range (V):
                ds5_constraintA2_coeff[i][n][row][col]={}
                for o in range(objects_number):
                    if dwc_step5_check_if_object_is_fixed(i,o)==False: 
                        w_key=ds5_w_names[i][n][o][row][col]
                        coeff=s[o]
                        (ds5_constraintA2_coeff[i][n][row][col])[w_key]=coeff  

def dwc_step5_build_constraintA1_bound(i):
    """ Bound because others stored to i"""   
    for row in range (Rows):
        for col in range (Cols): 
            capacity_promised=0
            for o in range(objects_number):
                for n in range(V):                     
                    if ds4_w[n][i][o][row][col]>0:         
                        capacity_promised=capacity_promised+s[o]
        ds5_constraintA1_bound[i][row][col]= capacity_constraint[i][row][col]-capacity_promised          

def dwc_step5_build_constraintA2_bound(i):
    """" Capacity constraint in remote cdn n"""   
    for row in range (Rows):
        for col in range (Cols): 
            capacity_reserved=0
            for n in range(V):             
                if n!=i:        
                    for o in range(objects_number):
                        if ds4_w[i][n][o][row][col]>0:         
                            capacity_reserved=capacity_reserved+s[o]
                ds5_constraintA2_bound[i][n][row][col]= capacity_reserved    





def dwc_step5_build_constraintB_coeff_and_bound(i):    
    """ 
     Constraint B:  Store only in one place constraint
         
    """
    for o in range(objects_number):
        if dwc_step5_check_if_object_is_fixed(i,o)==False:
            ds5_constraintB_bound[i][o]=1 
            ds5_constraintB_coeff[i][o]={}
            for row in range(Rows):
                for col in range(Cols):
                    key=ds5_x_names[i][o][row][col]
                    (ds5_constraintB_coeff[i][o])[key]=1
                    for n in range(V):
                        if n!=i:
                            key=ds5_w_names[i][n][o][row][col]
                            (ds5_constraintB_coeff[i][o])[key]=1
                            key=ds5_y_names[i][n][o][row][col]
                            (ds5_constraintB_coeff[i][o])[key]=1   
                                
                                    

def dwc_step5_build_constraintC_coeff_and_bound(i):
    """ Constraint C: In order to ask for an object from CDN i he needs to have it"""
    for o in range(objects_number):
        if dwc_step5_check_if_object_is_fixed(i,o)==False: 
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            ds5_constraintC_coeff[i][n][o][row][col]={}
                            y_key=ds5_y_names[i][n][o][row][col]
                            (ds5_constraintC_coeff[i][n][o][row][col])[y_key]=1
                            x_remote_key=ds5_x_names[n][o][row][col]
                            if x_remote_key in ds5_x_fixed[n]:
                                ds5_constraintC_bound[i][n][o][row][col]=1
                            else:
                                ds5_constraintC_bound[i][n][o][row][col]=0

                                        
                                        
                                              
                            
              
        
        
        
def dwc_step5_build_cplex_model(i):
    temp_obj_coeff={}
    
    ds5_my_obj.clear()
    ds5_my_colnames.clear()
    ds5_my_ub.clear()
    ds5_my_lb.clear()
    ds5_my_rownames.clear()
    ds5_my_rhs.clear()
    ds5_my_rows.clear()
    
    """ B1: Objective function """
    for b1_key,b1_value in ds5_b1_coeff.items():
        if b1_key in temp_obj_coeff:
            current_value=int(temp_obj_coeff[b1_key])
            temp_obj_coeff[b1_key]=current_value+float(b1_value)
        else:
            temp_obj_coeff[b1_key]=float(b1_value)
            
#   
    """ C1: Cost function """          
    for c1_key,c1_value in ds5_c1_coeff.items():
        if c1_key in temp_obj_coeff:
            current_value=float(temp_obj_coeff[c1_key])
            new_value=current_value-float(c1_value)
            temp_obj_coeff[c1_key]=new_value
        else:
            value=-1*float(c1_value)
            temp_obj_coeff[c1_key]=value 
    

    """ Prepare the final list"""    
    for key,value in temp_obj_coeff.items():    
        ds5_my_obj.append(int(value))  
        ds5_my_colnames.append(key)
     
#     mmm=0
#     for kkk in my_obj:
#         print("My_COLNAME:",my_colnames[mmm], "My_objective", kkk)
#         mmm = mmm+1
                    
    print("------------------------ds5_my_obj i:",i)                
    pprint.pprint(ds5_my_obj)                
    print("------------------------ds5 my_colnames:")                
    pprint.pprint(ds5_my_colnames)                
    
    """Variables Bounds """
    global ds5_my_ctype
    ds5_my_ctype=""
    index=0    
    while index <len(ds5_my_colnames):
        ds5_my_lb.append(0.0)
        ds5_my_ub.append(1.0)
        ds5_my_ctype = ds5_my_ctype+"I"
        index=index+1
    
#     print("my_lb")
#     pprint.pprint(my_lb)
#     print("my_temp_ub")
#     pprint.pprint(my_temp_ub)
#     print("my_ctype")
#     pprint.pprint(my_ctype)

    """ Constraint A1 set"""
    for row in range(Rows):
        for col in range(Cols):
            constrainta_row=[]
            lista_coeff_key=[]
            lista_coeff_value=[]
            ds5_my_rhs.append(ds5_constraintA1_bound[i][row][col])
            identifier="ds5_rowA1["+str(i)+"]["+str(row)+"]["+str(col)+"]"
            ds5_my_rownames.append(identifier)
                
            for key,value in ds5_constraintA1_coeff[i][row][col].items():
                lista_coeff_key.append(key)
                lista_coeff_value.append(value)    
            constrainta_row.append(lista_coeff_key)
            constrainta_row.append(lista_coeff_value)
            ds5_my_rows.append(constrainta_row)
    
    """ Constraint A2 set"""
    for row in range(Rows):
        for col in range(Cols):
            constrainta2_row=[]
            lista2_coeff_key=[]
            lista2_coeff_value=[]
            for n in range (V):
                if i!=n:
                    ds5_my_rhs.append(ds5_constraintA2_bound[i][n][row][col])
                    identifier="ds5_rowA2["+str(i)+"]["+str(n)+"]["+str(row)+"]["+str(col)+"]"
                    ds5_my_rownames.append(identifier)
                        
                    for key,value in ds5_constraintA2_coeff[i][n][row][col].items():
                        lista2_coeff_key.append(key)
                        lista2_coeff_value.append(value)    
                    constrainta2_row.append(lista2_coeff_key)
                    constrainta2_row.append(lista2_coeff_value)
                    ds5_my_rows.append(constrainta2_row)           

    """ Constraint B set"""
    for o in range(objects_number):
        if dwc_step5_check_if_object_is_fixed(i,o)==False:
            identifier="ds5_rowB["+str(i)+"]["+str(o)+"]"
            ds5_my_rownames.append(identifier)
            ds5_my_rhs.append(ds5_constraintB_bound[i][o])
            constraintb_row=[]
            listb_coeff_key=[]
            listb_coeff_value=[]
            for key,value in ds5_constraintB_coeff[i][o].items():
                listb_coeff_key.append(key)
                listb_coeff_value.append(value)    
            constraintb_row.append(listb_coeff_key)
            constraintb_row.append(listb_coeff_value)
            ds5_my_rows.append(constraintb_row)

#     print("My row names with B")
#     pprint.pprint(my_rownames)
#     print("My constraints rows with B")
#     pprint.pprint(my_rows)
#     print("My rhs with B")
#     pprint.pprint(my_rhs)

    """ Constraint C set"""
    for o in range(objects_number):
        if dwc_step5_check_if_object_is_fixed(i,o)==False: 
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            constraintc_row=[]
                            listc_coeff_key=[]
                            listc_coeff_value=[]
                            ds5_my_rhs.append(ds5_constraintC_bound[i][n][o][row][col])
                            identifier="ds5_rowC["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                            ds5_my_rownames.append(identifier)
                            
                            for key,value in ds5_constraintC_coeff[i][n][o][row][col].items():
                                listc_coeff_key.append(key)
                                listc_coeff_value.append(value)    
                            constraintc_row.append(listc_coeff_key)
                            constraintc_row.append(listc_coeff_value)
                            ds5_my_rows.append(constraintc_row)
                                
      

                            
#     print("My row names with C")
#     pprint.pprint(my_rownames)
#     print("My constraints rows with B")
#     pprint.pprint(my_rows)
#     print("My rhs with C")
#     pprint.pprint(my_rhs)
                            
    """ My sense """
    global ds5_my_sense
    ds5_my_sense=""
    index=0
    while index <len(ds5_my_rows):
        ds5_my_sense=ds5_my_sense+"L"
        index=index+1
                    
def dwc_find_benefit_b1(i,x_var,w_var,y_var):
    x_benefit=0
    w_benefit=0
    y_benefit=0
    coef=0
    for o in range(objects_number): 
        for rowD in range(Rows):
            for col in range(Cols):
                coef=0
                for rowS in range(Rows):
                    for m in range(M):
                        req=r[i][o][rowS][m]
                        gain=b[i][o][rowS][rowD][col][m]
                        coef=coef+req*gain
                x_benefit=x_benefit+coef*x_var[i][o][rowD][col]   
                for n in range(V):
                    if n!=i:
                        w_benefit=w_benefit+coef*w_var[i][n][o][rowD][col]
                        y_benefit=y_benefit+coef*y_var[i][n][o][rowD][col]
    
    results={}
    results["benefit"]=x_benefit+w_benefit+y_benefit  
    results["x_benefit"]=x_benefit
    results["w_benefit"]=w_benefit  
    results["y_benefit"]=y_benefit  
                            
    return results

def dwc_find_benefit_b2(i,w_var):
    benefit=0                    
    for o in range(objects_number):
        size=s[o] 
        for row in range(Rows):
            for col in range(Cols):
                for n in range(V):
                    if n!=i:
                        coef=0
                        benefit=psi[i][n][row][col]
                        coef=size*benefit
                        benefit=benefit+coef*w_var[n][i][o][row][col]    
    return benefit

def dwc_find_benefit_b3(i,y_var):
    benefit=0                       
    for i in range(V):
        for o in range(objects_number):
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            coef=0
                            for m in range(M):
                                rate=r[n][o][row][m]
                                benefit=h[i][n][o][row][col]
                                coef=coef+rate*benefit
                            benefit=benefit+y_var[n][i][o][row][col]*coef
    return benefit

def dwc_find_cost_c1(i,x_var,w_var,y_var):
    x_cost=0
    w_cost=0
    y_cost=0
    
    for o in range(objects_number):
        size=s[o] 
        for row in range(Rows):
            for col in range(Cols):
                coef=0
                cost=c[i][row][col]
                coef=size*cost
                x_cost=x_cost+(x_var[i][o][row][col]*coef)    
                for n in range(V):
                    if n!=i:
                    #   w parameters
                        coef=0
                        cost=psi[n][i][row][col]
                        coef=size*cost
                        w_cost=w_cost+(w_var[i][n][o][row][col]*coef)   
                    #   y parameters
                        coef=0
                        cost=h[n][i][o][row][col]
                        coef=cost
                        y_cost=y_cost+(y_var[i][n][o][row][col]*coef)    
    total_cost=x_cost+w_cost+y_cost
    
    results={}
    results["cost"]=total_cost
    results["x_cost"]=x_cost
    results["w_cost"]=w_cost
    results["y_cost"]=y_cost

    return results

def dwc_find_cost_c2(i,w_var):
    """Cost of placing content from CDN n """
    w_cost=0
    for o in range(objects_number):
        size=s[o] 
        for row in range(Rows):
            for col in range(Cols):
                cost=c[i][row][col]
                for n in range(V):
                    if n!=i:
                        coef=0
                        coef=size*cost
                        w_cost=w_cost+w_var[n][i][o][row][col]*coef    
    
    return w_cost

# ******************** Common Solver methods ***********************                     

def dwc_caclulate_net_benefit(x_var,w_var,y_var):
    """ 
        Benefit after Step 4 is: benefit form ds1_x, benefit from ds3_y and benefit from ds4_4 
        Cost after Step 4 is: benefit form ds1_x, benefit from ds3_y and benefit from ds4_4
    """
    total_benefit=0
    total_cost=0
    b1_benefit=0
    b2_benefit=0
    b3_benefit=0
    c1_cost=0
    c2_cost=0
    
    for i in range(V):
        print()
        print("****** Provider:", i)
        b1_results=dwc_find_benefit_b1(i,x_var,w_var,y_var)
        b1_benefit=b1_results["benefit"]
#         b1_x_benefit=float(b1_results["x_benefit"])
#         b1_w_benefit=float(b1_results["w_benefit"])
#         b1_y_benefit=float(b1_results["y_benefit"])
#         print("(b1-x-w-y):",b1_benefit,b1_x_benefit,b1_w_benefit,b1_y_benefit)
        b2_benefit=dwc_find_benefit_b2(i,w_var) 
        b3_benefit=dwc_find_benefit_b3(i,y_var) 
        
        c1_results=dwc_find_cost_c1(i,x_var,w_var,y_var)                               
        c1_cost=c1_results["cost"]
#         c1_x_cost=c1_results["x_cost"]
#         c1_w_cost=c1_results["w_cost"]
#         c1_y_cost=c1_results["y_cost"]
#         print("(c1-x-w-y):",c1_cost,c1_x_cost,c1_w_cost,c1_y_cost)
        c2_cost=dwc_find_cost_c2(i,w_var)
#         print()
#         print("(b1-b2-b3-c1-c2):",b1_benefit,b2_w_benefit,b3_y_benefit,c1_cost,c2_w_cost)
#         print("w3 allocated):",ds3_w_number_allocated)
#         print("y3 allocated):",ds3_y_number_allocated)
#         print("w4 allocated):",ds4_w_number_allocated)
        
        total_benefit=total_benefit+(b1_benefit+b2_benefit+b3_benefit)  
        total_cost=total_cost+c1_cost+c2_cost
                  
    total_net_benefit=total_benefit-total_cost
    
    return total_net_benefit

                            

                            
def populatebyrows(prob,my_obj_param,my_lb_param,my_ub_param,my_ctype_param,my_colnames_param,my_rows_param,my_sense_param,my_rhs_param,my_rownames_param):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.variables.add(obj=my_obj_param, lb=my_lb_param, ub=my_ub_param, types=my_ctype_param,
                       names=my_colnames_param)

    prob.linear_constraints.add(lin_expr=my_rows_param, senses=my_sense_param,
                                rhs=my_rhs_param, names=my_rownames_param)    
def solver(sim_type,slot):
    
    try:
        my_prob = cplex.Cplex()
        if sim_type=="cwc":
            populatebyrows(my_prob,my_obj,my_lb,my_ub,my_ctype,my_colnames,my_rows,my_sense,my_rhs,my_rownames)
        elif sim_type=="nc":
            populatebyrows(my_prob,nc_my_obj,nc_my_lb,nc_my_ub,nc_my_ctype,nc_my_colnames,nc_my_rows,nc_my_sense,nc_my_rhs,nc_my_rownames)
        elif sim_type=="dwc_s3":
            populatebyrows(my_prob,ds3_my_obj,ds3_my_lb,ds3_my_ub,ds3_my_ctype,ds3_my_colnames,ds3_my_rows,ds3_my_sense,ds3_my_rhs,ds3_my_rownames)
        elif sim_type=="dwc_s5":
            populatebyrows(my_prob,ds5_my_obj,ds5_my_lb,ds5_my_ub,ds5_my_ctype,ds5_my_colnames,ds5_my_rows,ds5_my_sense,ds5_my_rhs,ds5_my_rownames)
            
        my_prob.solve()
    except CplexError as exc:
        print(exc)
        return

    print()
    # solution.get_status() returns an integer code
    print("Solution status = ", my_prob.solution.get_status(), ":", end=' ')
    # the following line prints the corresponding string
    print(my_prob.solution.status[my_prob.solution.get_status()])
    net_benefit=my_prob.solution.get_objective_value()
    print("Solution value  = ", net_benefit)
    
    
    
    numcols = my_prob.variables.get_num()
    numrows = my_prob.linear_constraints.get_num()
    slack = my_prob.solution.get_linear_slacks()
    solution_values = my_prob.solution.get_values()

#     for j in range(numrows):
#         print("Rows %d:  Slack = %10f" % (j, slack[j]))
    result_set={}
    for j in range(numcols):
        if solution_values[j]==1.0:
            if sim_type=="cwc":
                result_set[my_colnames[j]]=solution_values[j]
            elif sim_type=="nc":
                result_set[nc_my_colnames[j]]=solution_values[j]
            elif sim_type=="dwc_s3":
                result_set[ds3_my_colnames[j]]=solution_values[j]
            elif sim_type=="dwc_s5":
                result_set[ds5_my_colnames[j]]=solution_values[j]       
            
            
    pprint.pprint(result_set)
    solution={}
    solution["result_set"]=result_set
    solution["net_benefit"]=net_benefit
    
    return solution
    
    
def process_results(sim_type,results_set):
    if sim_type=="cwc":
        for key,value in results_set.items():
            if key[0]=="x" and key[1]=="[":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                o=int(param[2])
                r=int(param[3])
                c=int(param[4])
                x[i][o][r][c]=value
    #             print (key,x[i][o][r][c])
            elif key[0]=="w":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                n=int(param[2])
                o=int(param[3])
                r=int(param[4])
                c=int(param[5])
                w[i][n][o][r][c]=value
    #             print (key,w[i][n][o][r][c])
            elif key[0]=="y":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                n=int(param[2])
                o=int(param[3])
                r=int(param[4])
                c=int(param[5])
                y[i][n][o][r][c]=value
    elif sim_type=="nc":
        for key,value in results_set.items():
            if key[0:4]=="nc_x":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                o=int(param[2])
                r=int(param[3])
                c=int(param[4])
                nc_x[i][o][r][c]=value
    elif sim_type=="dwc_s3":
        for key,value in results_set.items():
            if key[0:5]=="ds3_w":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                n=int(param[2])
                o=int(param[3])
                r=int(param[4])
                c=int(param[5])
                ds3_w[i][n][o][r][c]=value
                ds3_w_number_allocated[i][n]+=1
    #             print (key,ds3_w[i][n][o][r][c])
            elif key[0:5]=="ds3_y":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                n=int(param[2])
                o=int(param[3])
                r=int(param[4])
                c=int(param[5])
                ds3_y[i][n][o][r][c]=value
                ds3_y_number_allocated[i][n]+=1
    #             print (key,ds3_w[i][n][o][r][c])
    elif sim_type=="dwc_s5":
        for key,value in results_set.items():
            if key[0:5]=="ds5_x":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                o=int(param[2])
                r=int(param[3])
                c=int(param[4])
                ds5_x[i][o][r][c]=value
                ds5_x_number_allocated[i]+=1
            if key[0:5]=="ds5_w":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                n=int(param[2])
                o=int(param[3])
                r=int(param[4])
                c=int(param[5])
                ds5_w[i][n][o][r][c]=value
                ds5_w_number_allocated[i][n]+=1
    #             print (key,ds3_w[i][n][o][r][c])
            elif key[0:5]=="ds5_y":
                key1=key.replace("]"," ")
                param=key1.split("[")
                i=int(param[1])
                n=int(param[2])
                o=int(param[3])
                r=int(param[4])
                c=int(param[5])
                ds5_y[i][n][o][r][c]=value
                ds5_y_number_allocated[i][n]+=1
    #             print (key,ds3_w[i][n][o][r][c])

#     pprint.pprint(ds1_x)
#     pprint.pprint(ds3_w)
#     pprint.pprint(ds3_y)
    





def simulator():
    
    initialize_simulator()
    slot=0

    
    while slot<slots_number:
        print (" ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ")
        print ("             slot :",slot)
        print (" ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ")
        
        load_slot_rates(slot)
        
        """ SIMULATION A: Centralized with Collaboration (CWC) """
        sim_type="cwc"
        util_print_new_simtype(sim_type)
        cwc_reset_model_variables()
        cwc_build_model() 
        cwc_build_cplex_model()
        cwc_solution=solver(sim_type,slot)
        
        """ SIMULATION B: Centralized without Collaboration (NC) """

        sim_type="nc"
        util_print_new_simtype(sim_type)
        nc_reset_model_variables()
        nc_build_model()
        nc_build_cplex_model() 
        nc_solution=solver(sim_type,slot)
        process_results(sim_type, nc_solution["result_set"])
        
        """ SIMULATION C: Distributed with Collaboration (DWC) """
        sim_type="dwc"
        util_print_new_simtype(sim_type)
        dwc_step3_reset_model_variables()
        
        
        #  STEP 1: calculate x
        dwc_step1_load_xd_from_nc()
        #  STEP 2: internal structure update
        #  STEP 3: calculate w and y
        sim_type="dwc_s3"
        s3_total_net_benefit=0
        s3_results_sets=[]
        for i in range(V):
            print ("   --- DWC -provider :",i)
            dwc_step3_build_model(i)
            dwc_step3_build_cplex_model(i)
            s3_solution=solver(sim_type,slot)
            s3_results_sets.append(s3_solution["result_set"])
            process_results(sim_type,s3_solution["result_set"])
#             s3_nb=dwc_step3_calculate_net_benefit(i,s3_solution["result_set"])
#             s3_total_net_benefit=s3_total_net_benefit+s3_nb
            
            s3_total_net_benefit=dwc_caclulate_net_benefit(ds1_x,ds3_w,ds3_y)
        print ("Distributed total net benefit:")
        print (s3_total_net_benefit)
        
        
        #  STEP 4: solve conflicts for w
        dwc_step4_solve_storage_violations(s3_results_sets)
        s4_total_net_benefit=dwc_caclulate_net_benefit(ds1_x,ds4_w,ds3_y)
        dwc_s4_update_variables_values()
#         file = open("results.txt","a")
#         s1="\n    cwc:"+str(cwc_solution["net_benefit"])
#         s2="\n     nc:"+str(nc_solution["net_benefit"])
#         s3="\n dwc_s3:"+str(s3_total_net_benefit)
#         s4="\n dwc_s4:"+str(s4_total_net_benefit)
#         message="-slot-"+str(slot) + s1 + s2 + s3 + s4
#         
#         print (message)
#         
#         
#         file.write(message)
#         message="\n"
#         file.write(message)
#         file.close()
        
        #  STEP 5: run again optimization
        
        #  Build Optimization
        # B1+B2+B3-C1-C2, s.t. A,B,C plus following constraints:
        # constraint D, that was requested must remain-new : 1<=x<=1
        # Constraint A: bounds must be updated, based on what n advertised in the previous step
        sim_type="dwc_s5"
        s5_total_net_benefit=0
        s5_results_sets=[]
        dwc_step5_reset_variables()
        dwc_step5_fix_requested_x()
        dwc_step5_fix_requested_y()
        
        for i in range(V):
            dwc_step5_build_model(i)
            dwc_step5_build_cplex_model(i)
            s5_solution=solver(sim_type,slot)
            s5_results_sets.append(s5_solution["result_set"])
            process_results(sim_type,s5_solution["result_set"])
            
        s5_total_net_benefit=dwc_caclulate_net_benefit(ds5_x,ds5_w,ds5_y)
            
        s1="\n    cwc:"+str(cwc_solution["net_benefit"])
        s2="\n     nc:"+str(nc_solution["net_benefit"])
        s3="\n dwc_s3:"+str(s3_total_net_benefit)
        s4="\n dwc_s4:"+str(s4_total_net_benefit)
        s5="\n dwc_s5:"+str(s5_total_net_benefit)
        
        message="-slot-"+str(slot) + s1 + s2 + s3 + s4+s5
        print (message)
        
        slot=slot+1
        
        
       
        
def util_print_new_simtype(sim_type):
    print()    
    print()
    
    if sim_type=="cwc":
        print (" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
        print ("   -- SIMULATION A: Centralized with Collaboration (CWC)  --")
        print (" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
    elif sim_type=="nc":
        print (" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
        print ("   -- SIMULATION B: Centralized without Collaboration (NC)  --")
        print (" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
    elif sim_type=="dwc":
        print (" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
        print ("   -- SIMULATION C: Distributed with Collaboration (DWC) --")
        print (" %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ")
    print()
   
        
if __name__ == "__main__":
    simulator()