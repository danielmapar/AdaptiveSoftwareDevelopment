import json
import requests
import time
from urllib.request import urlopen
import socket
import ssl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cert_manager = ('/Users/daniel/.docker/machine/machines/master/cert.pem', '/Users/daniel/.docker/machine/machines/master/key.pem')
cert_node = ('/Users/daniel/.docker/machine/machines/node/cert.pem', '/Users/daniel/.docker/machine/machines/node/key.pem')

scontext_manager = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
scontext_manager.load_cert_chain(cert_manager[0], cert_manager[1])

scontext_node = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
scontext_node.load_cert_chain(cert_node[0], cert_node[1])

# here we assume you tunneled port 4000 of all swarm nodes to ports on your local machine
nodes_list = [("192.168.99.100:2376", scontext_manager), ("192.168.99.101:2376", scontext_node)]

# the address your managers nodes REST API is listening
manager = "192.168.99.100:2376"

# upper and lower cpu usage thresholds where scaling should happen on
cpu_upper_threshold = int(input("Enter a number from 0 to 100 for the CPU upper threshold: ")) / 100 # 0.50
cpu_lower_threshold = int(input("Enter a number from 0 to 100 for the CPU lower threshold: ")) / 100 # 0.10

# p, i, d parameters to be tested
proportional_gain = float(input("Enter a number for Kp: "))
integral_gain = float(input("Enter a number for Ki: "))
derivative_gain = float(input("Enter a number for Kd: "))

# time interval between each avg cpu usage calculations
interval = int(input("Enter a number for the interval: "))

# this is taken directly from docker client:
#   https://github.com/docker/docker/blob/28a7577a029780e4533faf3d057ec9f6c7a10948/api/client/stats.go#L309
def calculate_cpu_percent(d):
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                   float(d["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent

# get_tasks functions gets a service in the form of {"name": <service-name>, "tasks": []} and fills the tasks.
def get_tasks(service):
    service["tasks"] = []
    with urlopen(
            'https://{manager}/tasks?filters={{"service":{{"{service}":true}},"desired-state":{{"running":true}}}}'.format(
                manager=manager, service=service["name"]), context=scontext_manager) as url:
        data = json.loads(url.read().decode())
        print("{service} tasks:".format(service=service["name"]))
        for task in data:
            if task["Status"]["State"] == "running":
                container_id = task["Status"]["ContainerStatus"]["ContainerID"]
            else:
                continue
            node_id = task["NodeID"]
            service["tasks"].append({"ContainerID": container_id, "NodeID": node_id})
            print('''\t ContainerID: {}, NodeID: {} '''.format(container_id, node_id))

# scale functions gets a service in the form of {"name": <service-name>, "tasks": []} and number of desired replicas
# and update the service accordingly
def scale(service, replicas):
    print("scaling triggered...")
    # get the service - we need the version of the service object
    with urlopen("https://{manager}/services/{service}".format(manager=manager, service=service["name"]),
    context=scontext_manager) as url:
        data = json.loads(url.read().decode())
        version = data["Version"]["Index"]

        # the whole spec object should be sent to the update API,
        # otherwise the missing values will be replaced by default values
        spec = data["Spec"]
        spec["Mode"]["Replicated"]["Replicas"] = replicas

        r = requests.post("https://{manager}/services/{service}/update?version={version}".format(manager=manager,
                                                                                                service=service["name"],
                                                                                                version=version),
                          data=json.dumps(spec), verify=False, cert=cert_manager)
        if r.status_code == 200:
            get_tasks(service)
        else:
            print(r.reason, r.text)


# get all NodeIDs in swarm
nodes = {}
print("Nodes:")
for node in nodes_list:
    node_ip = node[0]
    node_context = node[1]
    with urlopen("https://{node}/info".format(node=node_ip), context=node_context) as url:
        data = json.loads(url.read().decode())
        nodes[data["Swarm"]["NodeID"]] = (node_ip, node_context)
        print('''\t NodeID: {} '''.format(
            data["Swarm"]["NodeID"], ))

# list all the services
services = {}
with urlopen("https://{manager}/services".format(manager=manager), context=scontext_manager) as url:
    data = json.loads(url.read().decode())
    print("Services:")
    for service in data:
        services[service["Spec"]["Name"]] = {"name": service["Spec"]["Name"], "tasks": []}
        print('''\t name: {}, version: {}, replicas: {}  '''.format(
            service["Spec"]["Name"],
            service["Version"]["Index"],
            service["Spec"]["Mode"]["Replicated"]["Replicas"]))

# get the tasks running on our swarm cluster
for service_name, service in services.items():
    get_tasks(service)

# cpu usage api is not fast. be patient!
# here we consistently get the cpu usage of all the web-workers and calculate the average

# https://en.wikipedia.org/wiki/Proportional_control
# e(t) = SP - PV
def e(sp, pv):
    return sp - pv

cpu_usage_avg_prev = None
cpu_usage_avg_arr = []

while True:
    cpu_usages = []

    service_in_analysis_name = "getstartedlab_web"

    get_tasks(services[service_in_analysis_name])

    for task in services[service_in_analysis_name]["tasks"]:
        with urlopen('https://{node}/containers/{containerID}/stats?stream=false'.format(
                node=nodes[task["NodeID"]][0], containerID=task["ContainerID"]), context=nodes[task["NodeID"]][1]) as url:
            data = json.loads(url.read().decode())
            cpu_usages.append(calculate_cpu_percent(data))

    cpu_usage_avg = sum(cpu_usages) / len(cpu_usages)
    cpu_usage_avg_arr.append(cpu_usage_avg)

    if cpu_usage_avg_prev == None:
        cpu_usage_avg_prev = cpu_usage_avg

    set_point = (cpu_upper_threshold + cpu_lower_threshold) / 2

    # PID Controller

    # Proportional gain - e(t)
    output_proportional_controller = proportional_gain * e(set_point, cpu_usage_avg)
    print("Output Proportional Controller: {0}".format(output_proportional_controller))

    # Integral gain (using last five cpu usages) -> Sum
    output_integral_controller = integral_gain * (sum(cpu_usage_avg_arr[-interval: ]) * interval)
    print("Output Integral Controller: {0}".format(output_integral_controller))

    # Derivative gain: (e(k)-e(k-1))/T
    output_derivative_controller = derivative_gain * (e(set_point, cpu_usage_avg) - e(set_point, cpu_usage_avg_prev) / interval)
    print("Output Derivative Controller: {0}".format(output_derivative_controller))

    controller_output = abs(round(output_proportional_controller + output_integral_controller + output_derivative_controller))

    print("Controller final output: {0}".format(controller_output))

    if controller_output > 0 and controller_output <= 15:
        scale_num = controller_output
    elif controller_output > 15:
        scale_num = 15
    else:
        scale_num = 1

    print("Previous CPU Usage (avg): {0:.2f}%".format(cpu_usage_avg_prev * 100))
    print("CPU Usage (avg): {0:.2f}%".format(cpu_usage_avg * 100))
    print("CPU Setpoints are currently from {low:.2f}% to {high:.2f}%".format(low=cpu_lower_threshold * 100, high=cpu_upper_threshold * 100))
    print("Scale parameter value: ", scale_num)
    print("-------------")

    cpu_usage_avg_prev = cpu_usage_avg

    if cpu_usage_avg > cpu_upper_threshold:
        # scale up
        task_count = len(services[service_in_analysis_name]["tasks"])
        scale(services[service_in_analysis_name], task_count + scale_num)
    elif cpu_usage_avg < cpu_lower_threshold:
        # scale down
        task_count = len(services[service_in_analysis_name]["tasks"])
        if task_count > 1:
            scale(services[service_in_analysis_name], task_count - scale_num)
    else:  # do nothing
        pass

    # block the main thread for <interval> seconds
    time.sleep(interval)
