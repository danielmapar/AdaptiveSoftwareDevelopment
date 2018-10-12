import docker
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

tls_config_node = docker.tls.TLSConfig(
  client_cert=('/Users/daniel/.docker/machine/machines/node/cert.pem', '/Users/daniel/.docker/machine/machines/node/key.pem')
)
node = docker.DockerClient(base_url='192.168.99.101:2376', tls=tls_config_node)

tls_config_master = docker.tls.TLSConfig(
  client_cert=('/Users/daniel/.docker/machine/machines/master/cert.pem', '/Users/daniel/.docker/machine/machines/master/key.pem')
)
master = docker.DockerClient(base_url='192.168.99.100:2376', tls=tls_config_master)

nodes_list = [node, master]

# get all NodeIDs in swarm
nodes = {}
print("Nodes:")
for entry in nodes_list:
    entry = entry.info()
    nodes[entry["Swarm"]["NodeID"]] = entry["Swarm"]["NodeAddr"]
    print('''\t NodeID: {} '''.format(entry["Swarm"]["NodeID"], ))


# list all the services
services = {}
print("Services:")
for service in master.services.list():
    service = service.attrs;
    services[service["Spec"]["Name"]] = {"name": service["Spec"]["Name"], "tasks": []}
    print('''\t name: {}, version: {}, replicas: {}  '''.format(
        service["Spec"]["Name"],
        service["Version"]["Index"],
        service["Spec"]["Mode"]["Replicated"]["Replicas"]))
