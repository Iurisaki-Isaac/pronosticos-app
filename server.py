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
                print(post_body)
                valores = {}
                response1, summary1, valores["simple"] =  processing.filt(post_body,"simple")
                response2, summary2, valores["temporal_c"] =  processing.filt(post_body,"temporal_c")
                response3, summary3, valores["temporal_a"] =  processing.filt(post_body,"temporal_a")
                response4, summary4, valores["temporal_a2"] =  processing.filt(post_body,"temporal_a2")
                response5, summary5, valores["croston"] =  processing.filt(post_body,"croston")
                response6, summary6, valores["croston_tsb"] =  processing.filt(post_body,"croston_tsb")                                            
                valores["label"] = [date.strftime("%Y-%m-%d") for date in processing.weekDates(post_body["fecha_inicio"], post_body["fecha_fin"])]
                valores["datos_pasados"] = processing.realPastData(post_body)                       
                
                general_summary = '['
                first = True
                for resumen in [summary1,summary2,summary3,summary4,summary5,summary6]:
                    general_summary = general_summary + "," if not first and resumen != '[]' else general_summary
                    general_summary = general_summary + resumen[1:-1] if resumen != '[]' else general_summary
                    first = False if first == True else first
                general_summary = general_summary + ']'

                data = {}
                data["summary"] = json.loads(general_summary)
                data["simple"] = json.loads(response1)
                data["temporal_c"] = json.loads(response2)
                data["temporal_a"] = json.loads(response3)
                data["temporal_a2"] = json.loads(response4)
                data["croston"] = json.loads(response5)
                data["croston_tsb"] = json.loads(response6)
                data["graficar"] = valores
                data = json.dumps(data)
                
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