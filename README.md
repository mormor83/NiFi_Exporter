# NiFi Exporter

Prometheus exporter for Nifi metrics written in python  
Data is scraped by [prometheus](https://prometheus.io).

## Installation

### Docker 

Run the following to build the image using Docker-compose

      docker-compose up -d --build
 
## Configuration

nifi_exporter uses environment variables for configuration.
Settings:

Environment variable|default|description
--------------------|-------|------------
BASE_URL|None| Use the following format https:// <Nifi Domain> : <Cluster port>
USERNAME|None|Please make sure you have the relevant policies 
PASSWORD|None|
  
  
## Metrics

All metrics are prefixed with "nifi_".


### Nodes
metric | description
-------| ------------
nifi_nodes_status| General status per node
nifi_node_activeThreadCount| Active Thread Count
nifi_node_queuedItems|Each node queued items

### Cluster
metric | description
-------| ------------
nifi_cluster_activeThreadCount |
nifi_cluster_terminatedThreadCount |
nifi_cluster_flowFilesQueued |
nifi_cluster_bytesQueued |
nifi_cluster_runningCount|
nifi_cluster_stoppedCount|
nifi_cluster_invalidCount|

### Processor
metric | description
-------| ------------
nifi_amount_items_queued | Count the number of queued files per PG









