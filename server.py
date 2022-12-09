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
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                content_len = int(self.headers.get('Content-Length'))
                post_body = json.loads(self.rfile.read(content_len))
                response, summary =  processing.filt(post_body,"simple")
                response2, summary2 =  processing.filt(post_body,"temporal_c")
                response3, summary3 =  processing.filt(post_body,"temporal_a")
                response4, summary4 =  processing.filt(post_body,"temporal_a2")
                response5, summary5 =  processing.filt(post_body,"croston")
                response6, summary6 =  processing.filt(post_body,"croston_tsb")
                
                general_summary = '['+summary[1:-1]+','+summary2[1:-1]+','+summary3[1:-1]+','+summary4[1:-1]+','+summary5[1:-1]+','+summary6[1:-1]+']'
                data = '{"summary" :'+ general_summary +', "simple":'+ response+', "temporal_c":'+response2+', "temporal_a":'+response3+', "temporal_a2":'+response4+', "croston":'+response5+', "croston_tsb":'+response6+'}'                
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