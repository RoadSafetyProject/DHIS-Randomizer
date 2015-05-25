import base64
import httplib2

class HttpRequestor:
    
    def __init__(self, dhisAPIUrl,name, password):
        self.auth = base64.encodestring( name + ':' + password)
        self.http = httplib2.Http()
        self.dhisAPIUrl = dhisAPIUrl
    def get(self,url):
        return self.request(url,"GET")
    def delete(self,url):
        return self.request(url,"DELETE")
    def post(self,url,data):
        return self.request(url,"POST",data)
    def request(self,url,method,data = None):
        return self.http.request(self.dhisAPIUrl + "api/"+ url,
                          method,body=data,
                          headers = { 'Authorization' : 'Basic ' + self.auth,"Content-Type": "application/json" }
        )