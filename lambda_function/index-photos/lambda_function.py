import json
import boto3
import requests 
import requests_aws4auth
import datetime
import inflect
bot = boto3.client('s3')
def lambda_handler(event, context):
    #get bucket name and key
    
    info = event['Records'][0]['s3']
    bucket_name = info['bucket']['name']
    photo_name = info['object']['key']
    
    #get label using rekognition
    labels = getLabels(bucket_name, photo_name)
    
    
    #get json formatted photo
    jsoned_photo = jsonfiy_photo(bucket_name, photo_name, labels)
    
    #upload to opensearch
    response = upload_to_open_search(jsoned_photo)
    
    # TODO implement
    return {
        'response':labels,
        'label':labels,
        'key_name': photo_name,
        'bucket_name': bucket_name,
        'statusCode': 200,
        'body': json.dumps("hello")
    }
    
    
def getLabels(bucket_name, key_name):
    boto = boto3.session.Session('','',region_name='us-east-1')
    rekognition = boto.client('rekognition')
    response = rekognition.detect_labels(
        Image = {
            'S3Object' : {
                'Bucket' : bucket_name,
                'Name' : key_name
            }
        },
        MaxLabels=10
    )
    labels=[]
    for res in response['Labels']:
        labels.append(res['Name'])
    
    # Get S3 metadata using headObject() method
    headObject = bot.head_object(Bucket=bucket_name, Key=key_name)
    
    print(headObject)
    metaData = headObject['Metadata']
    if len(metaData) !=0:
        custom_labels = metaData['customlabels'].split(',')
        
        p=inflect.engine()
        singular_query = []
        for word in custom_labels:
            word.lower()
            if p.singular_noun(word) == False:
                singular_query.append(word)
            else:
                singular_query.append(p.singular_noun(word))
            
        
        
        
        labels.extend(singular_query)
    return labels
    
def jsonfiy_photo(bucket_name, key_name, labels):
    jsonfied_photo = {
        'objectKey': key_name,
        'bucket': bucket_name,
        'createdTimeStamp': datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"),
        'labels': labels
    }
    return jsonfied_photo


def upload_to_open_search(jsoned_photo):
    #endpoint = 'https://search-photos-qxhwqporwm5u6sqzzema4xdt6a.us-east-1.es.amazonaws.com/photos/photo'
    
    endpoint = 'https://search-photo-7temacsocjsgnz6tc44hgswsh4.us-east-1.es.amazonaws.com/photos/photo'
    headers = { "Content-Type": "application/json" }
    response = requests.post(endpoint, auth=("hanfushi", "4a5s6d4A5S6D#"), json=jsoned_photo, headers=headers)
    
    return response
    
    
