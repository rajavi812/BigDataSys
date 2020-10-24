from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse
import boto3
from boto3.dynamodb.conditions import Key, Attr
from mangum import Mangum
from pydantic import BaseModel

# response = client.put_item(TableName='lendingclub', Item={"id":{"S":"keyid123"}})
#response = client.scan(TableName='lendingclub')


API_KEY = "1234567asdfgh"
API_KEY_NAME = "access_token"
COOKIE_DOMAIN = "localtest.me"

# extract the access_token key in the querry, header, cookie
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

#---defining API key
async def get_api_key(
    api_key_query: str = Security(api_key_query), # extract the querry value
    api_key_header: str = Security(api_key_header), # extract the header value
    api_key_cookie: str = Security(api_key_cookie), # extract the cookie value
):

    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

#--defining dynamodb
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('lendingclub')


#---Start of API Endpoints


#----DynamoDb - fetching all records
@app.get("/lenddingclub")
async def scandata():
    client = boto3.client('dynamodb')
    response = client.scan(TableName='lendingclub')
    return response['Items']

#---DynamoDB - fetching loan details
@app.get("/loandetails")
async def loandata():
    response = table.scan(AttributesToGet=['amt','term','rate'])
    return response['Items']

#---DynamoDB - fetching recipient details
@app.get("/recipientdetails")
async def recipientdata():
    response = table.scan(AttributesToGet=['title','length','income','ownership'])
    return response['Items']



@app.post("/loanid/{loan_id}")
async def getloandata(loan_id : int):
    print(loan_id)
    response = table.scan(FilterExpression=Attr('id').eq(loan_id),
                          ProjectionExpression="amt,term,rate")
    return response['Items']

@app.post("/ownership/{ownership}")
async def filterownership(ownership : str):
    response = table.scan(FilterExpression=Attr('ownership').eq(ownership),
                          ProjectionExpression="amt,income,length")
    return response['Items']

#----Welcome Page
@app.get("/")
async def homepage():
    return "welcome to our website"


#---Signin and Authentication
@app.get("/signin")
async def get_documentation(api_key: APIKey = Depends(get_api_key), access_code : str ="" ):

    response = get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
    response.set_cookie(
        API_KEY_NAME,
        value=api_key,
        domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response

#---logout and deleting cookies
@app.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie(API_KEY_NAME, domain=COOKIE_DOMAIN)
    return response

@app.get("/secure_endpoint", tags=["test"])
async def get_open_api_endpoint(api_key: APIKey = Depends(get_api_key)):
    response = api_key
    return response

#---Wrapping fastapi into Mangum, for AWS lambda
handler = Mangum(app)
