#Grigoraskos Giwrgos 1797
import pyomo.environ as pyomo
import time
import winsound



def load_problem_data(file_name):

    with open(file_name, "r") as file:
        data = file.read()

        problem_data = {}
        exec(data, {}, problem_data)   # data to dictionary
        return problem_data

data_file = "supply_cost_data.txt"
problem_data = load_problem_data(data_file)
warehouses = problem_data["warehouses"]# Extract data
stores = problem_data["stores"]
fixed_cost = problem_data["fixed_cost"]
capacity = problem_data["capacity"]
supply_cost = problem_data["supply_cost"]
start_time = time.time()  # Start timer

# ------------initialize the model------------------------------

model = pyomo.ConcreteModel()


# define the variables
model.X = pyomo.Var(warehouses, domain=pyomo.Binary)  # 1-> warehouse open
model.Y = pyomo.Var(warehouses, stores, domain=pyomo.Binary)  # 1 ->warehouse i supplies store j 

# define the constraints#################

# capacity
def capacity_constraint(model, i):
    return sum(model.Y[i, j] for j in stores) <= capacity[i] * model.X[i]
model.capacity_constraint = pyomo.Constraint(warehouses, rule=capacity_constraint)

# single store assignment
def assignment_constraint(model, j):
    return sum(model.Y[i, j] for i in warehouses) == 1
model.assignment_constraint = pyomo.Constraint(stores, rule=assignment_constraint)

# Logical constraint
def logical_constraint(model, i, j):
    return model.Y[i, j] <= model.X[i]
model.logical_constraint = pyomo.Constraint(warehouses, stores, rule=logical_constraint)

# define the objective function#################

def objective_function(model):
    return sum(fixed_cost[i] * model.X[i] for i in warehouses) + \
           sum(supply_cost[i, j] * model.Y[i, j] for i in warehouses for j in stores)
model.obj = pyomo.Objective(rule=objective_function, sense=pyomo.minimize)

solver = pyomo.SolverFactory('gurobi')

results = solver.solve(model, tee=False)
end_time = time.time()  # End timer

'''
# Output results
print("-----Printing the model-----")
model.pprint()

print("-----Printing the results-----")
print(results)

print("-----Printing the values of the optimal solution-----")
for i in warehouses:
    for j in stores:
        if model.Y[i, j]() > 0.05:
            print(f"Store {j} is assigned to Warehouse {i}")
'''
print("####Solved with Pyomo####")
#print("data loaded W= %d S= %d" % (len(warehouses), len(stores)))
print("key: ",problem_data["supply_cost"][0, 0])    # Output the results
print(f"Execution Time: {end_time - start_time:.4f} seconds")
print("Total cost : ", model.obj())
winsound.Beep(220, 700)#(Hz,milliseconds)
winsound.Beep(300, 700)#(Hz,milliseconds)

