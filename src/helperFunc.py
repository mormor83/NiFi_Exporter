import nipyapi
from nipyapi.nifi.models import ProcessGroupEntity, ClusterEntity
from prometheus_client.core import CollectorRegistry
from prometheus_client import  Gauge , Info
import prometheus_client

from typing import List
import urllib3



def nifiLogin(BASE_URL: str,USERNAME: str,PASSWORD: str):
    urllib3.disable_warnings()
    nipyapi.config.nifi_config.host = f'{BASE_URL}/nifi-api'
    nipyapi.config.nifi_config.verify_ssl = False
    nipyapi.security.service_login(username=USERNAME,password=PASSWORD)


def clusterNodeStatus():
    lst = []
    cluster: ClusterEntity = nipyapi.system.get_cluster()

    for node in cluster.cluster.nodes:
        registry = CollectorRegistry()
        node_name = {"instance":node.address}

        node_status = Gauge('nifi_nodes_status', 'Nifi node status', node_name.keys(), registry=registry)
        status = 1 if node.status == 'CONNECTED' else 0
        node_status.labels(**node_name).set(status)
        lst.append(prometheus_client.generate_latest(node_status))

        active_thread_count = Gauge('nifi_node_activeThreadCount', 'Total number of activeThreadCount per node', node_name.keys(), registry=registry)
        active_thread_count.labels(**node_name).set(node.active_thread_count)
        lst.append(prometheus_client.generate_latest(active_thread_count))

        queued_items = Gauge('nifi_node_queuedItems','Number of queud items per node', node_name.keys(), registry=registry)
        queue = int(node.queued.split(' ')[0])
        queued_items.labels(**node_name).set(queue)
        lst.append(prometheus_client.generate_latest(queued_items))

    return lst

def clusterStatusInfo():
    lst = []
    registry = CollectorRegistry()

    about = nipyapi.nifi.apis.flow_api.FlowApi().get_about_info().about
    nifi_version = Info('nifi_cluster_version','This is the version',registry=registry)
    nifi_version.info({"title":about.title, "version":about.version , "timezone":about.timezone})
    lst.append(prometheus_client.generate_latest(nifi_version))

    flow_status = nipyapi.nifi.apis.flow_api.FlowApi().get_controller_status().controller_status

    active_thread_count = Gauge('nifi_cluster_activeThreadCount', 'General number of activeThreadCount', registry=registry)
    active_thread_count.set(flow_status.active_thread_count)
    lst.append(prometheus_client.generate_latest(active_thread_count))

    terminated_thread_count = Gauge('nifi_cluster_terminatedThreadCount', 'General terminatedThreadCount', registry=registry)
    terminated_thread_count.set(flow_status.terminated_thread_count)
    lst.append(prometheus_client.generate_latest(terminated_thread_count))

    flow_files_queued = Gauge('nifi_cluster_flowFilesQueued', 'flowFilesQueued', registry=registry)
    flow_files_queued.set(flow_status.flow_files_queued)
    lst.append(prometheus_client.generate_latest(flow_files_queued))

    bytes_queued = Gauge('nifi_cluster_bytesQueued','bytesQueued', registry=registry)
    bytes_queued.set(flow_status.bytes_queued)
    lst.append(prometheus_client.generate_latest(bytes_queued))

    running_count = Gauge('nifi_cluster_runningCount','runningCount', registry=registry)
    running_count.set(flow_status.running_count)
    lst.append(prometheus_client.generate_latest(running_count))

    stopped_count = Gauge('nifi_cluster_stoppedCount','stoppedCount', registry=registry)
    stopped_count.set(flow_status.stopped_count)
    lst.append(prometheus_client.generate_latest(stopped_count))

    invalid_count = Gauge('nifi_cluster_invalidCount','invalidCount', registry=registry)
    invalid_count.set(flow_status.invalid_count)
    lst.append(prometheus_client.generate_latest(invalid_count))

    return lst

def processGroupInfo():
    lst = []
    process_groups: List[ProcessGroupEntity] = nipyapi.nifi.ProcessGroupsApi().get_process_groups(id='root')

    for pg in process_groups.process_groups:
        registry = CollectorRegistry()
        processor_name = {"processor_name": pg.component.name}
        processor_queue = Gauge('nifi_amount_items_queued','Total number of items queued by the processor',processor_name.keys(), registry=registry)
        queue = int(pg.status.aggregate_snapshot.queued.split(' ')[0])
        processor_queue.labels(**processor_name).set(queue)
        lst.append(prometheus_client.generate_latest(processor_queue))

    return lst

def connectionsInfo():
    lst = []
    connections = nipyapi.canvas.list_all_connections(pg_id='root', descendants=True)

    for connection in connections:
        registry = CollectorRegistry()
        source_name = connection.status.aggregate_snapshot.source_name
        destination_name = connection.status.aggregate_snapshot.destination_name
        pg_name = list(nipyapi.canvas.get_process_group_status(pg_id=connection.source_group_id, detail='names').keys())[0]
        connection_name = {"connection_name": f'{source_name}_to_{destination_name}','processor_group':pg_name,'source_name':source_name,'destination_name':destination_name}
        connection_queue = Gauge('nifi_connection_queue','Queue size by connection',connection_name.keys(), registry=registry)
        queue = int(connection.status.aggregate_snapshot.queued_count)
        connection_queue.labels(**connection_name).set(queue)
        lst.append(prometheus_client.generate_latest(connection_queue))

    return lst

def controllerStatus():
    lst = []
    controller = nipyapi.nifi.apis.flow_api.FlowApi().get_controller_status().controller_status.to_dict()
    
    for k, v in controller.items():
        registry = CollectorRegistry()
        connection_queue = Gauge(k,k, registry=registry)
        if k == 'queued':
          connection_queue.set(int(v.split(' ')[0]))  
        else:
            connection_queue.set(v)
        lst.append(prometheus_client.generate_latest(connection_queue))

    return lst