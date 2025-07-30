import sys
import os
import socket

STOP_FILE = "pyhttp.stop"

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

def serve(conn, path):
    try:
        req = conn.recv(1024)
        if not req:
            return
        parts = string.split(req, "\r\n")
        first = parts[0]
        words = string.split(first)
        if len(words) < 2:
            return
        method = words[0]
        target = words[1]

        if target == "/":
            index = os.path.join(path, "index.html")
            if os.path.exists(index):
                target = "/index.html"

        full = os.path.join(path, target[1:])
        if os.path.isdir(full):
            body = listdir(full)
            conn.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.send(body)
        else:
            data = readfile(full)
            if data:
                conn.send("HTTP/1.0 200 OK\r\n\r\n")
                conn.send(data)
            else:
                conn.send("HTTP/1.0 404 Not Found\r\n\r\n404 Not Found")
        print "Visited:", target
    except:
        print "Error in request"

def main():
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            port = 8000
    else:
        port = 8000

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.listen(1)
        print "Serving on port", port
        print "To stop the server, create a file named 'pyhttp.stop'"
        while 1:
            if os.path.exists(STOP_FILE):
                print "Server stopped"
                os.remove(STOP_FILE)
                break
            conn, addr = s.accept()
            serve(conn, os.getcwd())
            conn.close()
    except:
        print "Server error"
        sys.exit(1)

import string
main()
