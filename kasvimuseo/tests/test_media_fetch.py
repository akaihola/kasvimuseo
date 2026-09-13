"""These tests check the development photo download command under Python 3."""

import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def test_media_fetch_downloads_unicode_names_and_reports_missing_files(tmp_path):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            self.send_response(404 if self.path == '/missing.jpg' else 200)
            self.end_headers()
            self.wfile.write(b'photo bytes')

        def log_message(self, *args):
            pass

    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    script = (Path(__file__).resolve().parents[2] / 'dev/kasvimuseo').read_text()
    # Run the command's Python payload with a small model/settings fixture.
    payload = script.split('media_fetch() {', 1)[1].split("python -c '\n", 1)[1].split("\n'", 1)[0]
    prelude = '''
import sys, types
class Photos:
    def values_list(self, *args, **kwargs):
        return self
    def order_by(self, *args):
        return ['flowers/ä.jpg', 'present.jpg', 'missing.jpg']
sys.modules['django'] = types.SimpleNamespace(setup=lambda: None)
sys.modules['django.conf'] = types.SimpleNamespace(settings=types.SimpleNamespace(
    MEDIA_FALLBACK_URL=%r, MEDIA_ROOT=%r))
sys.modules['photologue.models'] = types.SimpleNamespace(
    Photo=types.SimpleNamespace(objects=Photos()))
''' % ('http://127.0.0.1:%s/' % server.server_port, str(tmp_path))
    (tmp_path / 'present.jpg').write_bytes(b'existing')
    try:
        result = subprocess.run([sys.executable, '-c', prelude + payload],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    assert (tmp_path / 'flowers/ä.jpg').read_bytes() == b'photo bytes'
    assert (tmp_path / 'present.jpg').read_bytes() == b'existing'
    assert requests == ['/flowers/%C3%A4.jpg', '/missing.jpg']
    assert '1 fetched, 1 failed, 1 already present' in result.stdout
    assert result.returncode == 0, result.stderr
