import os
import requests
import re
from tabulate import tabulate
import json
import uuid
from datetime import datetime

def limpiar_pantalla():
    sistema_operativo = os.name
    if sistema_operativo == "posix":  
        os.system("clear")
    elif sistema_operativo == "nt":  
        os.system("cls")
    else:
        print("Sistema operativo no compatible")

def getActivosData():
    peticion = requests.get("http://154.38.171.54:5501/activos")
    data = peticion.json()
    return data

def getActivosID(id):
    peticion = requests.get(f"http://154.38.171.54:5501/activos/{id}")
    return [peticion.json()] if peticion.ok else []

def getPersonalData():
    peticion = requests.get("http://154.38.171.54:5501/personas")
    data = peticion.json()
    return data

def getZonasData():
    peticion = requests.get("http://154.38.171.54:5501/zonas")
    data = peticion.json()
    return data


######################   VALIDACIONES   ######################
def getPersonalId(id):
    for val in getPersonalData():
        if val.get("id") == id:
            return [val]

def getZonaId(id):
    for val in getZonasData():
        if val.get("id") == id:
            return [val]

def getDataHistoriales(id):
    result = []
    for val in getActivosID(id):
        if val.get("historialActivos"):
            for asd in val['historialActivos']:
                diccitionarioss = asd
                result.append(diccitionarioss)
    return result


def getDataHistorialesMov1(id):
    result = []
    for val in getActivosID(id):
        if val.get("historialActivos"):
            for asd in val['historialActivos']:
                if asd.get('tipoMov') == "1":
                    diccitionarioss = asd
                    result.append(diccitionarioss)
    return result

##   CREAR ASIGNACION ( DEBE ESTAR EN NO ASIGNADO ( ID ESATDO = 0 ) )   ##
def asignarActivo():
    id = input(f"""
Ingrese el id del activo que desea asignar: """)
    data = getActivosID(id)
    if data:
        if data[0]["idEstado"] == "0":
            data[0]["idEstado"] = "1"
            listaDeAsigVacia = data[0]["asignaciones"]
            diccionario = dict()
            while True:
                try:
                    if not diccionario.get("id"):
                        NumeroAsignaciones = len(getDataHistorialesMov1(id))
                        NumeroAsignacionesMas1 = NumeroAsignaciones + 1
                        Resultado = str(NumeroAsignacionesMas1)
                        diccionario["NroAsignacion"] = Resultado

                    if not diccionario.get("FechaAsignacion"):
                        fecha = datetime.now().strftime('%Y-%m-%d')
                        diccionario["FechaAsignacion"] = fecha
        



                    if not diccionario.get("TipoAsignacion"):
                        print(f"""
ASIGNACION: 
1. Persona
2. Zona""")
                        eleccion = input(f"""
Seleccione una opcion: """)
                        if eleccion == "1":
                            diccionario["TipoAsignacion"] = "Personal"
                        elif eleccion == "2":
                            diccionario["TipoAsignacion"] = "Zona"
                        else:
                            raise Exception("Opcion no valida.")



                    if not diccionario.get("AsignadoA"):
                        if diccionario.get("TipoAsignacion") == "Personal":
                            idPersonal = input(f"""
Ingrese el id de la persona a la que desea asignar: """)
                            if getPersonalId(idPersonal):
                                diccionario["AsignadoA"] = idPersonal
                                break
                            else:
                                raise Exception("Id no encontrado.")
                        if diccionario.get("TipoAsignacion") == "Zona":
                            idPersonal = input(f"""
Ingrese el id de la zona a la que desea asignar: """)
                            if getZonaId(idPersonal):
                                diccionario["AsignadoA"] = idPersonal
                                break
                            else:
                                raise Exception("Id no encontrado.")
      
                except Exception as error:
                    print(error)


            listaDeAsigVacia.append(diccionario)
            diccionarioID = data[0]
            idPersonal = diccionario.get("AsignadoA")
            if diccionario["TipoAsignacion"] == "Personal":
                asd = diccionario["AsignadoA"]
                personal = getPersonalId(asd)[0]
                Nombre = personal.get("Nombre")
            else:
                asd = diccionario["AsignadoA"]
                Zona = getZonaId(asd)[0]
                Nombre = Zona.get("nombreZona")

        
            opcion = input(f"""
¿Esta seguro que desea asignar {diccionarioID['Nombre']} a {Nombre}?
    1. Si
    2. Cancelar
                       
Seleccione una opcion: """)
            if opcion == "1":
                agregarHistorial = dict()
                IdQuienRealizaAsignacion = input(f"""
Ingrese el id de la persona que realiza la asignacion: """)
                if getPersonalId(IdQuienRealizaAsignacion):
                    NumeroAsignaciones = len(getDataHistoriales(id))
                    NumeroAsignacionesMas1 = NumeroAsignaciones + 1
                    Resultado = str(NumeroAsignacionesMas1)
                    agregarHistorial["NroId"] = Resultado
                    agregarHistorial["Fecha"] = fecha
                    agregarHistorial["tipoMov"] = "1"
                    agregarHistorial["idRespMov"] = IdQuienRealizaAsignacion
                    dictSolo = data[0]
                    listaDeHistorial = dictSolo["historialActivos"]
                    listaDeHistorial.append(agregarHistorial)
                    requests.put(f"http://154.38.171.54:5501/activos/{id}", data=json.dumps(data[0], indent=4).encode("UTF-8"))
                    print(f"""
Activo asignado correctamente.""")
                    input(f"""
Presione enter para continuar.""")
                else:
                    print("ID no encontrado en la data de personal.")
                    input(f"""
Presione enter para continuar.""")
            else:
                print(f"""
Se cancelo la modificacion""")
                input(f"""
Presione enter para continuar.""")
        
        else:
            print(f"""
SOLO PUEDE ASIGNAR ACTIVOS QUE NO ESTEN ASIGNADOS ( IDESTADO = 0 ) O QUE NO ESTEN DADOS DE BAJA O EN GARANTIA.""")
            input(f"""
Presione enter para continuar.""") 
            
    else:
        print(f"""
ID ingresado no existente""")
        input(f"""
Presione enter para continuar.""")

##   BUSCAR ASIGNACION   ##
def getDataAsiganciones():
    result = []
    for val in getActivosData():
        if val.get("asignaciones"):
            diccitionarioss = val['asignaciones'][0]
            diccitionarioss["ID Activo"] = val.get("id")
            diccitionarioss["Nombre del Activo"] = val.get("Nombre")
            result.append(diccitionarioss)
    return result
    
def getAsignacionPorId(id):
    for val in getDataAsiganciones():
        if val.get("ID Activo") == id:
            return [val]



def menuAsignacionActivos():
    while True:
        try:
            limpiar_pantalla()
            print(f"""
    __  ___                                          
   /  |/  /__  ____  __  __                          
  / /|_/ / _ \/ __ \/ / / /                          
 / /  / /  __/ / / / /_/ /                           
/_/ _/_/\___/_/ /_/\__,_/                _           
   /   |  _____(_)___ _____  ____ ______(_)___   ____ 
  / /| | / ___/ / __ `/ __ \/ __ `/ ___/ / __ \/ __  |
 / ___ |(__  ) / /_/ / / / / /_/ / /__/ / /_/ / / / /
/_/  |_/____/_/\__, /_/ /_/\__,_/\___/_/\____/_/ /_/ 
    ____      /____/_        __  _                   
   / __ \___     /   | _____/ /_(_)   ______  _____  
  / / / / _ \   / /| |/ ___/ __/ / | / / __ \/ ___/  
 / /_/ /  __/  / ___ / /__/ /_/ /| |/ / /_/ (__  )   
/_____/\___/  /_/  |_\___/\__/_/ |___/\____/____/    
                                                     
OPCIONES:
    1. CREAR ASIGNACION
    2. BUSCAR ASIGNACION
    3. REGRESAR AL MENU PRINCIPAL""")
            opcion = input(f"""
Seleccione una opcion: """)
            if opcion == "1":
                asignarActivo()
            elif opcion == "2":
                id = input(f"""
Escriba el ID del activo: """)
                print(tabulate(getAsignacionPorId(id), headers="keys", tablefmt="rounded_grid"))
                input(f"""
Presione enter para continuar.""")
            elif opcion == "3":
                break
            else:
                raise Exception("Opcion no valida")



        except Exception as error:
            print(error)