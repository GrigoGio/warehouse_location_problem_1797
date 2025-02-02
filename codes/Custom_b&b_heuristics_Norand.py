#Grigoraskos Giwrgos 1797
from collections import deque
import numpy as np
import random
from gurobipy import Model, GRB
import time
import math
import winsound


def load_problem_data(file_name):

    with open(file_name, "r") as file:
        data = file.read()
        problem_data = {}
        exec(data, {}, problem_data)  # data to dictionary
        return problem_data

def fixed_cost_efficiency_greedy(warehouses, stores, fixed_cost, capacity, supply_cost):
    print("greedy start")
    #calculate cost-efficiency(warehouse)
    efficiency = {i: fixed_cost[i] / capacity[i] for i in warehouses}

    #short by efficency
    sorted_warehouses = sorted(warehouses, key=lambda i: efficiency[i])

    #solution variables
    X = {i: 0 for i in warehouses}  # 0 no warehouse 1 open warehouse
    Y = {(i, j): 0 for i in warehouses for j in stores}  #store assignment
    remaining_capacity = {i: capacity[i] for i in warehouses}  #remaining warehouse capacity
    assigned_warehouses = {j: None for j in stores}  #warehouse a store is assigned to
    total_cost = 0 

    #assign stores-warehouses greedy
    for j in stores:
        best_warehouse = None
        best_cost = float('inf')

        #put store j in cheapest warehouse j
        for i in sorted_warehouses:
            if remaining_capacity[i] > 0 and supply_cost[i, j] < best_cost:
                best_warehouse = i
                best_cost = supply_cost[i, j]

        # assignment
        if best_warehouse is not None:
            X[best_warehouse] = 1
            Y[best_warehouse, j] = 1
            remaining_capacity[best_warehouse] -= 1
            assigned_warehouses[j] = best_warehouse
            total_cost += best_cost 
        else: 
            print("Problem has no solutions,**capacity contrains**") 
            exit()  

    #+opeening costs
    total_cost += sum(fixed_cost[i] for i in warehouses if X[i] == 1)
    print("greedy end")
    return total_cost, X, Y

def custom_branch_and_bound(warehouses, stores, fixed_cost, capacity, supply_cost):
    #heuristic smart branching depth######
    proon_depth=0.04*(len(warehouses)*len(stores))**0.4
    if proon_depth>4:proon_depth=5 #xlarge 
    elif proon_depth>3: proon_depth = 4 #medium/large
    else: proon_depth = 3 #small
    print("proon_depth= ",proon_depth)

    if proon_depth==3:print("DFS")    
    else:print("BFS")
    # Heuristic upper bound (greedy)
    upper_bound, best_X, best_Y = fixed_cost_efficiency_greedy(warehouses, stores, fixed_cost, capacity, supply_cost)

    ####Initialize stack
    stack = deque()  
    best_solution = {"objective": upper_bound, "X": best_X, "Y": best_Y }
    root_node = {
        "fixed_vars": {}, 
        "depth": 0      
    }
    stack.append(root_node)

    #Gurobi
    def solve_relaxed_problem(fixed_vars):

        model = Model("Relaxation")
        model.setParam("OutputFlag", 0) #no guorobi spamm

        #decision variables #######################3
        X = {i: model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1, name=f"X[{i}]") 
             for i in warehouses}
        Y = {(i, j): model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1, name=f"Y[{i},{j}]") 
             for i in warehouses for j in stores}
        
        #fixed variables(if any)#######################4
        for var, value in fixed_vars.items():
            if var.startswith("X"):
                i = int(var.split("[")[1][:-1])
                X[i].lb = X[i].ub = value
            elif var.startswith("Y"):
                i, j = map(int, var.split("[")[1][:-1].split(","))
                Y[i, j].lb = Y[i, j].ub = value

        model.setObjective(
            sum(fixed_cost[i] * X[i] for i in warehouses) +
            sum(supply_cost[i, j] * Y[i, j] for i in warehouses for j in stores),
            GRB.MINIMIZE
        )

  
        for i in warehouses:######################2
            model.addConstr(sum(Y[i, j] for j in stores) <= capacity[i] * X[i])
        for j in stores:
            model.addConstr(sum(Y[i, j] for i in warehouses) == 1)
        for i in warehouses: ###logical
            for j in stores:
                model.addConstr(Y[i, j] <= X[i])

        model.optimize()
        if model.status == GRB.OPTIMAL:
            return (model.ObjVal, {var.VarName: var.X for var in model.getVars()})  
        else :return (None, None)

    #branch & bound
    while stack:
        depth_flag=False
        depth_flag99=False
        check_timer = time.time()  #end timer
        if (check_timer - start_time)>600:
            print("T ",end="")
            print("\ntime limit reached",end="")
            break
        #heuristic dfs or bfs based on how hard the problem is
        if proon_depth==3:current_node=stack.pop()    
        else:current_node =stack.popleft()
        fixed_vars = current_node["fixed_vars"]


        
        relaxed_obj, solution = solve_relaxed_problem(fixed_vars)########################2
        
        
        if relaxed_obj is None or relaxed_obj >= best_solution["objective"]:
            print("P ",end="")
            continue  #proon
    

        is_integer = True
        fractional_var = None
        max_cost_impact = -float('inf')
        counter=0
        for var, value in solution.items():#Find the most costly from the fisrt 300
            if counter==300 and is_integer == False: ####heuristic
                break
            counter+=1
            if not np.isclose(value, round(value), atol=1e-5):
                is_integer = False

                if var.startswith("X"):
                    i = int(var.split("[")[1][:-1])
                    cost_impact = fixed_cost[i]
                elif var.startswith("Y"):
                    i, j = map(int, var.split("[")[1][:-1].split(","))
                    cost_impact = supply_cost[i, j]
                else:
                    continue

                if cost_impact > max_cost_impact:
                    max_cost_impact = cost_impact
                    fractional_var = var  # Store highest impact variable

        if is_integer:
            best_solution = {"objective": relaxed_obj, "solution": solution,} 
            print("S ",end="")       
            continue

        
        #print(f"{ relaxed_obj:.0f},{ best_solution['objective']:.0f}")
        print(f"{relaxed_obj/best_solution['objective']*100:.2f}","%",end="  ")

        #if problem l or xl just look for good solution
        
        if relaxed_obj/best_solution['objective']*100>=99.98 :
            depth_flag99=True
            print("F99.99%  ",end="")
            break   
        
        #Proon if too deep and we have acceptable solution
        elif current_node["depth"]>=proon_depth and relaxed_obj/best_solution['objective']*100>=250/proon_depth: #83/62/50
            #if current_node["depth"]>proon_depth*2: proon_depth=2*proon_depth #solution is propably deep
            #else: proon_depth=current_node["depth"]
            depth_flag=True
            dd_flag=True
            print("D ",end="")
            continue

        #proon if too deep and we have a bad branch
        elif current_node["depth"]>=proon_depth*2 and relaxed_obj/best_solution['objective']*100>=180/proon_depth:#60/45/36
            depth_flag=True
            print("DD ",end="")
            continue 
        
        #branch
        left_branch = {"fixed_vars": {**fixed_vars, fractional_var: 0}, "depth": current_node["depth"] + 1}
        right_branch = {"fixed_vars": {**fixed_vars, fractional_var: 1}, "depth": current_node["depth"] + 1}

        stack.append(left_branch)
        stack.append(right_branch)
    if depth_flag :print("\nmax depth limi reached:",proon_depth,end="")
    elif depth_flag99 :print("\n99.99% ","reached",end="")
    return best_solution

if __name__ == "__main__":
    print("****B&B with heuristics****")

    data_file = "supply_cost_data.txt"
    problem_data = load_problem_data(data_file)
    if problem_data==None:
        print("Error proccessing data")
        exit()

    else:
        
        warehouses = problem_data["warehouses"]
        stores = problem_data["stores"]
        fixed_cost = problem_data["fixed_cost"]
        capacity = problem_data["capacity"]
        supply_cost = problem_data["supply_cost"]
        print("data loaded W= %d S= %d" % (len(warehouses), len(stores)))

    '''
        
    warehouses = [0, 1, 2]
    stores = [0, 1, 2, 3]
    fixed_cost = {0: 500, 1: 600, 2: 700}
    capacity = {0: 2, 1: 2, 2: 3}
    np.random.seed(42)  # Set a fixed seed for reproducibility

    supply_cost = {(i, j): np.random.randint(50, 150) for i in warehouses for j in stores}
     '''
    start_time = time.time() 

    best_solution= custom_branch_and_bound(warehouses, stores, fixed_cost, capacity, supply_cost)
    end_time = time.time()
    print("\n****B&B with heuristics****",end="")
    print("\nKey:",problem_data["supply_cost"][0, 0])
    

    print(f"Execution Time: {end_time - start_time:.4f} seconds")
    if best_solution== None:
        print("Error solving the problem")
    else:
        print("Best Solution:" ,best_solution["objective"])
    
    winsound.Beep(300, 700)#(Hz,milliseconds)
    winsound.Beep(220, 700)#(Hz,milliseconds)