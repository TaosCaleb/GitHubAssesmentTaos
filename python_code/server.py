#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json 
import requests as req
import base64
import os

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        print("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        try:
            with open("auth-vals.json") as auth_file:
                auth = json.load(auth_file)
                api_key = auth["api_token"]
                target_user = auth["target_user"]
                if not api_key:
                    raise Exception("API_TOKEN not set")
                if not target_user:
                    raise Exception("TARGET_USER not set")
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
            #         str(self.path), str(self.headers), post_data.decode('utf-8'))
            payload = json.loads(post_data.decode('utf-8'))
            if "action" in payload and "repository" in payload:
                action = payload["action"]
                repo = payload["repository"]
                
                logging.info("A new repo {} has been {}".format(repo["full_name"], action))
                if action == "created":
                    logging.info("Adding protection to master branch in repo {}".format(repo["full_name"]))
                    with open("./README.md", "r") as f:
                        logging.info("Creating readme file")
                        file_data = f.read()
                        if "contents_url" in repo:
                            file_path = "README.md"
                            contents_url = repo["contents_url"].replace("{+path}",file_path)
                            logging.info("Using contents_url {}".format(contents_url))
                            b64_encoded_fdata = base64.b64encode(file_data.encode("utf-8"))
                            readme_file = str(b64_encoded_fdata, "utf-8")
                            logging.info("file content: {}".format(readme_file))
                            headers = {
                                    "Authorization": "token {}".format(api_key),
                                    "Content-Type": "application/json",
                                    "Accept": "application/vnd.github.v3+json"
                                }
                            put_body={
                                "branch": "master",
                                "path": file_path,
                                "message": "Adding initial README.md file",
                                "content": readme_file
                            }
                            with req.put(contents_url, data=json.dumps(put_body), headers=headers) as r:
                                if r.ok:
                                    logging.info("Created readme file")
                                    logging.info("Creating branch protection")
                                    branches_payload_body={
                                            "required_status_checks":
                                            {"strict":True,
                                            "contexts":["contexts"]},
                                            "enforce_admins":True,
                                            "required_pull_request_reviews":
                                            {"dismissal_restrictions":
                                            {"users":["users"],
                                                "teams":["teams"]},
                                            "dismiss_stale_reviews":True,
                                            "require_code_owner_reviews":True,
                                            "required_approving_review_count":1},
                                            "restrictions":
                                            {"users":["users"],
                                            "teams":["teams"],
                                            "apps":["apps"]}}
                                    if "branches_url" in repo:
                                            branches_url = repo["branches_url"].replace("{/branch}", "/master/protection")
                                            
                                            with req.put(headers=headers, data=json.dumps(branches_payload_body), url=branches_url) as r:
                                                logging.info("Using branch url {}".format(branches_url))
                                                if r.ok:
                                                    logging.info("headers {}".format(headers))
                                                    logging.info("Created branch protection")
                                                    self._set_response()
                                                    if "issues_url" in repo:
                                                        issues_url = repo["issues_url"].replace("{/number}","")
                                                        logging.info("Using issues url {}".format(issues_url))
                                                        issues_payload_body = {
                                                            "title": "Repo master branch protected",
                                                            "body": "@{}".format(target_user)
                                                    
                                                        }
                                                        with req.post(headers=headers, data=json.dumps(issues_payload_body), url=issues_url) as r:
                                                            if r.ok:
                                                                logging.info("Created issue")
                                                            else:
                                                                logging.info("Failed to created issue {}".format(r.content))
                                                else:
                                                    logging.info("Failed to create readme file {}".format(r.content))
                                                    r.raise_for_status()
                                else:
                                    logging.info("Failed to create readme file {}".format(r.content))
                                    r.raise_for_status()
                        else:
                            raise Exception("Content_url not found in payload")             
                    
            else:
                logging.info("No action in payload")
                self._set_response()
        except Exception as e:
                    raise Exception("There was an exception {}".format(e))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()