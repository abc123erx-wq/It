#!/usr/bin/env python3
"""Servidor estático do hub "BO1 Zombies — Modo Online".

Uso:  python3 online/serve.py [porta]     (padrão 8080)
Abre em http://<host>:8080/ — a página chama o Firebase direto do navegador.
"""
import http.server
import os
import socketserver
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".json": "application/json",
    }

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[online] %s\n" % (fmt % args))


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"BO1 Zombies — Modo Online: http://0.0.0.0:{PORT}")
    sys.stdout.flush()
    httpd.serve_forever()
