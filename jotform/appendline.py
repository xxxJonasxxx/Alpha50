
# [START sheets_append_values]
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#======================================================================================
# Programa: appendline.py
# Realizado Por: Elvis García
# Fecha: 05/2024
# Descripción: Programa que se encarga de cargar información a Google Sheet
#              
#======================================================================================


#==================================================================
# Carga los datos al Google Sheet especificado
#==================================================================
def append_values(spreadsheet_id, range_name, value_input_option, _values):
  """
  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  # If modifying these scopes, delete the file token.json.
  SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/contacts"]
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "client_secret_114630298739-71hmm89b9logpjv8tk41assehvtclauj.apps.googleusercontent.com.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)

    values = [
        [
            # Cell values ...
        ],
        # Additional rows ...
    ]
    # [START_EXCLUDE silent]
    values = _values
    # [END_EXCLUDE]
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body,
        )
        .execute()
    )


    return result

  except HttpError as error:
    print(f"Ha ocurrido un error: {error}")
    return error


if __name__ == "__main__":
  # Pass: spreadsheet_id, range_name value_input_option and _values)
  append_values(
      "1daEsUwb_Gzz9D0tCaFmNOuRm4YC28KtuFRJbZCL0l60",
      "A1:Q2",
      "USER_ENTERED",
      [["Products Accelerator-Kiara","Vicent","Spain","'+34 669419898","vicentnavarro@mac.com","2024-05-06 02:01:59","Bueno","No","","Mejorable","Quiero resultados ya","Ponerte en la mejor forma física de tu vida","Quiero probar tu método","Hoy mismo","Sí","Más de 500€ (más de $580)","Entre 51-55"], 
       ["Products Accelerator-Elvis","Vicent","Spain","'+34 669419898","vicentnavarro@mac.com","2024-05-06 02:01:59","Bueno","No","","Mejorable","Quiero resultados ya","Ponerte en la mejor forma física de tu vida","Quiero probar tu método","Hoy mismo","Sí","Más de 500€ (más de $580)","Entre 51-55"]],
  )
  # [END sheets_append_values]
