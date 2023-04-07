import pulp
dir (pulp)
import json
import numpy as np
import re

with open('Alt_data.json', 'r') as openfile:
    json_data = json.load(openfile)
#Data
produkt = json_data['produkter']
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

produkt = range(0, len(produkt))
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

#Problemet
prob = pulp.LpProblem('minimer omk', pulp.LpMinimize)

#Variabler
Xt = pulp.LpVariable.dicts("produceret",(produkt,t),lowBound=0,cat="Integer")
It = pulp.LpVariable.dicts("lager",(produkt,t),lowBound=0,cat="Integer")
Yt = pulp.LpVariable.dicts("maskine_start",(produkt,t),lowBound=0, upBound=1,cat=pulp.LpBinary)

#Problemet
prob = pulp.LpProblem('minimer omk', pulp.LpMinimize)

#Variabler
Xt = pulp.LpVariable.dicts("produceret",(produkt,t),lowBound=0,cat="Integer")
It = pulp.LpVariable.dicts("lager",(produkt,t),lowBound=0,cat="Integer")
Yt = pulp.LpVariable.dicts("maskine_start",(produkt,t),lowBound=0, upBound=1,cat=pulp.LpBinary)

#Objekt funktion
prob += pulp.lpSum([epo[i]*Xt[i][j]+elo[i]*It[i][j] for i in produkt for j in t])

#Bibetingelse
for i in produkt:
    for j in t:
        if j>0:
            prob += (Xt[i][j]+It[i][j-1]-It[i][j]) == ed[i][j]+intern_d[i][j] #lager balance
        else:
            prob += (Xt[i][j]+sL[i]-It[i][j]) == ed[i][j]
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

value = []
name = []

for v in prob.variables():
    value.append(v.varValue)
    name.append(v.name)
    if v.varValue>=0:
        print(v.name, "=", v.varValue)

check_lager = 'l'
check_maskine = 'm'
check_produceret = 'p'

lager_name = [idx for idx in name if idx[0].lower() == check_lager.lower()]
maskine_name = [idx for idx in name if idx[0].lower() == check_maskine.lower()]
produceret_name = [idx for idx in name if idx[0].lower() == check_produceret.lower()]

lager_value = value[0:len(lager_name)]
maskine_value = value[len(lager_name):len(lager_name+maskine_name)]
produceret_value = value[len(lager_name+maskine_name):len(lager_name+maskine_name+produceret_name)]

lager_name_sorted = []
lager_name_sorted_int = []
for i in range(0,len(lager_name)):
    lager_name_sorted.append(re.sub("[^0-9]", "", lager_name[i]))
    #lager_name_sorted[i] = lager_name_sorted[i][1:]
    lager_name_sorted_int.append(int(lager_name_sorted[i])) #Virker ikke, bliver nødt til at være på en loop måde der tager højde for den åndsvage navngivning



print("hest")
#prob += pulp.lpSum(upc*Xt[i]+uhc*It[i]+fc*Yt[i]for i in t[1:])