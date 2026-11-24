"""Serve only the generated public viewer assets on localhost; no workspace files."""
import argparse
import json
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,unquote
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--port',type=int,default=8090);p.add_argument('--enhancer-url',help='Optional loopback GPU enhancer, reached directly or through an SSH tunnel');a=p.parse_args();root=a.root.resolve();lab=Path(__file__).resolve().parent
if a.enhancer_url:
 target=urlsplit(a.enhancer_url)
 if target.scheme!='http' or target.hostname not in {'localhost','127.0.0.1','::1'} or target.username or target.password or target.query or target.fragment or target.path not in {'','/'}:p.error('--enhancer-url must be a plain loopback HTTP base URL')
ALLOWED={'alpamayo.json','perception.json','road.spz','guided.spz','guidance.json','support.spz','support.json','matched-rgb.spz','matched-depth.spz','volvo-s90.glb','cameras.json','ATTRIBUTION.txt','preview.jpg','road.spz.json','PANDASET-DATA-LICENSE.txt','VEHICLE-LICENSE.txt'}
def camera_file(route):
 path=root/route
 return route.startswith('camera/') and path.suffix=='.jpg' and path.resolve().is_relative_to((root/'camera').resolve()) and path.is_file()
class Handler(SimpleHTTPRequestHandler):
 def config(self,head=False):
  value=json.loads((root/'cameras.json').read_text());value['enhancement_endpoint']='/api/enhance';raw=json.dumps(value).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers()
  if not head:self.wfile.write(raw)
 def do_GET(self):
  route=unquote(urlsplit(self.path).path).lstrip('/')
  if route=='cameras.json' and a.enhancer_url:self.config();return
  if route=='favicon.ico':self.send_response(204);self.end_headers();return
  if route in {'','index.html','viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js','enhancement-view.js'}:
   name='viewer.html' if route in {'','index.html'} else route;self.path='/'+name;self.directory=str(lab)
  elif route in ALLOWED or camera_file(route):self.directory=str(root)
  else:self.send_error(404);return
  super().do_GET()
 def do_HEAD(self):
  route=unquote(urlsplit(self.path).path).lstrip('/')
  if route=='cameras.json' and a.enhancer_url:self.config(head=True);return
  if not camera_file(route) and route not in ALLOWED|{'','index.html','viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js','enhancement-view.js'}:self.send_error(404);return
  self.directory=str(lab if route in {'','index.html','viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js','enhancement-view.js'} else root);self.path='/viewer.html' if route in {'','index.html'} else self.path;super().do_HEAD()
 def do_POST(self):
  if urlsplit(self.path).path!='/api/enhance' or not a.enhancer_url:self.send_error(404);return
  if urlsplit('http://'+self.headers.get('Host','')).hostname not in {'localhost','127.0.0.1','::1'}:self.send_error(403);return
  if self.headers.get('Origin') not in {None,'http://'+self.headers.get('Host','')}:self.send_error(403);return
  if self.headers.get('Content-Type','').split(';')[0]!='application/json':self.send_error(415);return
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=3500000:raise ValueError('size')
   raw=self.rfile.read(size);request=Request(a.enhancer_url.rstrip('/')+'/infer',data=raw,headers={'Content-Type':'application/json'},method='POST')
   with urlopen(request,timeout=90) as response:result=response.read(5000000)
  except ValueError:self.send_error(400);return
  except (URLError,HTTPError,TimeoutError):self.send_error(503,'Local GPU enhancer unavailable');return
  self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(result)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(result)
print(f'RGB viewer: http://127.0.0.1:{a.port}/',flush=True);ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
