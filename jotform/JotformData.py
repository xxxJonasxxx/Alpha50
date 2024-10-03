import requests
import pandas as pd
import re
import os
import datetime
import appendline as gapi
import addcontact as contact

#======================================================================================
# Programa: JotformData.py
# Realizado Por: Elvis García
# Fecha: 04/2024
# Descripción: Programa que descarga las respuestas de los Leads en los Jotforms de Alpha50
#              las organiza y luego las carga en un Google Sheet.
#======================================================================================

#======================================================================
# Obtiene los nombres de los formularios 
#======================================================================
def getnameforms(formsIDs):

    apikey = os.environ.get("alpha_jotformapikey") #Obtiene el API Key de Jotform
    formsIDsNames = [] #Inicializa lista de nombres y ids de los formularios

    for row in formsIDs.values:
        strRow = str(row[0])

        # Crea los parámetros del request
        url = f'https://eu-api.jotform.com/form/{strRow}?apikey={apikey}'
        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload) #Realiza el request al API

        # Evalua si la consulta fue correcta
        if response.status_code == 200:
            dataResponse = response.json()

            # Carga en el diccionario los valores del id y el nombre del formulario
            formIDName = {
                strRow: dataResponse["content"]["title"].rstrip()
            }

            formsIDsNames.append(formIDName) #Agrega el id y el nombre del formulario a la lista
    

    return(formsIDsNames) #Retorna la lista


#==============================================================================
# Obtiene las respuestas de los formularios
#==============================================================================
def getanswers(idForm, formName, created):

    # print(f"id form es {idForm}")
    # Obtiene el API Key de Jotform
    apikey = os.environ.get("alpha_jotformapikey")

    # Crea las variables de request
    url = f'https://eu-api.jotform.com/form/{idForm}/submissions?apikey={apikey}&limit=1000&filter={{"status":"ACTIVE"}}'
    payload = {}
    headers = {}

    # Envía el request al API de Jotform
    response = requests.request("GET", url,headers=headers,data=payload)
    dataResponse = response.json()

    answersList = [] # Inicia la lista de respuesta
    idAnswerList = [] # Inicializa lista de id de respuetas

    # Orden del archivo a crear
    orderList = [
        'Nombre Formulario',
        'Nombre',
        'País',
        'Teléfono',
        'E-mail',
        'Fecha',
        '¿Cuál es tu estado físico actual?',
        '¿Padeces sobrepeso?',
        'En caso afirmativo, ¿Cuánto kgs crees que te sobran?',
        '¿Cómo definirías tu estado anímico actual?',
        '¿Cuál dirías que es tu punto débil?',
        '¿Cuál es tu objetivo principal?',
        '¿Por qué crees que puedo ayudarte?',
        '¿Cuándo estarías dispuesto a empezar?',
        '¿Estás dispuesto a comprometerte durante los próximos seis meses invirtiendo tiempo y recursos económicos en tu salud, con el objetivo de alcanzar el mejor estado físico de tu vida?',
        '¿Cuál es tu presupuesto actual para invertir en tu salud? Hago esta pregunta para asegurarme de no hacerte perder el tiempo y determinar el nivel de asesoramiento que puedo ofrecer?',
        '¿Qué edad tienes?',
        '¿Te gustaría hablar con nuestro equipo de asesores estratégicos con el objetivo de brindarte alternativas personalizadas y adaptadas a tus necesidades?',
        'Fecha Creación'
    ]

    # Valida que exista data que procesar
    if len (dataResponse["content"]) > 0:
        for record in dataResponse["content"]:

            # Agrega a la lista el id de la respuesta    
            idAnswerList.append(record["id"])

            # Inicia el diccionario de respuestas
            answer = {
                'Nombre Formulario': formName,
                'Fecha': record["created_at"],
                'Fecha Creación': created
            } 

            for idAnswer in record["answers"]:

                if record["answers"][idAnswer]["text"] != "Divider": #Pregunta si es un Divider
                    
                    if record["answers"][idAnswer]["text"] != "": #Pregunta si no hay pregunta
                        
                        if "answer" in record["answers"][idAnswer]: #Pregunta si no hay respuesta
                            
                            # Valida si la pregunta es la País Télefono para separarlo en 2 variable. 
                            if record["answers"][idAnswer]["text"] == "País y teléfono": 
                                pattern = r'^(.*?)\r\n(.*)$'
                                match = re.match(pattern, record["answers"][idAnswer]["answer"])

                                pais = match.group(1).strip()
                                telefono = "'" + match.group(2).strip()

                                # Valida si es México y le agrega un 1 luego de código de país
                                if pais == "Mexico":
                                    telefono = telefono.replace("+52 ","+52 1")

                                answer.update({
                                    "País": pais,
                                    "Teléfono": telefono
                                })
                            else:
                                answer.update({
                                    record["answers"][idAnswer]["text"]: record["answers"][idAnswer]["answer"]
                                })
                        else:
                            answer.update({
                                record["answers"][idAnswer]["text"]: ""
                            })

            # Se organiza las columnas
            dataOrdenada = {key: answer[key] for key in orderList if key in answer} 

            # Excluye respuesta de Venezuela y Cuba 
            if dataOrdenada["País"] != "Venezuela" and dataOrdenada["País"] != "Cuba":
                
                invertir = dataOrdenada['¿Cuál es tu presupuesto actual para invertir en tu salud? Hago esta pregunta para asegurarme de no hacerte perder el tiempo y determinar el nivel de asesoramiento que puedo ofrecer?']

                if invertir != "" and invertir != "No estoy en condiciones de invertir" and invertir != "No me interesa invertir en mi salud" and invertir != "No quiero pagar nada" and invertir != "No quiero invertir en mi salud":
                    answersList.append(dataOrdenada)

        # Carga la lista al DataFrame
        df = pd.DataFrame(answersList)
        pathFile = r'C:\Users\egarcia\Documents\Programas\Files\jotformdata.xlsx'

        # Evalúa si el archivo existe, si existe agrega las nuevas lineas sino crea un nuevo archivo y carga las lineas. 
        if os.path.exists(pathFile):
            old_df = pd.read_excel(pathFile)
            update_df = pd.concat([old_df, df], ignore_index=True)
            update_df.to_excel(pathFile, index=False)
            
        else:
            df.to_excel(pathFile,index=False) 


        print(f"Se cargan datos del formulario {formName}.")
        return(idAnswerList, answersList) #Retorna el listado de ids de las respuestas             
        
    else:
        
        return(None,None)
    
#============================================================
# Enviar respuestas de los formularios al Google Sheet
#============================================================
def sentgoogle(leadAnswers):

    sheetid = os.environ.get("alpha_googlesheetid") #Obtiene ID de Google Sheet
    googlesheetdata =[] #Crea la lista de las respuestas
    
    # Recorre el diccionario para organizar las respuestas en listas
    for answers in leadAnswers:
        data = []
        for value in answers.values():
            data.append(value)

        googlesheetdata.append(data)

    # Envía las respuestas al módulo que carga al Google Sheet
    respond = gapi.append_values(
            sheetid, #Id Google Sheets
            "A1:R2", #Celdas
            "USER_ENTERED",
            googlesheetdata #Data
        )
    if "updates" in respond:
        print(f"Se agregaron {(respond.get('updates').get('updatedCells'))} celdas.")
        return("updated")
    else:
        print(f"Se generó el siguiente error --> {respond}")
        return("error")
    
#============================================================
# Agregar contactos a Google Contacts
#============================================================

def addcontacts (listAnswers):
    
    i = 0 #Contador de Contactos Nuevos
    
    # Recorre cada contacto
    for answer in listAnswers:
        phone = answer["Teléfono"].replace("'","") #Quita el (') al inicio del número de teléfono
        
        # Crea la estructura
        new_contact = {
        "names": [
            {"givenName": phone}
        ],
        "phoneNumbers":[
            {"value":phone}
        ]
        }

        flag = contact.main(new_contact=new_contact) #Se envía a cargar el contacto el Google Contacts 

        # Si guardó el contacto agrega un contacto nuevo a la cuenta
        if flag == "success":
            i = i + 1


    print(f"Se agregaron {i} contactos.")

#============================================================
# Borra las respuestas enviadas por los leads.
#============================================================
def deleteanswers(idAnswers):

    apikey = os.environ.get("alpha_jotformapikey") #Obtiene el API Key de Jotform

    for idAnswer in idAnswers:

        # Crea los parámetros del request por cada grupo de respuesta de los leads
        url = f'https://eu-api.jotform.com/submission/{idAnswer}?apikey={apikey}'
        payload = {}
        headers = {}

        # Envía el request
        response = requests.request("DELETE", url, headers=headers, data=payload)

        if response.status_code != 200:
            print(f"Error al borrar respuesta {idAnswer} con el código {response.status_code}")

#=======================================================
# Módulo principal
#=======================================================
def main():

    # Ruta donde están los ID's de los formularios activos
    # pathExcel = r'C:\files\jobformids.xlsx'
    pathExcel = r'C:\files\jobformids_test.xlsx'

    # Calcula la fecha de ejecución del programa
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Valida que exista el archivo de ID's de formularios válidos
    if os.path.exists(pathExcel):
        
        jfid_df = pd.read_excel(pathExcel) #Abre el archivo Excel

        formsIDsNames = getnameforms(jfid_df) #Envía el listado para consultar los nombres de los formularios

        idAnswerList = []
        leadAnswers = []
        
        # Recorre el listado de ids y nombres de formularios
        for dataList in formsIDsNames:
            for key, value in dataList.items():
                
                # Llama al módulo que consulta las respuestas en Jotform y devuelve id respuestas y las respuestas
                answerlist, Answers = getanswers(key,value,formatted_datetime)

                if answerlist != None:
                    idAnswerList.extend(answerlist) #Actualiza la lista
                    leadAnswers.extend(Answers)

        # Valida que hayan respuestas para cargar en el Google Sheet
        if leadAnswers != None:

            delete = sentgoogle(leadAnswers) 

            # Borra si confirma que se insertó en el Google Sheet
            if delete == "updated":

                # Borra las respuesta de JotForm (Se comenta momentaneamente)
                deleteanswers(idAnswerList)

            # Agrega contactos nuevos    
            addcontacts(leadAnswers)
        
    else:
        print("El archivo del listado de formularios válidos no existe.")
      

if __name__ == '__main__':
    main()

