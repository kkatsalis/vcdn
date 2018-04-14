import pprint

#***** Example******
# V=1
# Objects=10
# k=[[0 for i in range(V)] for o in range(Objects)] 
# for i in range(Objects):
#     for j in range(V): 
#         k[i][j]="k"+str(i)+","+str(j)
# pprint.pprint (k)

#  B1 coefficients
V=1
M=2
Objects=2
Row=2
Col=2

# Defines request rate r[i][o][row][m]
r=[[[[0 for m in range(M)]for row in range(Row)] for o in range(Objects)] for i in range(V)] 
# Defines b[i][o][row][col][m]   
b=[[[[[0 for m in range(M)] for col in range(Col)] for row in range(Row)] for o in range(Objects)] for i in range(V)]    
# Defines solution_values[i][o][row][col]   
solution_values=[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Objects)] for i in range(V)] 
# x_names[i][o][row][col]
x_names=[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Objects)] for i in range(V)] 
# Defines w[i][n][o][row][col]   
w=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Objects)] for n in range(V)]for i in range(V)] 
# Defines w_names[i][n][o][row][col]
w_names=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Objects)] for n in range(V)]for i in range(V)] 
# Defines y[i][n][o][row][col]   
y=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Objects)] for n in range(V)]for i in range(V)] 
# y_names[i][n][o][row][col]
y_names=[[[[[0 for col in range(Col)] for row in range(Row)] for o in range(Objects)] for n in range(V)]for i in range(V)] 

# Defines c[i][row][col] unit cost    
c=[[[0 for col in range(Col)] for row in range(Row)] for i in range(V)] 
# Defines s[o] size of object o   
s=[0 for o in range(Objects)]
# Defines s[i][r][c] size of available storage in row r and column c for cdn i   
sirc=[[[0 for col in range(Col)] for row in range(Row)] for i in range(V)]
# Defines constraintA_bound[i][row][col]
constraintA_bound=[[[5+col*5 for col in range(Col)] for row in range(Row)] for i in range(V)]
# Defines constraintA_coeff[i][row][col]
constraintA_coeff=[[[0 for col in range(Col)] for row in range(Row)] for i in range(V)]
# Defines constraintB_bound[i][o]
constraintB_bound=[[1 for o in range(Objects)] for i in range(V)]
# Defines constraintB_coeff[i][o]
constraintB_coeff=[[0 for o in range(Objects)] for i in range(V)]


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

# s[o]:  Objects size
s[0]=5
s[1]=10

# c[i][row][col] COST
c[0][0][0]=2
c[0][0][1]=1
c[0][1][0]=4
c[0][1][1]=2


# ****************************** # 
#      X Names                 *
# ****************************** # 

# x_names[i][o][row][col]
index=0
for i in range(V):
    for o in range(Objects): 
        for row in range(Row):
            for col in range(Col):
                x_names[i][o][row][col]="solution_values["+str(i)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                index=index+1
# print("X names")              
# pprint.pprint(x_names)                

# ****************************** # 
#      W Names                 *
# ****************************** # 
# w_names[i][n][o][row][col]
index=0
for i in range(V):
    for n in range(V):
        for o in range(Objects): 
            for row in range(Row):
                for col in range(Col):
                    w_names[i][n][o][row][col]="w["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1
# print("W names")              
# pprint.pprint(w_names)

# ****************************** # 
#      Y Names                 *
# ****************************** # 
# y_names[i][n][o][row][col]
index=0
for i in range(V):
    for n in range(V):
        for o in range(Objects): 
            for row in range(Row):
                for col in range(Col):
                    y_names[i][n][o][row][col]="y["+str(i)+"]["+str(n)+"]["+str(o)+"]["+str(row)+"]["+str(col)+"]"
                    index=index+1
# print("Y names")              
# pprint.pprint(y_names)                

# ****************************** # 
#       B1:  Benefit           *
# ****************************** # 
b1_coeff={}
for i in range(V):
    for o in range(Objects): 
        for row in range(Row):
            for col in range(Col):
                coef=0
                for m in range(M):
                    req=r[i][o][row][m]
                    gain=b[i][o][row][col][m]
                    coef=coef+(req*gain)
                key=x_names[i][o][row][col]    
                b1_coeff[key]=str(coef)    

print("--- B1 Gain coefficients ---")              
pprint.pprint(b1_coeff)

# ****************************** # 
# C1:  Cost of placement *
# ****************************** # 

c1_coeff={}
for i in range(V):
    for o in range(Objects):
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


# *********************************** # 
# Constraint A:  Capacity constraints
# *********************************** # 

# constraintA_bound[i][row][col]
# constraintA_coeff[i][row][col]

for i in range(V):
    for row in range(Row):
        for col in range(Col):
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

print("--- constraintA_Bounds --- ")
pprint.pprint(constraintA_bound)
                         
print("--- constraintA_coeff --- ")
pprint.pprint(constraintA_coeff)

# *********************************** # 
# Constraint B:  Store only in one place contraint
# *********************************** # 
# w[i][n][o][row][col]
# y[i][n][o][row][col]

# constraintB_bound[i][o]
# constraintB_coeff[i][o]


for i in range(V):
    for o in range(Objects):
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