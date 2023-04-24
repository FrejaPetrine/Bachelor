import pulp
dir (pulp)
import json
import numpy as np
import matplotlib.pyplot as plt
import os

license_path = "/Users/frejaandersen/gurobi.lic"
path_to_gurobi = "/Library/gurobi1001/macos_universal2/bin/gurobi_cl"

solver = pulp.GUROBI_CMD(path=path_to_gurobi, timeLimit=20, logPath='/Users/frejaandersen/gurobi.log')

os.environ["GRB_LICENSE_FILE"] = license_path

with open('Data.json', 'r') as openfile:
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
It = pulp.LpVariable.dicts("lager",(produkt,t),lowBound=0,cat=pulp.LpContinuous)
Yt = pulp.LpVariable.dicts("maskine_start",(produkt,t),lowBound=0, upBound=1,cat=pulp.LpBinary)

#Objekt funktion
prob += pulp.lpSum([epo[i]*b[i]*Xt[i][j] + elo[i]*It[i][j] + f[i]*Yt[i][j] for i in produkt for j in t])

#Bibetingelser
for i in produkt:
    It[i][-1] = sL[i]

Xt[0][-1] = 3
Xt[11][-1] = 3
Xt[15][-1] = 3
Xt[23][-1] = 3
Xt[31][-1] = 2
Xt[37][-1] = 4
Xt[41][-1] = 3



'''
for i in produkt:
    if False:
        for j in t:
            if i == 0:
                prob += (b[i] * Xt[i][j - l[i]]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance
            if i == 11:
                prob += (b[i] * Xt[i][j - l[i]]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance
            if i == 15:
                prob += (b[i] * Xt[i][j - l[i]]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance
            if i == 23:
                prob += (b[i] * Xt[i][j - l[i]]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance
            if i == 31:
                prob += (b[i] * Xt[i][j - l[i]]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance
            if i == 37:
                prob += (b[i] * Xt[i][j - l[i]]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance
            if i == 41:
                prob += (b[i] * Xt[i][j - l[i]]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance
            else:
                prob += (b[i] * Xt[i][j - l[i]] + It[i][j - 1] - It[i][j]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance

'''

for i in produkt:
    for j in t:
        prob += (b[i] * Xt[i][j - l[i]] + It[i][j - 1] - It[i][j]) == ed[i][j] + sum(b[l] * r[l][i] * Xt[l][j] for l in produkt)  # lager balance
#for i in {0, 11, 15, 23, 31, 37, 41}:
    #for j in t:
       # prob += It[i][j] <= 0

for i in produkt:
    for j in t:
        prob += Yt[i][j]*bigM >= Xt[i][j] #at Yt slår ud som en når der produceres
        prob += It[i][j] >= mL[i]  # Mindste lager
        prob += Xt[i][j] >= Yt[i][j] * mP[i]  # Mindste produktion

for i in produkt:
    for j in t:
        prob += Xt[0][j]+Xt[11][j]+Xt[15][j]+Xt[23][j]+Xt[31][j]+Xt[37][j]+Xt[41][j] <= 4

prob.solve(solver)

with open('/Users/frejaandersen/gurobi.log', "r") as log_file:
    log_content = log_file.read()
    print(log_content)


print("solution status = ", pulp.LpStatus[prob.status])

for v in prob.variables():
    if v.varValue>=0:
        print(v.name, "=", v.varValue)




print('Optimal cost is:', pulp.value(prob.objective))
# Number of periods - used to control placement on the x-axis
numPeriods = len(t)
# Position of bars on x-axis
pos = np.arange(numPeriods)

#Plottet
recept = []
for i in produkt:
    if "Recept" in produkt_navn[i]:
        recept.append(i)
        print("Recept opfanget")
#Plottet
fig = 0
    # For hvert produkt, plot produktionsplanen
for k in produkt:
    if k in recept:
        fig += 1
        plt.figure(fig)

    try:
        plt.subplot(recept[fig] - recept[fig - 1], 1, k - recept[fig - 1] + 1)
    except IndexError:
        plt.subplot(len(produkt) - recept[fig - 1], 1, k - recept[fig - 1] + 1)
    #plt.subplot(len(produkt), 1, k+1)
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
    #plt.legend()
    plt.xticks(fontsize=6)
    plt.ylim(0, max(max(produktion_values),max(lager_values))+max(max(produktion_values),max(lager_values))/10)


plt.show()