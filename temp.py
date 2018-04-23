for o in range(Objects):
        if dwc_object_is_placed_in_xd(i,o)==False: 
            for row in range(Rows):
                for col in range(Cols):
                    for n in range(V):
                        if n!=i:
                            ds3_constraintC_coeff[i][n][o][row][col]={}
                            ds3_y_key=ds3_y_names[i][n][o][row][col]
                            (ds3_constraintC_coeff[i][n][o][row][col])[ds3_y_key]=1   
                            
     for n in range(V):
        for o in range (Objects):
            for row in range (Rows):
                for col in range (Cols):
                    ds3_constraintC_bound[i][n][o][row][col]=ds1_x[n][o][row][col]
                            
                            
                            
                            
    