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


produkt = range(0, len(produkt_navn))
t = range(0, len(t))

#Beregning af bigM
d_sum = [0]
for recept in range(0, len(ed)):
    for tal in range(0, len(ed[recept])):
        d_sum[recept] += ed[recept][tal]
    d_sum.append(0)
bigM = max(sum(d_sum),max(mP))
print(bigM)

#Berengning af intern efterspørgsel
intern_d_0 = []
for j in range(0,len(ed[0][:])):
    hest = 0
    for i in range(1, len(r)):
        hest += r[i]*ed[i][j]
    intern_d_0.append(hest)

intern_d_0 = np.array(intern_d_0)
intern_d = np.zeros((len(produkt),len(t)))
intern_d[0][:] = intern_d_0
intern_d = np.ceil(intern_d)

print(intern_d[0])
#Problemet
prob = pulp.LpProblem('minimer omk', pulp.LpMinimize)

#Variabler
Xt = pulp.LpVariable.dicts("produceret",(produkt,t),lowBound=0,cat="Integer")
It = pulp.LpVariable.dicts("lager",(produkt,t),lowBound=0,cat="Continuous")
Yt = pulp.LpVariable.dicts("maskine_start",(produkt,t),lowBound=0, upBound=1,cat=pulp.LpBinary)

#Objekt funktion
prob += pulp.lpSum([(epo[i]*(b[i]*Xt[i][j]))+elo[i]*It[i][j] for i in produkt for j in t])

#Bibetingelse

for j in t:
    k = np.ceil(intern_d[0][j]/b[0])
    print("j = ",j,'og k = ',k)
    if j-l[0]>0:
        if k > 0:
            prob += Xt[0][j] == k*b[0]
            prob += ((Xt[0][j]) + It[0][j - 1] - It[0][j]) == ed[0][j] + intern_d[0][j]
        else:
            prob += ((Xt[0][j]) + It[0][j - 1] - It[0][j]) == ed[0][j] + intern_d[0][j]
    else:
        if k > 0:
            prob += Xt[0][j] == k*b[0]
            prob += ((Xt[0][j]) + sL[0] - It[0][j]) == ed[0][j] + intern_d[0][j]
        else:
            prob += ((Xt[0][j]) + sL[0] - It[0][j]) == ed[0][j] + intern_d[0][j]

for i in range(1,len(produkt)):
    for j in t:
        if j-l[i]>0:
            prob += ((b[i]*Xt[i][j])+It[i][j-1]-It[i][j]) == ed[i][j]+intern_d[i][j] #lager balance
        else:
            prob += ((b[i]*Xt[i][j])+sL[i]-It[i][j]) == ed[i][j]+intern_d[i][j]


for i in produkt:
    for j in t:
        prob += It[i][j]>= mL[i] #Mindste lager
        prob += Xt[i][j] >= Yt[i][j]*mP[i] #Mindste produktion
        prob += Yt[i][j]*bigM >= Xt[i][j] #at Yt slår ud som en når der produceres
'''
for i in produkt:
    for j in range(0,len(t)-1):
        prob += Xt[0][j] == r[1]*Xt[1][j+1] + r[2]*Xt[2][j+1] + r[3]*Xt[3][j+1] + r[4]*Xt[4][j+1]
'''

prob.solve()
print("solution status = ",pulp.LpStatus[prob.status])

#print resultat
for v in prob.variables():
    if v.varValue>=0:
        print(v.name, "=", v.varValue)


print('Optimal cost is:', pulp.value(prob.objective))
# Number of periods - used to control placement on the x-axis
numPeriods = len(t)
# Position of bars on x-axis
pos = np.arange(numPeriods)


plt.figure(1)
    # For each product, plot the production plan
for k in produkt:
    plt.subplot(len(produkt), 1, k+1)
    # Extract the optimal variable values
    lager_values = [It[k][j].varValue for j in t]
    produktion_values = [Xt[k][j].varValue for j in t]
    demands = [ed[k][j] + r[k]*Xt[k][j].varValue for j in t]
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


# Labels on axis
plt.xlabel('Periods to plan')
plt.ylabel('Demand')

plt.show()