from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from ruamel.yaml import YAML

yaml = YAML()

def load_config():
    try:
        config.load_incluster_config()
    except ConfigException:
        try:
            config.load_kube_config()
        except ConfigException as err:
            raise err

class NamespaceManager():
    def __init__(self):
        self.client = client.CoreV1Api()

    def get_client_namespaces(self):
        namespaces_list = self.client.list_namespace()
        namespaces = [item.metadata.name for item in namespaces_list.items if item.metadata.name.isdigit()]
        return namespaces

def main():
    ns_client = NamespaceManager()
    namespaces = ns_client.get_client_namespaces()

    route_namespace = {
        'inputs': ['logs_with_metadata'],
        'type': 'route',
        'route': {},
        'reroute_unmatched': False
    }

    with open('/etc/vector/agent.yaml', 'r') as config_file:
        vector_config = yaml.load(config_file)

    if 'transforms' not in vector_config:
        vector_config['transforms'] = {}

    if 'sinks' not in vector_config:
        vector_config['sinks'] = {}

    for ns in namespaces:
        env = ns
        route_namespace['route'][f'env_{env}'] = f'.kubernetes.pod_namespace == "{env}"'
        vector_config['sinks'][f'env_{env}'] = {
            'type': 'vector',
            'inputs': [f'route_namespace.env_{env}'],
            'address': f'{env}-0.hosting.luminance.com:3150'
        }

        vector_config['transforms']['route_namespace'] = route_namespace

        with open('/etc/vector/agent.yaml', 'w') as config_file:
            yaml.dump(vector_config, config_file)

        print("Vector configuration updated successfully.")

if __name__ == "__main__":
    main()
