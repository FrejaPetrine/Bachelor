
import pulp
dir(pulp)

# define variable
x = pulp.LpVariable('x',lowBound=0)
y = pulp.LpVariable('y',lowBound=0)

# Objektfunktion
max_z = pulp.LpProblem("maximer_Z",pulp.LpMaximize)
max_z += 5*x + 10*y

# Bibetingelser
max_z += 1*x +2*y <= 120
max_z += x + y >= 60
max_z += x - 2*y >= 0

# previe
print(max_z)

# Check
print(pulp.LpStatus[max_z.status])

#Solve
max_z.solve()

#Få variabler
print(x.varValue)
print(y.varValue)

for var in max_z.variables():
    print(var.name,"==>",var.varValue)

max_z

# få den optimale value
print(pulp.value(max_z.objective))