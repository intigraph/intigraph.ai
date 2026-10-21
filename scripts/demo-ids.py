"""Read-only local before/after HTTP demonstration; no production requests."""
import functools
import http.server
from pathlib import Path
import subprocess
import tarfile
import tempfile
import threading
import urllib.error
import urllib.request

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

root = Path(__file__).resolve().parents[1]
base = '9c55a60d7487b43f98ef327d678e9917d7fbf90f'
with tempfile.TemporaryDirectory(prefix='ids-demo-') as temporary:
    previous = Path(temporary)
    archive = subprocess.check_output(['git','archive',base],cwd=root)
    import io
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(previous,filter='data')
    for label,directory in [('BASE '+base,previous),('CANDIDATE working source',root)]:
        server = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(directory)))
        worker = threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            print(label)
            for resource in ['/', '/ids/quechua/ns.ttl','/ids/quechua/ns.jsonld','/ids/quechua/ns/']:
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}'+resource) as response:
                        print(' GET',resource,'->',response.status,len(response.read()),'bytes')
                except urllib.error.HTTPError as error:print(' GET',resource,'->',error.code)
        finally:server.shutdown();server.server_close();worker.join()
