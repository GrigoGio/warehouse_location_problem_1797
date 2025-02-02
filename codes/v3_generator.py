#Grigoraskos Giwrgos 1797
import numpy as np  

num_warehouses =30   # <------ Number of warehouses
num_stores = 100# <----- Number of stores
min_cost = 20
max_cost = 50
min_fixed_cost = 100  
max_fixed_cost = 1000  
min_capacity = 5 
max_capacity = 10  
output_file = "supply_cost_data.txt"

#generate ID (0num-1)
warehouses = list(range(num_warehouses))  
stores = list(range(num_stores))  # Now starts from 0

# cost matrix
cost_matrix = np.random.randint(min_cost, max_cost + 1, size=(num_warehouses, num_stores))

#fixed cost and capacities dictionary 
fixed_cost = {i: np.random.randint(min_fixed_cost, max_fixed_cost + 1) for i in range(num_warehouses)}
capacity = {i: np.random.randint(min_capacity, max_capacity + 1) for i in range(num_warehouses)}

# supply cost matrix to dictionary
cost_dict = {
    (i, j): cost_matrix[i][j]
    for i in range(num_warehouses)
    for j in range(num_stores)
}
with open(output_file, "w") as file:
    file.write(f"warehouses = {warehouses}\n")
    file.write(f"stores = {stores}\n\n")
    file.write("supply_cost = {\n")
    first = True
    for (warehouse, store), cost in cost_dict.items():
        if not first:
            file.write(",\n")  #comma and nl before all but first
        file.write(f"    ({warehouse}, {store}): {cost}")
        first = False 
    file.write("}\n\n")
    
    file.write(f"fixed_cost = {fixed_cost}\n")
    file.write(f"capacity = {capacity}\n\n")
    file.write(f"num_stores = {num_stores}\n")
    file.write(f"num_warehouses = {num_warehouses}\n")

print(f"Random supply cost, fixed cost, and capacity data saved to {output_file}.")

# Sanity check 
if num_warehouses * max_capacity < num_stores:
    print("ERROR: values won't work")
elif num_warehouses * min_capacity < num_stores:
    print("CAUTION: values may not work")
else:
    print("SUCCESS: values will work")
 