# Istio templates files generated in python 

A simple script to generate YAMLs files for your kubernetes service:

* Virtual Service
* Destination Rule
* Gateway
* Service Entry

Key features:

* Generates proper Istio API versioning
* Creates consistent naming conventions
* Sets up basic configurations that you can customize
* Organizes files in a dedicated directory
* Includes common best practices for each resource type

Just use it like this :

```bash

    $ python templ-gen.py generate --service my-app --namespace cms --domain my-domain.com
```
The necessary libraries to run use this script are in the **requirements.txt** file.

```bash

    $ pip install -r requirements.txt
```

Take a look at the usage doing so :

```bash

    $ python templ-gen.py
    usage: templ-gen.py [-h] --service SERVICE [--namespace NAMESPACE] [--domain DOMAIN] {generate,delete,list}
```