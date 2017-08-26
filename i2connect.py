'''i2connect.py
   Maintain a connection to the Icinga2 Application Programming Interface
   Objects: Icinga2Connect
   Methods: Icinga2Connect.stream(events, host, port, api)
'''

import requests
import json
#from urllib3.util.retry import Retry
from socket import gethostbyname, gethostbyaddr, gaierror

class Icinga2Connect(object):
    '''Creates a persistent connection object to the Icinga2 API'''

    def __init__(self,
                 host='localhost',
                 port='5665',
                 api='v1',
                 ca=None,
                 auth=None):
        self.host = host
        self.port = str(int(port))
        self.api = api
        self.ca = ca
        self.auth = auth
  
    @staticmethod
    def i2url(host, port, api):
        ''' Validate host and port, and return the API URL header '''
        try:
            host = gethostbyaddr(gethostbyname(host))[0]
        except gaierror:
            raise ValueError("Could not resolve hostname from configuration. Abandoning.")
        return 'https://'+host+':'+port+'/'+api

    def events(self, events=('StateChange'), host="localhost", port="5665", api="v1"):
        '''Generates a stream of events from Icinga2 to relay to the channel.
           CheckResult is disabled, because it's too spammy. Create/delete comments for testing.'''
        url = self.i2url(host, port, api)
        url += '/events'
        validevents = {"v1": [
            'CheckResult',
            'StateChange',
            'Notification',
            'AcknowledgementSet',
            'AcknowledgementCleared',
            'CommentAdded',
            'CommentRemoved',
            'DowntimeAdded',
            'DowntimeRemoved',
            'DowntimeTriggered'
            ]}
        types = list(set(events) & set(validevents[api]))
        data = {"types": types, "queue": "errbot_events"}
  
        try:
            stream = requests.post(url,
                                   auth = self.auth,
                                   verify = self.ca,
                                   headers = {
                                       'Accept':'application/json',
                                       'X-HTTP-Method-Override':'POST'
                                       },
                                   data=json.dumps(data),
                                   stream=True)
            if stream.status_code == 200:
                for line in stream.iter_lines():
                    yield(line)
            else:
                print('Received a bad response from Icinga API: '+str(stream.status_code))
                print('Icinga2 API connection lost.')
        except (requests.exceptions.ConnectionError) as drop:
            raise("No connection to Icinga API. Error received: "+str(drop))


##    def Command(self):
##        i2session = requests.session()
##        i2session.auth = self.auth
##        i2session.verify = self.ca
##        i2session.headers  = {
##            'Accept': 'application/json',
##            }
##        sess_args = requests.adapters.HTTPAdapter(
##            max_retries = Retry(read=5, connect=10, backoff_factor=1)
##            )
##
##        try:
##            i2session.mount(url, sess_args)
##        except (requests.exceptions.ConnectionError) as drop:
##            raise("No connection to Icinga API. Error received: "+str(drop))
