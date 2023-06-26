from gurobipy import GRB, Model, quicksum
from get_data import *

YEARS = 4
MESES = 48

# datos
qty_comunas = get_comunas()
demanda_predios, qty_predios, almacenamiento_predios = get_predios(MESES)
demanda_comunas, almacenamiento_comunas = get_demanda_comunas(YEARS)
cantidad_agua_cuencas, qty_cuencas = get_cuencas(YEARS)
costos_transporte_comunas = get_costos_transporte('comunas')
costos_transporte_predios = get_costos_transporte('predios')

m = Model("Optimización de la distribución hídrica en Chile para un plan de gobierno en un horizonte de cuatro años")

presupuesto_comunas_min = 10**10
presupuesto_comunas_max = 2*10**10

presupuesto_predios_min = 8*10**11
presupuesto_predios_max = 1*10**12


# Conjuntos
T = range(MESES+1) # 4 años
I = range(qty_cuencas) # cuencas hidrógraficas principales de Chile
J = range(qty_comunas) # comunas de Chile con datos 232
K = range(qty_predios) # predios silvoagropecuarios de más de 2000 hectáreas en Chile en las comunas revisadas

# Parámetros
ctu = costos_transporte_comunas
ctp = costos_transporte_predios
du = demanda_comunas
dp = demanda_predios
su = almacenamiento_comunas
sp = almacenamiento_predios
ka = cantidad_agua_cuencas
cau = {(j, t): uniform(10, 20) for j in J for t in T}
cap = {(k, t): uniform(10, 20) for k in K for t in T}
pu = {(j, t): uniform(presupuesto_comunas_min, presupuesto_comunas_max) for j in J for t in T}
pp = {(k, t): uniform(presupuesto_predios_min, presupuesto_predios_max) for k in K for t in T}

# Variables
u = m.addVars(I, J, T, vtype=GRB.CONTINUOUS, name="u_ijt")
p = m.addVars(I, K, T, vtype=GRB.CONTINUOUS, name="p_ikt")
ku = m.addVars(J, T, vtype=GRB.CONTINUOUS, name="ku_jt")
kp = m.addVars(K, T, vtype=GRB.CONTINUOUS, name="kp_kt")
epu = m.addVars(J, T, vtype=GRB.CONTINUOUS, name="epu_jt")
epp = m.addVars(K, T, vtype=GRB.CONTINUOUS, name="epp_kt")

m.update()

# Restricciones
m.addConstrs((quicksum(u[i, j, t] for j in J) + quicksum(p[i, k, t] for k in K) <= ka[i, t] for i in I for t in T[1:]), name="R1")

m.addConstrs((ku[j, 0] == 0 for j in J), name="R2")

m.addConstrs((quicksum(u[i, j, t] for i in I) + ku[j, t-1] == du[j ,t] + ku[j, t] for j in J for t in T[1:]), name="R3")

m.addConstrs((kp[k, 0] == 0 for k in K), name="R4")

m.addConstrs((quicksum(p[i, k, t] for i in I) + kp[k, t-1] == dp[k, t] + kp[k, t] for k in K for t in T[1:]), name="R5")

m.addConstrs((epu[j, 0] == 0 for j in J), name="R6")

m.addConstrs((pu[j, t] + epu[j, t-1] - quicksum(ctu[i, j]*u[i, j, t] for i in I) - cau[j, t]*ku[j, t] == epu[j, t] for j in J for t in T[1:]), name="R7")

m.addConstrs((epp[k, 0] == 0 for k in K), name="R8")

m.addConstrs((pp[k, t] + epp[k, t-1] - quicksum(ctp[i, k]*p[i, k, t] for i in I) - cap[k, t]*kp[k, t] == epp[k, t] for k in K for t in T[1:]), name="R9")

m.addConstrs((ku[j, t] <= su[j] for j in J for t in T[1:]), name="R10")

m.addConstrs((kp[k, t] <= sp[k] for k in K for t in T[1:]), name="R11")

m.update()

objetivo = quicksum(ka[i, t] - quicksum(u[i, j, t] for j in J) - quicksum(p[i, k, t] for k in K) for i in I for t in T[1:])

m.setObjective(objetivo, GRB.MAXIMIZE)

m.optimize()


print(f"Valor objetivo: {m.ObjVal}")

with open('resultadosu_ijt.csv', 'w') as file:
    file.write('cuenca,comuna,periodo,cantidad agua transportada\n')
    for cuenca in I:
        for comuna in J:
            for periodo in T:
                file.write(f'{cuenca},{comuna},{periodo},{u[cuenca, comuna, periodo].x}\n')

with open('resultadosp_ikt.csv', 'w') as file:
    file.write('cuenca,predio,periodo,cantidad agua transportada\n')
    for cuenca in I:
        for predio in K:
            for periodo in T:
                file.write(f'{cuenca},{predio},{periodo},{p[cuenca, predio, periodo].x}\n')

with open('resultadosku_jt.csv', 'w') as file:
    file.write('comuna,periodo,cantidad agua almacenada\n')
    for comuna in J:
        for periodo in T:
            file.write(f'{comuna},{periodo},{ku[comuna, periodo].x}\n')

with open('resultadokp_kt.csv', 'w') as file:
    file.write('predio,periodo,cantidad agua almacenada\n')
    for predio in K:
        for periodo in T:
            file.write(f'{predio},{periodo},{kp[predio, periodo].x}\n')

with open('resultadoepu_jt.csv', 'w') as file:
    file.write('comuna,periodo,excedente presupuesto\n')
    for comuna in J:
        for periodo in T:
            file.write(f'{comuna},{periodo},{epu[comuna, periodo].x}\n')

with open('resultadoepp_kt.csv', 'w') as file:
    file.write('predio, periodo,excedente presupuesto\n')
    for predio in K:
        for periodo in T:
            file.write(f'{predio},{periodo},{epp[predio, periodo].x}\n')
