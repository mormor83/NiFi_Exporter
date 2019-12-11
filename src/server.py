from flask import Response, Flask, request , jsonify, render_template
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import  Gauge , Info
from helperFunc import *
import time
import os
import requests
import urllib3
import json
import csv
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Variables ###
CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

BASE_URL = os.environ['BASE_URL']
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']

app = Flask(import_name=__name__)

@app.route("/")
def hello():
    return "This is a prometheus exporter"

@app.route('/metrics', methods=['GET'])
def metrics():
  lst=[]
  #print (globals().keys())
  registry = CollectorRegistry()
  url=BASE_URL+"/nifi-api/access/token"
  token = getToken(url,USERNAME,PASSWORD  )


  #### ====  cluster nodes status ==== ####
  url=BASE_URL+"/nifi-api/controller/cluster"
  cluster = getCluster(url,token)
  for item in cluster:
    NodeName = {"instance":item['address']}
    nodeStatus =  Gauge('nifi_nodes_status','Nifi node status',NodeName.keys(),registry=registry)
    activeThreadCount=Gauge('nifi_node_activeThreadCount','Total number of activeThreadCount per node',NodeName.keys(),registry=registry)
    queuedItems = Gauge('nifi_node_queuedItems','Number of queud items per node',NodeName.keys(),registry=registry) 

    nodeStatus.labels(**NodeName).set(convertStatus(item['status']))
    lst.append(prometheus_client.generate_latest(nodeStatus))

    activeThreadCount.labels(**NodeName).set(item['activeThreadCount'])
    lst.append(prometheus_client.generate_latest(activeThreadCount))
    flow = float(item['queued'].rsplit(' ')[0].replace(',',''))
    queuedItems.labels(**NodeName).set(flow)
    lst.append(prometheus_client.generate_latest(queuedItems))

    registry = CollectorRegistry()

  #### ====  general cluster info ==== ####
  url=BASE_URL+"/nifi-api/flow/about"
  flowAbout = about(url,token)
  nifiVersion = Info('nifi_cluster_version','This is the version',registry=registry)
  nifiVersion.info({"title":flowAbout['title'], "version":flowAbout['version'] , "timezone": flowAbout['timezone']})
  lst.append(prometheus_client.generate_latest(nifiVersion))

  #### ====  general cluster status ==== ####
  url=BASE_URL+"/nifi-api/flow/status"
  generalFlow = getFlow(url,token)
  with open('cluster_status.csv',mode="r") as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      line_num = 0
      for line in csv_reader:
          if line_num != 0:
                if line[0] in globals().keys():
                      del globals()[line[0]]
                globals()[line[0]] = Gauge(line[1],line[2],registry=registry)
                globals()[line[0]].set(generalFlow[line[0]])
                lst.append(prometheus_client.generate_latest(globals()[line[0]]))
          line_num +=1
  csv_file.close


  url = BASE_URL+"/nifi-api/process-groups/root/process-groups"
  nifi_group = getProcessorFlow(url,token)
  for PG in nifi_group:
    processorName = {"processorName": PG['component']['name']}
    processorQueue = Gauge('nifi_amount_items_queued','Total number of items queued by the processor',processorName.keys(), registry=registry)
    aggregateSnapshot_queued=float(PG['status']['aggregateSnapshot']['queued'].rsplit(' ')[0].replace(',',''))
    processorQueue.labels(**processorName).set(aggregateSnapshot_queued)
    lst.append(prometheus_client.generate_latest(processorQueue))

    registry=CollectorRegistry()

  return Response(lst,mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
  app.debug = True
  app.run(host='127.0.0.1')
