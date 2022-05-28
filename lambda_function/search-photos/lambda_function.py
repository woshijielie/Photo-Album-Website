import json,boto3 ,requests, idna,requests_aws4auth,urllib3,certifi,datetime
import time
import inflect

from boto3.dynamodb.conditions import Key
# ,chardet

    
def lambda_handler(event, context):
    # text = get_request(event)
    
    query = event['queryStringParameters']['q']
    query.lower()
    # query = 'show me toes and walls'
    singular_query = make_all_singular(query)
    
    
    labels = get_label_fromLex(singular_query)
    print(labels)
    
    
    # if len(labels) != 0:
        
    #     labels = labels[0]
    #     labels = labels.split(' ')
    
    photo_paths = getPhotoPaths(labels)
    
    return{
        # 'json_photo':json_photo,
        # 'responase':labels,
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With,x-api-key',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        
        },
        # 'body': json.dumps(['https://hanfuphotobucket.s3.amazonaws.com/car.png'])
        'body': json.dumps(photo_paths)
        
    }

# function to get labels 
def get_label_fromLex(query):
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName='Detect',  
        botAlias='searchAlias',
        userId="string",           
        inputText=query
    )
    
    labels=[]
    if 'slots' not in response:
        print('No photo collection for query {}'.format(query))
    else:
        slot_val = response['slots']
        for key,value in slot_val.items():
            if value!=None:
                singular_value =  value.rstrip('s')
                labels.append(singular_value)
    return labels
    # if 'slots' not in response:
    #     print('No photo collection for query {}'.format(query))
    # else:
    #     slot_val = response['slots']
    #     for key, value in response['slots']:
    #         if value!=None:
    #             # singular_value =  value.rstrip('s')
    #             labels.append(value)
    # return labels
    
# function to get all photo paths  
def getPhotoPaths(labels):
    photo_paths=[]
    for i in range(len(labels)):
        cur_path = []
        
        host = 'https://search-photo-7temacsocjsgnz6tc44hgswsh4.us-east-1.es.amazonaws.com/photos'
        path = host + '/_search?q=labels:'+ labels[i] 
        headers = { "Content-Type": "application/json" }
        response = requests.get(path, headers=headers, auth=('hanfushi', '4a5s6d4A5S6D#'))
        response = response.json()
        if 'hits' in response:
            for res in response['hits']['hits']:
                img_bucket = res['_source']['bucket']
                img_key_name = res['_source']['objectKey']
                
                # need to check the link format 
                img_url = 'https://s3.amazonaws.com/' + str(img_bucket) + '/' + str(img_key_name)
                
                if i == 0 and img_url not in photo_paths:
                    cur_path.append(img_url)
                    photo_paths.append(img_url)
                else:
                    if img_url in photo_paths and img_url not in cur_path:
                        cur_path.append(img_url)
            photo_paths = cur_path
                
                
    return photo_paths

def make_all_singular(query):
    p=inflect.engine()
    singular_query = ""
    
    query = query.split(" ")
    for word in query:
        
        if p.singular_noun(word) == False:
            singular_query += word
        else:
            singular_query += p.singular_noun(word)
        singular_query += " "
    return singular_query
    
