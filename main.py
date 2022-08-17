from __future__ import print_function

import os.path

import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email_getter import data_df
from hidden_variables import CALENDAR_ID

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        dates = data_df[0].to_list()
        start_time = data_df[1].to_list()
        end_time = data_df[2].to_list()
        post = data_df[4].to_list()
        for num in range(0, 30):
            id_number = dates[num] + start_time[num] + end_time[num]
            id_number = id_number.replace('-', '1')
            id_number = id_number.replace(':', '0')

            print(id_number)
            event = {
                'id': f"{id_number}",
                'summary': "Rob Work Shift",
                'description': post[num],
                'start': {
                    'dateTime': f'{dates[num]}T{start_time[num]}:00-04:00',
                },
                'end': {
                    'dateTime': f'{dates[num]}T{end_time[num]}:00-04:00',
                }
            }
            # Call the Calendar API, try/catch in case ID number was used previously and will not post duplicates
            try:
                event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
                print('Event created: %s' % (event.get('htmlLink')))
            except HttpError as error:
                print("DUPLICATE EVENT WILL NOT BE CREATED")
                pass

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
