import pulp
dir(pulp)

#liste af tidsperioder
t = [0,1,2,3]

#import af data
demand={1:116,2:67,3:71} # efterspørgsel data
upc = 64.66 #Produktions omkostninger
uhc = 5.17 #Lager omkostninger
fc = 0 #start upp omkostninger
mL = {1:25,2:25,3:25}
m = 421
bigM = max(sum(demand[i] for i in range(1,4)),m)
print('Big M', bigM)

#Problemet
prob = pulp.LpProblem('minimer omk', pulp.LpMinimize)

#variabler
Xt = pulp.LpVariable.dicts("produceret",t,lowBound=0,cat="Integer")
It = pulp.LpVariable.dicts("lager",t,lowBound=0,cat="Integer")
Yt = pulp.LpVariable.dicts("maskine_start",t,lowBound=0, upBound=1,cat=pulp.LpBinary)


#Objekt funktion
prob += pulp.lpSum(upc*Xt[i]+uhc*It[i]+fc*Yt[i]for i in t[0:])


#Bibetingelse
prob += It[0] == 100
for i in t[1:]:
    prob += (Xt[i]+It[i-1]-It[i]) == demand[i] #lager balancen
for i in t[1:]:
    prob+= It[i]>=mL[i]
for i in t[1:]:
    prob += Yt[i]*bigM >= Xt[i] #sæt Yt
for i in t[1:]:
    prob += Yt[i]*m <= Xt[i]

prob.solve()
print("solution status = ",pulp.LpStatus[prob.status])

#print resultat
for v in prob.variables():
    if v.varValue>=0:
        print(v.name, "=", v.varValue)