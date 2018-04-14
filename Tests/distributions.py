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
global Row 
Row=1
# Columns of the Grid
global Col
Col=2

global slots_number
slots_number=3


popularity_weights=[0 for o in range(Objects)]
rate=[[[[0 for m in range(M)]for row in range(Row)] for o in range(Objects)] for i in range(V)] 

zipf_parameter = 2.5
zipf_object_popularity=np.random.zipf(zipf_parameter,Objects)
popularity_list=zipf_object_popularity.tolist()
popularity_list_sum=sum(popularity_list) 

for i in range(Objects):
    popularity_weights[i]=popularity_list[i]/popularity_list_sum

# pprint.pprint(popularity_list)
# print("sum",popularity_list_sum)    
pprint.pprint(popularity_weights)

slot_r=[]

for i in range(V):
    for row in range(Row):
        for m in range(M):
            print("i-row-m:",i,row,m)

            requests_array=np.random.poisson(10+m,slots_number)
            requests=requests_array.tolist()
            pprint.pprint(requests)
            for slot in range(slots_number):
                print("***** slot :",slot)
                for o in range(Objects):
                    rate[i][o][row][m]=int(round(requests[slot]*popularity_weights[o]))
                    print("R :",rate[i][o][row][m])
#                 slot_r.append("slot")
                slot_r.append(rate)
print()
pprint.pprint(slot_r)    


# for s in range(slots_number):
#    
#         for o in range(Objects): 
#             
                
                
                
