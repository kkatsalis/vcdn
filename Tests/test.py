
key='y[18][9990][16][0][1]'

if key[0]=="y":
    key1=key.replace("]"," ")
    param=key1.split("[")
    print(param)
    i=int(param[1])
    n=int(param[2])
    o=int(param[3])
    r=int(param[4])
    c=int(param[5])
    
    print("i:",i)
    print("n:",n)
    print("o:",o)
    print("r:",r)
    print("c:",c)
    
