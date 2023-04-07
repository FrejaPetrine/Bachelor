import pulp
dir(pulp)

#Problemet
prob = pulp.LpProblem('produktions planlægning',pulp.LpMinimize)

#Definer variabler
produkt = ["Recept1","vare1","vare2"]
tidsperioder = ["januar","februar","marts"]
Xt = pulp.LpVariable.dicts("produktion",(produkt,tidsperioder),lowBound=0,cat="Integer")
It = pulp.LpVariable.dicts("lager",(produkt,tidsperioder),lowBound=0,cat="Integer")

#Import af data
demand = {"Recept1":[615,300,365],"vare1":[116,67,71],"vare2":[119,76,87]}
upc = {"Recept1":2.89,"vare1":64.66,"vare2":32.07}
uhc = {"Recept1":5,"vare1":5,"vare2":5}
fc = {"Recept1":610,"vare1":610,"vare2":610}
bigM = sum(demand)

#Objekt funktion
prob += pulp.lpSum(upc[p]*Xt[p][t])+




