from flask import Flask, Response
from helperFunc import *
import os

app = Flask(import_name=__name__)
CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

@app.before_request
def before_request_func():
     #Login to Nifi
    BASE_URL = os.environ['BASE_URL']
    USERNAME = os.environ['USERNAME']
    PASSWORD = os.environ['PASSWORD']
    nifiLogin(BASE_URL,USERNAME,PASSWORD)

@app.route("/")
def hello():
    return "This is a prometheus exporter"

@app.route('/metrics', methods=['GET'])
def metrics():
    lst=[]

    # Get Cluster Nodes Details
    lst += clusterNodeStatus()

    # Get Cluster Detatils
    lst += clusterStatusInfo()

    # Get Process Groups Details
    lst += processGroupInfo()

    # Get Connections Queue Size
    if os.environ.get('CONNECTIONS_QUEUE') == 'True':
        lst += connectionsInfo()

    return Response(lst,mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
  app.debug = True
  app.run(host='127.0.0.1')
