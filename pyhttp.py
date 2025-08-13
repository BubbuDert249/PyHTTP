version = "1.2.1"
import socket
import os
import string
import sys

py_version = string.split(sys.version, ' ')[0]

STOP_SERVER = False

def listdir(path):
    try:
        names = os.listdir(path)
    except:
        return "<html><body><h1>Can't list directory</h1></body></html>"
    names.sort()
    r = "<html><body><h1>Directory listing</h1><ul>"
    for name in names:
        r = r + '<li><a href="/' + name + '">' + name + '</a></li>'
    r = r + "</ul></body></html>"
    return r

def readfile(path):
    try:
        f = open(path, "rb")
        data = f.read()
        f.close()
        return data
    except:
        return None

def content_type_from_path(path):
    ext_map = {
        ".html": "text/html",
        ".htm": "text/html",
        ".txt": "text/plain",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".css": "text/css",
        ".js": "application/javascript"
    }
    dot = string.rfind(path, ".")
    if dot == -1:
        return "application/octet-stream"
    ext = path[dot:].lower()
    return ext_map.get(ext, "application/octet-stream")

def serve(conn, path):
    try:
        req = conn.recv(1024)
        if not req:
            return
        parts = string.split(req, "\r\n")
        if len(parts) < 1:
            return
        first = parts[0]
        words = string.split(first)
        if len(words) < 2:
            return
        method = words[0]
        target = words[1]

        if target == "/":
            index = path + "/index.html"
            try:
                f = open(index)
                f.close()
                target = "/index.html"
            except:
                pass

        full = path + "/" + target[1:]
        try:
            st = os.stat(full)
        except:
            st = None

        if st and (st[0] & 0o170000) == 0o040000:  # directory
            body = listdir(full)
            header = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
            conn.send(header + body)
        else:
            data = readfile(full)
            if data:
                ctype = content_type_from_path(full)
                header = "HTTP/1.0 200 OK\r\nContent-Type: %s\r\n\r\n" % ctype
                conn.send(header + data)
            else:
                body = "<html><body><h1>404 Not Found</h1></body></html>"
                header = "HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
                conn.send(header + body)
        print "Visited:", target
    except:
        print "Error in request"

def main():
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = string.atoi(sys.argv[1])
        except:
            port = 8000

    print "PyHTTP", version, "on Python", py_version
    print "Serving on port", port
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen(1)
        while 1:
            try:
                conn, addr = s.accept()
                serve(conn, os.getcwd())
                conn.close()
            except KeyboardInterrupt:
                print "\nServer stopped by Ctrl+C"
                break
    except:
        print "Server error"
        sys.exit(1)

main()
