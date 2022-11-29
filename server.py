from http.server import HTTPServer, BaseHTTPRequestHandler
import processing
import json

#handler class
class Serv(BaseHTTPRequestHandler):
    def do_GET(self):  
        if self.path == '/':
            self.path = '/public/index.html'
        try:            
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))
    
    def do_POST(self):        
        try:
            if self.path.endswith("/filtrar"):
                print("ENTRO")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                content_len = int(self.headers.get('Content-Length'))
                post_body = json.loads(self.rfile.read(content_len))
                response, summary =  processing.filt(post_body)
                data = '{"response" :'+ response +', "summary":'+ summary+'}'           
                self.wfile.write(bytes(data,'utf-8'))

            if self.path.endswith("/obtener-clientes"):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                content_len = int(self.headers.get('Content-Length'))
                post_body = json.loads(self.rfile.read(content_len))
                response = processing.customers(post_body)
                self.wfile.write(bytes(response,'utf-8'))

            if self.path.endswith("/obtener-productos"):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                content_len = int(self.headers.get('Content-Length'))
                post_body = json.loads(self.rfile.read(content_len))
                response = processing.products(post_body)
                self.wfile.write(bytes(response,'utf-8'))
        except IOError:
            self.send_error(404,"File not found")
            print("PATH",self.path)



port = 8091
httpd = HTTPServer(('localhost', port), Serv)
print("Server running on port:" + str(port))
httpd.serve_forever()
httpd.server_close()
print("Server clossed!")