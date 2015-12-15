from __future__ import print_function
import httplib2
import os

from apiclient import discovery, errors
import oauth2client
from oauth2client import client
from oauth2client import tools
from email.mime.text import MIMEText
import base64


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None



class GmailMyself:

    def __init__(self, my_mail):
        self.mail = my_mail
        self.SCOPES = 'https://www.googleapis.com/auth/gmail.send'
        self.CLIENT_SECRET_FILE = 'client_secret.json'
        self.APPLICATION_NAME = 'Bolsa Checker'
        self.service = self.service()

    def credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail-python-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags) 
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)

        return credentials

    def service(self):
        credentials = self.credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)
        return service


    def send(self, subject, message):
        message = MIMEText(message)
        message.update({'to': self.mail, 'from': self.mail, 'subject': subject})
        message = {'raw': base64.urlsafe_b64encode(message.as_string())}

        try:
            self.service.users().messages().send(userId=self.mail, body=message)\
                   .execute()
        except errors.HttpError, error:
            print('An error occurred: %s' % error)

