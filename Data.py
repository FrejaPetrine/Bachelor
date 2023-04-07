from pulp import *

# Define the problem
prob = LpProblem("Production Planning", LpMinimize)

# Define the decision variables
products = ['Product 1', 'Product 2']
time_periods = ['Week 1', 'Week 2', 'Week 3']
production = LpVariable.dicts("production", (products, time_periods), lowBound=0, cat='Integer')
inventory = LpVariable.dicts("inventory", (products, time_periods), lowBound=0, cat='Integer')
sales = LpVariable.dicts("sales", (products, time_periods), lowBound=0, cat='Integer')

# Define the production costs
prod_cost = {'Product 1': 50, 'Product 2': 70}

# Define the demand
demand = {'Product 1': [100, 150, 200], 'Product 2': [80, 120, 150]}

# Define the objective function
prob += lpSum([prod_cost[p]*production[p][t] + 70*production[p][t+1] + 10*inventory[p][t] + 5*(production[p][t]>0) + 8*(production[p][t+1]>0) for p in products for t in time_periods[:-1]])

# Define the constraints
for t in time_periods[:-1]:
    # Inventory balance constraint
    prob += inventory['Product 1'][t] + production['Product 1'][t] == inventory['Product 1'][t+1] + sales['Product 1'][t] + 2*production['Product 1'][t+1] + 5*production['Product 2'][t+1] + 20
    prob += inventory['Product 2'][t] + production['Product 2'][t] == inventory['Product 2'][t+1] + sales['Product 2'][t] + 3*production['Product 1'][t+1] + 2*production['Product 2'][t+1] + 12
    # Production capacity constraint
    prob += production['Product 1'][t] <= 5
    prob += production['Product 2'][t] <= 4
    # Sales constraint
    prob += sales['Product 1'][t] <= demand['Product 1'][t]
    prob += sales['Product 2'][t] <= demand['Product 2'][t]

# Initial inventory constraint
prob += inventory['Product 1']['Week 1'] == 0
prob += inventory['Product 2']['Week 1'] == 0

# Solve the problem
prob.solve()

# Analyze the solution
print("Status:", LpStatus[prob.status])
print("Optimal Solution:")
for v in prob.variables():
    print(v.name, "=", v.varValue)
print("Total Cost =", value(prob.objective))

prob += pulp.lpSum(upc*Xt[i] for i in t[1:])+pulp.lpSum(uhc*It[i] for i in t[1:])+pulp.lpSum(fc*Yt[i] for i in t[1:])
