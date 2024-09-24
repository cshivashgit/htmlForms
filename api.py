import json
import os
from jinja2 import Environment, FileSystemLoader

def get_flavour_data(flavour):
    if flavour == "mini" :
        return 1, 2
    elif flavour == "medium" :
        return 2, 4
    elif flavour == "large" :
        return 2, 8
    elif flavour == "xlarge" :
        return 4,16
    
        
def create_vm(data):
    print(f"<create_vm>: Received data : {data}")
    context = json.loads(data)
    print("<create_vm>: Customer Name ", context["customer_name"])
    context["vpc_name"] = context["vpc_name"].lower()
    context["vm_name"] = context["vm_name"].lower()
    context["data_volume_name"] = context["vpc_name"]+context["vm_name"]
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('templates'))
    # Load the template
    
    if context["os"] == "windows" :
        template = env.get_template('vmK8sWin.j2')
    elif context["os"] == "ubuntu2204" :
        context["url"] = "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"                
        template = env.get_template('vmK8sLinux.j2')
    else :
        context["url"] = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2"        
        template = env.get_template('vmK8sLinux.j2')
    
    if context["flavour"] != None:
        context["cpu"], context["ram"] = get_flavour_data(context["flavour"])

    context["ram"] = str(context["ram"])+"G"    
    context["storage"] = str(context["storage"])+"Gi"
    print(context)

    # Render the template with context
    config_content = template.render(context)
    
    fileName = '/tmp/vm_creation.yaml'
    with open(fileName, 'w+') as config_file:
        config_file.write(config_content)
    
    os.system(f"kubectl apply -f {fileName}")
    
        
    
def create_vpc(data):
    context = json.loads(data)
    print(f"<create_vpc>: Received data : {data}")
    print("<create_vpc>: Customer Name: ", context["customer_name"])
    context["pvClaims"] = 5
    context["vpc_name"] = context["vpc_name"].lower()
    context["customer_name"] = context["customer_name"].lower()
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('templates'))
    # Load the template
    template = env.get_template('vpcK8s.j2')
    # Render the template with context
    config_content = template.render(context)
    
    fileName = '/tmp/vpcK8s.yaml'
    with open(fileName, 'w+') as config_file:
        config_file.write(config_content)
    
    os.system(f"kubectl apply -f {fileName}")
    
    

def create_pod(data):
    print(f"<create_pod>: Received data : {data}")
    json_data = json.loads(data)
    print("<create_pod>: Customer Name ", json_data["customer_name"])
    
    os.system(f"kubectl apply -f {json_data["manifest_url"]}")