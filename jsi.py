import pulp
dir (pulp)
import json
import numpy as np
import matplotlib.pyplot as plt

with open('Alt_data.json', 'r') as openfile:
    json_data = json.load(openfile)
#Data
produkt_navn = json_data['produkter']
t = json_data['tidsperioder']
ed = json_data['efterspørgsel']
epo = json_data['produktion_omkostninger'] #Enheds produktions omkostninger
elo = json_data['lager_omkostninger']#Enheds lager omkostninger
mL = json_data['mindste_lager']
mP = json_data['mindste_produktion']
b = json_data['batch']
l = json_data['lead_time']
r = json_data['r']
sL = json_data["start_lager"]
f = json_data["fixed_cost"]

produkt = range(0, len(produkt_navn))
t = range(0, len(t))

#Beregning af bigM
d_sum = [0]
for recept in range(0, len(ed)):
    for tal in range(0, len(ed[recept])):
        d_sum[recept] += ed[recept][tal]
    d_sum.append(0)
bigM = max(sum(d_sum),max(mP))
print("bigM",bigM)

#Problemet
prob = pulp.LpProblem('minimer omk', pulp.LpMinimize)

#Variabler
Xt = pulp.LpVariable.dicts("produceret",(produkt,t),lowBound=0,cat=pulp.LpInteger)
It = pulp.LpVariable.dicts("lager",(produkt,t),lowBound=0,cat="Continuous")
Yt = pulp.LpVariable.dicts("maskine_start",(produkt,t),lowBound=0, upBound=1,cat=pulp.LpBinary)

#Objekt funktion
prob += pulp.lpSum([epo[i]*b[i]*Xt[i][j] + elo[i]*It[i][j] + f[i]*Yt[i][j] for i in produkt for j in t])

#Bibetingelser
for i in produkt:
    It[i][-1] = mL[i]

Xt[0][-1] = 4

for i in produkt:
    for j in t:
        prob += (b[i]*Xt[i][j-l[i]] + It[i][j - 1] - It[i][j]) >= ed[i][j] + sum(b[l]*r[l][i]*Xt[l][j] for l in produkt)  # lager balance

for i in produkt:
    for j in t:
        prob += Yt[i][j]*bigM >= Xt[i][j] #at Yt slår ud som en når der produceres
        prob += It[i][j] >= mL[i]  # Mindste lager
        prob += Xt[i][j] >= Yt[i][j] * mP[i]  # Mindste produktion




prob.solve(pulp.PULP_CBC_CMD(maxSeconds=20))
print("solution status = ",pulp.LpStatus[prob.status])


for v in prob.variables():
    if v.varValue>=0:
        print(v.name, "=", v.varValue)


print('Optimal cost is:', pulp.value(prob.objective))
# Number of periods - used to control placement on the x-axis
numPeriods = len(t)
# Position of bars on x-axis
pos = np.arange(numPeriods)

#Plottet
plt.figure(1)
    # For hvert produkt, plot produktionsplanen
for k in produkt:
    plt.subplot(len(produkt), 1, k+1)
    # Extract the optimal variable values
    lager_values = [It[k][j].varValue for j in t]
    produktion_values = [b[k]*Xt[k][j].varValue for j in t]
    demands = [ed[k][j] + sum(b[l]*r[l][k]*Xt[l][j].varValue for l in produkt) for j in t]
    print(f"Demands of product {k} =",demands)
    # Width of a bar
    width = 0.4
    # Add the three plots to the fig-figure
    plt.bar(pos, demands, width, label='Efterspørgsel '+ produkt_navn[k], color='blue')
    plt.bar(pos + width, lager_values, width, label='Inventory level', color='grey')
    plt.plot(pos, produktion_values, color='darkred', label='Production level')
    # Set the ticks on the x-axis
    plt.xticks(pos + width / 2, t) #Gør noget her
    # Labels on axis
    plt.xlabel('Periods to plan')
    plt.ylabel('Demand')
    plt.legend()
    plt.ylim(0, max(max(produktion_values),max(lager_values))+max(max(produktion_values),max(lager_values))/10)
    # Create a vertical scroll bar
    '''
    vscrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.get_tk_widget().yview)
    vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
'''

# Labels for akserne
plt.xlabel('Periods to plan')
plt.ylabel('Demand')

plt.show()