import yaml
import os
import glob
import argparse
from typing import Dict, Any

class IstioTemplateGenerator:
    def __init__(self):
        self.base_path = "templ-gen"
        
    def create_virtual_service(self, name: str, namespace: str, host: str, domain: str = None) -> Dict[Any, Any]:
        service_host = f"{host}.{domain}" if domain else host
        return {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "VirtualService",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "hosts": [service_host],
                "http": [{
                    "route": [{
                        "destination": {
                            "host": service_host,
                            "subset": "v1"
                        },
                        "weight": 100
                    }]
                }]
            }
        }

    def create_destination_rule(self, name: str, namespace: str, host: str, domain: str = None) -> Dict[Any, Any]:
        service_host = f"{host}.{domain}" if domain else host
        return {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "DestinationRule",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "host": service_host,
                "trafficPolicy": {
                    "loadBalancer": {
                        "simple": "ROUND_ROBIN"
                    }
                },
                "subsets": [{
                    "name": "v1",
                    "labels": {
                        "version": "v1"
                    }
                }]
            }
        }

    def create_gateway(self, name: str, namespace: str, domain: str = None) -> Dict[Any, Any]:
        hosts = [f"*.{domain}"] if domain else ["*"]
        return {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "Gateway",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "istio": "ingressgateway"
                },
                "servers": [{
                    "port": {
                        "number": 80,
                        "name": "http",
                        "protocol": "HTTP"
                    },
                    "hosts": hosts
                }]
            }
        }

    def create_service_entry(self, name: str, namespace: str, host: str, domain: str = None) -> Dict[Any, Any]:
        service_host = f"{host}.{domain}" if domain else f"{host}.example.com"
        return {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "ServiceEntry",
            "metadata": {
                "name": name,
                "namespace": namespace
            },
            "spec": {
                "hosts": [service_host],
                "ports": [{
                    "number": 443,
                    "name": "https",
                    "protocol": "HTTPS"
                }],
                "resolution": "DNS",
                "location": "MESH_EXTERNAL"
            }
        }

    def generate_templates(self, service_name: str, namespace: str = "default", domain: str = None):
        """Generate all Istio templates for a service"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        templates = {
            "virtual-service": self.create_virtual_service(
                f"{service_name}-vs", 
                namespace, 
                service_name,
                domain
            ),
            "destination-rule": self.create_destination_rule(
                f"{service_name}-dr",
                namespace,
                service_name,
                domain
            ),
            "gateway": self.create_gateway(
                f"{service_name}-gateway",
                namespace,
                domain
            ),
            "service-entry": self.create_service_entry(
                f"{service_name}-se",
                namespace,
                service_name,
                domain
            )
        }

        # Save each template to a separate YAML file
        for template_type, content in templates.items():
            filename = f"{self.base_path}/{service_name}-{template_type}.yaml"
            with open(filename, 'w') as f:
                yaml.dump(content, f, default_flow_style=False)
            print(f"Generated {filename}")
            
        # Print summary of domain settings
        if domain:
            print(f"\nDomain configuration:")
            print(f"- Service FQDN: {service_name}.{domain}")
            print(f"- Gateway hosts: *.{domain}")
        else:
            print("\nNo domain specified, using default service names")

    def delete_templates(self, service_name: str) -> bool:
        """Delete all Istio template files for a specific service name."""
        files_pattern = os.path.join(self.base_path, f"{service_name}-*.yaml")
        files_to_delete = glob.glob(files_pattern)
        
        if not files_to_delete:
            print(f"No template files found for service: {service_name}")
            return False
        
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except OSError as e:
                print(f"Error deleting {file_path}: {e}")
                return False
                
        return True

    def list_templates(self, service_name: str = None):
        """List all template files, optionally filtered by service name."""
        if service_name:
            pattern = os.path.join(self.base_path, f"{service_name}-*.yaml")
        else:
            pattern = os.path.join(self.base_path, "*.yaml")
            
        files = glob.glob(pattern)
        
        if not files:
            print("No template files found" + (f" for service: {service_name}" if service_name else ""))
            return
            
        print("\nExisting templates:")
        for file_path in files:
            print(f"- {os.path.basename(file_path)}")

def main():
    parser = argparse.ArgumentParser(description='Istio Template Generator')
    parser.add_argument('action', choices=['generate', 'delete', 'list'],
                      help='Action to perform (generate, delete, or list templates)')
    parser.add_argument('--service', '-s', required=True,
                      help='Service name')
    parser.add_argument('--namespace', '-n', default='default',
                      help='Kubernetes namespace (default: default)')
    parser.add_argument('--domain', '-d',
                      help='Domain name (e.g., mon-domaine.com)')
    
    args = parser.parse_args()
    generator = IstioTemplateGenerator()
    
    if args.action == 'generate':
        generator.generate_templates(args.service, args.namespace, args.domain)
    elif args.action == 'delete':
        generator.delete_templates(args.service)
    elif args.action == 'list':
        generator.list_templates(args.service)

if __name__ == "__main__":
    main()