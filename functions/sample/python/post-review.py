#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def main(dict):
    authenticator = IAMAuthenticator("ERFKpnpTmzK6SUvcCBMWgspwM3YoBK3InnJroz72Pag2")
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url("https://68cba383-c45c-4641-82f8-39fe8b15d7cb-bluemix.cloudantnosqldb.appdomain.cloud")

    response = service.post_document(db='reviews', document=dict["review"]).get_result()
    try: 
        result= {
            'headers': {'Content-Type':'application/json'}, 
            'body': {'data':response} 
            }        
        return result
    except:  
        return { 
            'statusCode': 404, 
            'message': 'Something went wrong'
            }