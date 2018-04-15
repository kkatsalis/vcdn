import scipy
import numpy as np
import pprint
from scipy.stats import zipf
from builtins import range


# CDN providers
global V 
V=1
# Mobile operators
global M
M=1
# Objects
global Objects  
Objects=5
# Rows of the Grid
global Rows 
Rows=2
# Columns of the Grid
global Cols
Cols=2

global slots_number
slots_number=3


pw=[0 for o in range(Objects)]
sim_r=[[[[[0 for m in range(M)]for row in range(Rows)] for o in range(Objects)] for i in range(V)] for s in range(slots_number)]

zipf_parameter = 2.5
zipf_object_popularity=np.random.zipf(zipf_parameter,Objects)
popularity_list=zipf_object_popularity.tolist()
popularity_list_sum=sum(popularity_list) 

for i in range(Objects):
    pw[i]=popularity_list[i]/popularity_list_sum

# pprint.pprint(popularity_list)
# print("sum",popularity_list_sum)    
pprint.pprint(pw)

for i in range(V):
    for row in range(Rows):
        for m in range(M):
            print("i-row-m:",i,row,m)

            requests_array=np.random.poisson(10+m,slots_number)
            sim_requests=requests_array.tolist()
            pprint.pprint(sim_requests)
            for slot in range(slots_number):
                print("***** slot :",slot)
                for o in range(Objects):
                    sim_r[slot][i][o][row][m]=int(round(sim_requests[slot]*pw[o]))
                    print("R :",sim_r[slot][i][o][row][m])
#                 slot_r.append("slot")
            
print()
pprint.pprint(sim_r)    


# for s in range(slots_number):
#    
#         for o in range(Objects): 
#             
                
                
                
