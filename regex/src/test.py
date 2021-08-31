import os
from azure.communication.sms import SmsClient

# Create the SmsClient object which will be used to send SMS messages
sms_client = SmsClient.from_connection_string("endpoint=https://sms_service.communication.azure.com/;accesskey=hjfPD6T3HDgYePWPViXeODt7bY9jmdFW1WL2KgHNr2wtd9HTPbcalQ87H/6aDeruCZRL4Di8V+6R9AlUDBWa4Q==")

try:
    # Quickstart code goes here
    #print(sms_client)
    sms_responses = sms_client.send(from_="4153365079", to=["4153365079"], \
                message="Hello World via SMS", enable_delivery_report=True, tag="custom-tag")

except Exception as ex:
    print('Exception:')
    print(ex)