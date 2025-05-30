import socketserver
import http.server
import urllib.request
import urllib.error
import ssl
PORT = 9097

class MyProxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = self.path[1:]
        print(f"Requesting: {url}")
        
        try:
            # Create SSL context that doesn't verify certificates
            # WARNING: This is less secure but needed for some sites
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create request with custom headers to mimic a real browser
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            req.add_header('Accept-Language', 'en-US,en;q=0.5')
            req.add_header('Accept-Encoding', 'gzip, deflate')
            req.add_header('Connection', 'keep-alive')
            
            # Open URL with SSL context
            if url.startswith('https://'):
                response = urllib.request.urlopen(req, context=ssl_context)
            else:
                response = urllib.request.urlopen(req)
            
            # Send successful response
            self.send_response(200)
            
            # Copy headers from the original response
            for header, value in response.headers.items():
                if header.lower() not in ['connection', 'transfer-encoding']:
                    self.send_header(header, value)
            
            self.end_headers()
            
            # Copy the content
            self.copyfile(response, self.wfile)
            response.close()
            
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            self.send_error(e.code, e.reason)
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            self.send_error(500, f"URL Error: {e.reason}")
        except Exception as e:
            print(f"General Error: {str(e)}")
            self.send_error(500, f"General Error: {str(e)}")

httpd = socketserver.ForkingTCPServer(('', PORT), MyProxy)
print("Now serving at " + str(PORT))
print("Access URLs like: http://localhost:9097/https://www.example.com")
httpd.serve_forever()