# Raw HTTP with nc and curl -v

## nc raw http request 
nc -C localhost 8000
GET /openapi.json HTTP/1.1
Host: localhost:8000
** Empty line enter to send the request **

## curl -v request
curl -v http://localhost:8000/openapi.json


## Reason
This particular practice was done for learning how the http requests are sent under the framework.