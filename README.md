#monapi


**Monapi** is in its conception a project for **Universidad de Mendoza** (University of Mendoza) **Monitoreo y Gestión de Redes**  (Monitoring and Network Management) subject.


##Introduction

Monapi allows you to monitor process running in host by requesting an API.

It is built in Python using two great tools: [**Flask**](http://flask.pocoo.org/) as framework and [**psutil**](https://github.com/giampaolo/psutil).

##Usage

Monapi allows you to make HTTP requests using its methods in a RESTful way.

You can:

* **Retrieve information about all process in host**

`curl -XGET <hostname:port>/api/<api_version>/process`

* **Launch a new process**

`curl -XPOST <hostname:port>/api/<api_version>/process -d '{"path": "/path/to/exec", "params": "-as -in /shell/format --optional"}'`

* **Retrieve information about a particular precess by PID**

`curl -XGET <hostname:port>/api/<api_version>/process/<pid>`
 
* **KIll a process**

`curl -XGET <hostname:port>/api/<api_version>/process/<pid>/kill`

* **Renice a process (root privilegies)**

`curl -XGET <hostname:port>/api/<api_version>/process/<pid>/renice` increase by 1 the actual value.
`curl -XGET <hostname:port>/api/<api_version>/process/<pid>/renice/<value>` set the value passed.

* **Retrieve process status**

`curl -XGET <hostname:port>/api/<api_version>/process/<pid>/status`

* **Retrieve connections opened by process**

`curl -XGET <hostname:port>/api/<api_version>/process/<pid>/connections`

* **Retrieve all connections opened in host**

`curl -XGET <hostname:port>/api/<api_version>/connections`



##TODO
* Add I/O monitoring
* Improve connections monitoring
* Improve documentation --> Usage and return data 
* Memory monitoring
