'''i2parse.py
   Parse JSON objects from the Icinga2 API
   Objects: EventStream
   Methods: EventSream.nice(event)
'''

import json
from datetime import timedelta


class EventStream(object):
    '''Process json from the Icinga2 API into chat-friendly strings'''

    def __init__(self, event=None):
        self.event = event

    #### This becomes my event object
    @staticmethod
    def comment(e):
        return "Re: {0}, {1} says: '{2}'.".format(
            e["comment"]["host_name"], e["comment"]["author"], e["comment"]["text"]
            )
        
    @staticmethod
    def commentrm(e):
        return "{0}'s comment ({1}) removed from {2}".format(
            e["comment"]["author"], e["comment"]["text"], e["comment"]["host_name"]
            )
        
    @staticmethod
    def ack(e):
        return "{0} problem on {1} acknowledged by {2}.".format(
            e.get("service","host"), e["host"], e["author"]
            )
    
    @staticmethod
    def ackrm(e):
        return "Acknowledgement of {0} problem on {1} cleared.".format(
            e.get("service","host"), e["host"]
            )
    
    @staticmethod
    def notification(e): 
        return "Notice of {0} on {1} sent to {2}".format(
            e["notification_type"], e["host"], ", ".join(e["users"])
            )
    
    @staticmethod
    def downservice(e):
        try:
            return "{0} ({1})".format(e["host_name"], e["service_name"])
        except KeyError:
            return e["hostname"]
            
    @staticmethod
    def downadd(e):
        d = e["downtime"]
        duration = str(timedelta(seconds=int(d["end_time"] - d["start_time"])))
        return "{0} has scheduled downtime for {1} lasting {2} because {3}".format(
            d["author"], downservice(d), duration, d["comment"] 
            )
          
    @staticmethod
    def downtrigger(e):
        return downservice(e["downtime"]) + " downtime has begun."
    
    @staticmethod
    def downrm(e):
        return downservice(e["downtime"]) + " downtime has ended."
    
    @staticmethod
    def state(e):
        '''Parse Icinga state numbers into meaningful strings'''
        before = e['check_result']['vars_before']
        after  = e['check_result']['vars_after']
        # Prevent retry spam before parsing results
        try:
            if after['attempt'] > 1.0:
                return
        except:
            pass
        
        if after['state'] < before['state']:
            change="RECOVERED"
        elif after['state'] > before['state']:
            change="DEGRADED"
        else:
            change="CHANGED"
    
        service = e.get("service","host")
        if not service.isupper(): service = service.title() 
        return "{0} {1} on {2}: {3}".format(
            service, change, e["host"], e["check_result"]["output"]
            )
            
    @classmethod
    def nice(self,event):
        ''' Parse json objects returned by icinga into chat-friendly text.'''
        nice = {
            'StateChange': self.state,
            'CommentAdded': self.comment,
            'CommentRemoved': self.commentrm,
            'AcknowledgementSet': self.ack,
            'AcknowledgementCleared': self.ackrm,
            'Notification': self.notification,
            'DowntimeAdded': self.downadd,
            'DowntimeTriggered': self.downtrigger,
            'DowntimeRemoved': self.downrm,
            }
        return nice[event['type']](event) if event['type'] in nice else event

