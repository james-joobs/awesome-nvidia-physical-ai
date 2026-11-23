"""Serve only the generated public viewer assets on localhost; no workspace files."""
import argparse
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,unquote
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--port',type=int,default=8090);a=p.parse_args();root=a.root.resolve();lab=Path(__file__).resolve().parent
ALLOWED={'alpamayo.json','perception.json','road.spz','volvo-s90.glb','cameras.json','ATTRIBUTION.txt','preview.jpg','road.spz.json','PANDASET-DATA-LICENSE.txt','VEHICLE-LICENSE.txt'}
def camera_file(route):
 path=root/route
 return route.startswith('camera/') and path.suffix=='.jpg' and path.resolve().is_relative_to((root/'camera').resolve()) and path.is_file()
class Handler(SimpleHTTPRequestHandler):
 def do_GET(self):
  route=unquote(urlsplit(self.path).path).lstrip('/')
  if route=='favicon.ico':self.send_response(204);self.end_headers();return
  if route in {'','index.html','viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js'}:
   name='viewer.html' if route in {'','index.html'} else route;self.path='/'+name;self.directory=str(lab)
  elif route in ALLOWED or camera_file(route):self.directory=str(root)
  else:self.send_error(404);return
  super().do_GET()
 def do_HEAD(self):
  route=unquote(urlsplit(self.path).path).lstrip('/')
  if not camera_file(route) and route not in ALLOWED|{'','index.html','viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js'}:self.send_error(404);return
  self.directory=str(lab if route in {'','index.html','viewer.html','viewer.js','viewer.css','perception-view.js','policy-view.js'} else root);self.path='/viewer.html' if route in {'','index.html'} else self.path;super().do_HEAD()
print(f'RGB viewer: http://127.0.0.1:{a.port}/',flush=True);ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
