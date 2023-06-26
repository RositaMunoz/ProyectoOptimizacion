from random import randint, seed, uniform
seed(10)

def get_comunas():
    with open('comunas_id.csv', 'r') as file:
        comunas = file.readlines()

    return len(comunas)-1

def get_predios(periodos):
    with open('demanda_predios5000.csv') as file:
        predios = file.readlines()

    dict_predios = {}
    almacenamiento = [0]*(len(predios)-1)
    
    for k in range(len(predios)):
        predios[k] = predios[k].strip().split(',')
        if k != 0:
            almacenamiento[int(predios[k][1])] = (float(predios[k][3])/4/7)*2
            for t in range(1, periodos+1):
                dict_predios[(int(predios[k][1]), t)] = (float(predios[k][3]) + uniform(float(predios[k][3])*-0.2, float(predios[k][3])*0.2))*0.1
    return dict_predios, len(predios)-1, almacenamiento

def get_demanda_comunas(years):
    with open('consumo_filtered.csv', 'r') as file:
        comunas = file.readlines()
    dict_comunas = {}
    almacenamiento = [0]*get_comunas()
    for j in range(len(comunas)):
        comunas[j] = comunas[j].strip().split(';')

    for j in range(1,len(comunas), 12):
        consumo_comuna = 0
        for t in range(years):
            for r in range(12):
                if t == 0:
                    consumo_comuna += float(comunas[j+r][0])
                dict_comunas[(int(comunas[j][2]), int(comunas[j+r][1])+12*t)] = float(comunas[j+r][0])
        almacenamiento[int(comunas[j][2])] = ((consumo_comuna/12)/4/7)*2
    return dict_comunas, almacenamiento

def get_cuencas(years):
    with open('caudales.csv', 'r') as file:
        cuencas = file.readlines()
    dict_cuencas = {}

    for i in range(len(cuencas)):
        cuencas[i] = cuencas[i].strip().split(',')
        if i != 0:
            for t in range(years):
                for r in range(12):
                    dict_cuencas[(int(cuencas[i][1]), int(cuencas[0][3+r])+12*t)] = float(cuencas[i][3+r])
    return dict_cuencas, len(cuencas)-1    

def get_costos_transporte(type_costo="comunas"):
    costo1 = 10
    with open('distancias_filtered.csv', 'r') as f:
        distancias = f.readlines()
    for i in range(len(distancias)):
        distancias[i] = distancias[i].strip().split(';')

    with open('Id-cuencas-con-comunas.csv', 'r') as file:
        cuencas = file.readlines()
    for i in range(len(cuencas)):
        cuencas[i] = cuencas[i].strip().split(';')

    dict_costos = {}

    if type_costo == "comunas":
        with open('comunas_id.csv', 'r') as file:
            comunas = file.readlines()
                
        for i in range(len(comunas)):
            comunas[i] = comunas[i].strip().split(';')

        for i in range(len(cuencas)):
            for j in range(len(comunas)):
                if i != 0 and j != 0:
                    distancia = distancias[int(comunas[j][1])+1][int(cuencas[i][1])]
                    dict_costos[(int(cuencas[i][0]), int(comunas[j][1]))] = int(float(distancia)*costo1)
        
    if type_costo == "predios":
        with open('demanda_predios5000.csv', 'r') as file:
            predios = file.readlines()
        for i in range(len(predios)):
            predios[i] = predios[i].strip().split(',')
        for i in range(len(cuencas)):
            for j in range(len(predios)):
                if i!= 0 and j != 0:
                    distancia = distancias[int(predios[j][4])+1][int(cuencas[i][1])]
                    dict_costos[(int(cuencas[i][0]), int(predios[j][1]))] = int(float(distancia)*costo1)
    return dict_costos
