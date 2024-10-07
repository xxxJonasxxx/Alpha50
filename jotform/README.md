# AUTOMATIZACIONES EN PYTHON PARA ALPHA50

## Programa de descarga de respuestas de leads en formularios de jotform
JotformData.py realiza la busqueda de todos los formularios que están marcados como activos y valida si existen respuestas nuevas de leads. Estas respuestas se enlistan y organizan de acuerdo a algunos criterios y luego son enviadas para ser cargadas en el un Google Sheet en la nube. Una vez que se carga toda la información nueva se eliminan las respuestas en Jotform. Esta aplicación utiliza el API de Jotform para realizar las consultas. 

## Programa de carga de información a Google Sheet
appendline.py es un programa que se encarga de agregar nuevas lineas a un documentos Google Sheet ubicado en la nube. Utiliza el API de Google para realizar esta tarea. 

## Programa addcontact.py
Programa que carga los teléfono contactos al google contact mediante el API de Google