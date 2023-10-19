#!/usr/bin/env python3

import os
import sys
import socket
import http.server


class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
  def do_GET(self) -> None:
    self.send_response(200)
    self.send_header("Content-Type", "text/plain")
    self.end_headers()
    self.wfile.write(os.uname()[1].encode())


def _get_best_family(*address):
  infos = socket.getaddrinfo(
      *address,
      type=socket.SOCK_STREAM,
      flags=socket.AI_PASSIVE,
  )
  family, type, proto, canonname, sockaddr = next(iter(infos))
  return family, sockaddr


def test(HandlerClass=http.server.BaseHTTPRequestHandler,
         ServerClass=http.server.ThreadingHTTPServer,
         secure=False, port=8000, bind=None):

  ServerClass.address_family, addr = _get_best_family(bind, port)
  HandlerClass.protocol_version = "HTTP/1.0"
  with ServerClass(addr, HandlerClass) as httpd:
    host, port = httpd.socket.getsockname()[:2]
    url_host = f'[{host}]' if ':' in host else host

    if secure:
      import ssl

      if not os.path.exists("/tmp/http-server_key.pem") or not os.path.exists("/tmp/http-server_cert.pem"):
        os.system(f"""
          echo -e "XX\nXX\nXX\nXX\n\nexample.com\n" | \
            openssl req -x509 \
              -newkey rsa:4096 \
              -keyout "/tmp/http-server_key.pem" \
              -out "/tmp/http-server_cert.pem" \
              -days 36500 \
              -sha256 -nodes &>/dev/null
        """)

      context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
      context.load_cert_chain(
          '/tmp/http-server_cert.pem', '/tmp/http-server_key.pem')
      httpd.socket = context.wrap_socket(httpd.socket)

    print(
        f"Serving HTTP{'S' if secure else ''} on {host} port {port} "
        f"(http{'s' if secure else ''}://{url_host}:{port}/) ..."
    )

    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      print("\nKeyboard interrupt received, exiting.")
      sys.exit(0)


if __name__ == "__main__":
  import argparse
  import contextlib

  parser = argparse.ArgumentParser()
  parser.add_argument('-b', '--bind', metavar='ADDRESS',
                      help='bind to this address '
                           '(default: all interfaces)')
  parser.add_argument('-d', '--directory', default=os.getcwd(),
                      help='serve this directory '
                           '(default: current directory)')
  parser.add_argument('port', default=8000, type=int, nargs='?',
                      help='bind to this port '
                           '(default: %(default)s)')
  parser.add_argument('-s', '--secure', default=False, action='store_true',
                      help='use https (self signed certificate)')
  args = parser.parse_args()

  class DualStackServer(http.server.ThreadingHTTPServer):
    def server_bind(self):
      with contextlib.suppress(Exception):
        self.socket.setsockopt(
            socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
      return super().server_bind()

    def finish_request(self, request, client_address):
      self.RequestHandlerClass(request, client_address, self,
                               directory=args.directory)

  test(
      HandlerClass=HTTPRequestHandler,
      ServerClass=DualStackServer,
      port=args.port,
      bind=args.bind,
      secure=args.secure
  )
