# API Guide
For a great, concise overview of what a RESTful API looks like, read the first page of the 
[Github API documentation](http://developer.github.com/v3/).  
For an example of what potential customers have come to expect, see the 
[VMWare VShield API](http://www.vmware.com/pdf/vshield_51_api.pdf), the 
[OpenStack Quantum LBaaS API](https://wiki.openstack.org/wiki/Quantum/LBaaS/API_1.0),  or the 
[OpenStack Atlas LB API](https://wiki.openstack.org/wiki/Atlas-LB).

## Summary of Client 

- All access is over HTTPS.
- All resources are accessed from the root path `https://<controller_domain>/api/`. 
- All data is sent and received as JSON (the header `Content-Type: application/json` must be set).
- Arguments to resources related to filtering, etc. are specified as query strings. 
- Versioning is specified through content negotiation.
- Basic Authetication and Token based authentication are supported.  The expected headers are `Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==` and `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b` respectively.
- Requests may be denied when a user is not __authenticated__ or not __authorized__.

### Resources
RESTful APIs expose resources over HTTP.  As a convenience to the user, meaningful strings frequently occur in 
pathnames.  A collection of a resource is located by a base path such as `https://<domain>/api/<collection>`.  An
instance of a resource is located relative to the base path and typically ends in a human readable identifier.  An 
example is `https://<domain>/api/<collection>/<id>` where `<id>` is a dash delimited string such as
`my-resource-id`.   

The following is a table of the resources exposed by this API:

Resource | Path
--- | ---
[Virtual IP](#virtual-ip) | `/api/virtual_ip`
[Virtual Service](#virtual-service) | `/api/virtualservice`
[Pool](#pool) | `/api/pool`
[Pool Server](#pool-server) | `/api/pool/<pool_name>/server`
[Health Monitor](#health-monitor) | `/api/healthmonitor`
**Network Profiles** |
[Traffic Profile](#traffic-profile) | `/api/traffic_profile`
[TCP Proxy Profile](#tcp-proxy-profile) | `/api/tcp_proxy_profile`
[TCP Fast Path Profile](#tcp-fast-path-profile) | `/api/tcp_fast_path_profile`
[UDP Fast Path Profile](#udp-fast-path-profile) | `/api/udp_fast_path_profile`
[Network Security Profile](#network-security-profile) | `/api/network_security_profile`
[Network Profile](#network-profile) | `/api/network_profile`
**Application Profiles** |
[Application Profile](#application-profile) | `/api/applicationprofile`
[HTTP Security Profile](#http-security-profile) | `/api/http_security_profile`
[HTTP Caching Profile](#http-caching-profile) | `/api/http_caching_profile`
[HTTP Compression Profile](#http-compression-profile) | `/api/http_compression_profile`
[HTTP SSL Termination Profile](#http-ssl-termination-profile) | `/api/http_ssl_termination_profile`
[HTTP Content Profile](#http-content-profile) | `/api/http_content_profile`
[HTTP User Data](#http-user-data) | `/api/http_user_data`
**Miscellaneous** |
[IP List](#ip-list) | `/api/ip_list`
[Service Engine](#service-engine) | `/api/serviceengine`
[Task](#task) | `/api/task`
[Auth Token](#auth-token) | `/api/token`

### Methods
RESTful APIs follow the convention that the operations on resources are inherited from the existing 
HTTP methods.  Below is a summary of the methods, the resource paths, and the meaning when applied 
to collections, instances and relationships.  The convention of omitting the trailing slash is followed.

#### Collection
Method | Path | Meaning
--- | --- | ---
GET | `/api/<collection>` | Read an entire collection of resources.
POST | `/api/<collection>` | Create a new instance of a resource.
PUT | `/api/<collection>` | Not supported (would imply replacing entire resource collection).
PATCH | `/api/<collection>` | Not supported.
DELETE | `/api/<collection>` | Not supported (would imply deleting entire resource collection).

#### Instance
Method | Path | Meaning
--- | --- | ---
GET | `/api/<collection>/<id>` | Read a single instance from a collection of resources.
POST | `/api/<collection>/<id>` | Not supported.
PUT | `/api/<collection>/<id>` | Replace an instance with a new representation entirely.
PATCH | `/api/<collection>/<id>` | Selectively update a resource with provided fields.
DELETE | `/api/<collection>/<id>` | Delete instance of resource.

#### Relationships
These resource paths apply only for many-to-many relationships.  One-to-one and one-to-many relationships 
can be captured with a single reference field pointing to the related resource.

Method | Path | Meaning
--- | --- | ---
PUT | `/api/<collection>/<id>/<relationship>/<id2>` | Add to many-to-many relationship. 
DELETE | `/api/<collection>/<id>/<relationship>/<id2>` | Delete from many-to-many relationship. 

### Requests
All fields in this document are required unless explicitly labeled as optional.  Optional fields 
will internally be represented as Null columns in the underlying schema.  Null columns will not be returned to 
the user.  Required fields with default values specified in this document may be omitted and defaults will be 
applied. 

The field `url` is added to each resource.  This field is read only and is included whenever a 
resource is returned.  A URL represents a resource's primary key that other resources may reference.  Two resources may
not share the same URL unless they are the same resource.  

Examples of successful request/response pairs for each method are listed below:

##### GET
```
GET /api/virtual_ip HTTP/1.1
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Accept-Type: application/json

HTTP/1.0 200 OK
Content-Type: application/json

[
    {
        "url" : "http://<controller>/api/virtual_ip/web-server",
        "name" : "web-server",
        "fqdn" : "backend.com",
        "type" : "V4",
        "ip_addr" : "10.0.0.10",
        "respond_to_ping" : false,
    },
    {
        "url" : "http://<controller>/api/virtual_ip/web-server-2",
        "name" : "web-server-2",
        "fqdn" : "backend2.com",
        "type" : "V4",
        "ip_addr" : "10.0.0.20",
        "respond_to_ping" : false,
    }
]

GET /api/virtual_ip/web-server HTTP/1.0
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Accept-Type: application/json

HTTP/1.0 200 OK
Content-Type: application/json

{
    "url" : "http://<controller>/api/virtual_ip/web-server",
    "name" : "web server",
    "fqdn" : "backend.com",
    "type" : "V4",
    "ip_addr" : "10.0.0.10",
    "respond_to_ping" : false,
}
``` 

##### POST
```
POST /api/virtual_ip HTTP/1.0
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Accept-Type: application/json

{
    "name" : "web-server-3",
    "fqdn" : "backend3.com",
    "type" : "V4",
    "ip_addr" : "10.0.0.30",
    "respond_to_ping" : false,
}
    
HTTP/1.0 201 CREATED
Content-Type: application/json
Location: http://<controller>/api/virtual_ip/web-server-3

{
    "url" : "http://<controller>/api/virtual_ip/web-server-3",
    "name" : "web-server-3",
    "fqdn" : "backend3.com",
    "type" : "V4",
    "ip_addr" : "10.0.0.30",
    "respond_to_ping" : false,
}
``` 
Note that `POST` requrests return the newly created resource in full, return `HTTP/1.0 201 CREATED`, and include the `Location` header.

##### PUT
```
PUT /api/virtual_ip/web-server-3 HTTP/1.0
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Accept-Type: application/json

{
    "name" : "web-server-3",
    "fqdn" : "backend3.com",
    "type" : "V4",
    "ip_addr" : "10.0.0.40",
    "respond_to_ping" : false,
}
    
HTTP/1.0 200 OK
Content-Type: application/json

{
    "url" : "http://<controller>/api/virtual_ip/web-server-3",
    "name" : "web server 3",
    "fqdn" : "backend3.com",
    "type" : "V4",
    "ip_addr" : "10.0.0.40",
    "respond_to_ping" : false,
}
``` 
Note that `PUT` requests return `HTTP/1.0 200 OK` status.

##### PATCH
```
PATCH /api/virtual_ip/web-server-3 HTTP/1.0
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Accept-Type: application/json

{
    "name" : "web-server-three",
}
    
HTTP/1.0 200 OK
Content-Type: application/json

{
    "url" : "http://<controller>/api/virtual_ip/web-server-three",
    "name" : "web-server-three,
    "fqdn" : "backend3.com",
    "type" : "V4",
    "ip_addr" : "10.0.0.30",
    "respond_to_ping" : false,
}
```
Note that only the fields required to "patch" the resource are specified.  The full object is returned to confirm
the change.  If the slug field has changed, a new url may be returned.

##### DELETE
```
DELETE /api/virtual_ip/web-server-three HTTP/1.0
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

HTTP/1.0 204 NO CONTENT

```

### Status Codes 
RESTful APIs reuse the existing status codes provided by HTTP.  The complete reference for HTTP status codes can be located 
[Here](http://en.wikipedia.org/wiki/List_of_HTTP_status_codes).  The commonly used status codes are listed below:

Status Code | Description
--- | ---
`200 OK` | Successful `GET`, `PUT`, or `PATCH`.
`201 Created` | Successful `POST`.
`202 Accepted` |  Returned for all legal requests when client specifies asyncronous processing.
`204 No Content` | Successful `DELETE`.
`301 Moved Permanently` | Returned when a resource has been renamed.
`401 Unauthorized` | Returned when client is not **authenticated**.
`403 Forbidden` | Returned when client is not **authorized**.
`404 Not Found` | Resource not found.
`405 Method Not Allowed` | Method is not allowed for user (i.e. user has read-only privilege).
`418 I'm a teapot` | Occasionally returned just for kicks.
`429 Too Many Requests` | Rate limit hit.
`500 Internal Server Error` | Blame Paul.

### Errors
If a request cannot be applied because the configuration is incorrect, an error code will be returned immediately
with a meaningful description in the payload and the proper status code set.  An example is below:

    POST /api/virtual_ip HTTP/1.0
    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    Accept-Type: application/json

    {
        "type" : "V4",
        "ip_addr" : "10.0.0.30",
    }
    
    HTTP/1.0 400 Bad Request
    Content-Type: application/json
    
    {
        "errors" : [
            "Missing required field 'name'!"
        ],
    }
    
### Operational Status

Instances of the object model represent a view of how the underlying resources should be configured.  This view, 
however, may not be the actual state of the resources behind the represenation.  Each object contains additional 
fields not shown in the resource specifications below to capture this operational state.  The `state` field represents
a high level status of the object while the `active_tasks` and `failed_tasks` represent configuration changes in action
or previously failed requests.  Failed requests will persist until explicitly deleted.

    GET /api/<object>/<instance>
    {
        . . .,

        "operational_status" : {
            "state" : "INVALID",
            "active_tasks" : [
                "/api/task/4k430vhs",
            ],
            "failed_tasks" : [
                "/api/task/fj32d89s",
                "/api/task/43j89su8",
                "/api/task/95vcx890",
            ]
        },
    }
    
### Synchronous Clients
At present all clients are synchronous by default.  This implies that clients will block until an object has been 
fully propogated throughout the cluster.  Future support will be provided for asynchronous clients to 
reference a task queue. 

### Asynchronous Clients
Clients that wish to be asynchronous may specify as such with the query string flag `?async=true`.  When operating in 
asynchronous mode the configuration is validated for obvious errors and then an `HTTP 202 Accepted` is returned 
along with a task id to poll on for status.  An example is below:

    PATCH /api/virtual_ip/web-server-3 HTTP/1.0
    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    Accept-Type: application/json

    {
        "name" : "web-server-three",
    }
    
    HTTP/1.0 202 Accepted
    Content-Type: application/json
    
    {
        . . ., 
        
        "task_ref" : "/api/task/fjk3kdjk2",
    } 




### Tenancy
All resources are implicitly tied to a tenant by authenticating an API consumer.  A global view of all tenants 
and their created resources is available relative to the path `/api/tenant/(?P<name>[-\w]+)`.  An example of 
this tenant specific path for the virtual IP resources would be `/api/tenant/sales/virtual_ip`.


---

# Resource Specification
Below is a specification of the supported resources.  To keep the specification consise, full HTTP samples are not
provided and instead are abbreviated by omitting all but the method, path, and data.

## Virtual IP
### Description
A Virtual IP described by at least an FQDN or an IP address with an optional netmask. 

### List all Virtual IPs for a Tenant
    GET /api/virtual_ip

### Create a Virtual IP
    POST /api/virtual_ip
    {
      "name" : "super-ip",
      "ip_type" : "V4",
      "ip_addr" : "10.0.0.1",
      "respond_to_ping" : false,
    }

### Get, Edit, Replace, or Delete existing Virtual IP
    [GET|PUT|PATCH|DELETE] /api/virtual_ip/(?P<name>[-\w]+)

### Fields
* `name` - Nickname of the IP.
* `description` - *(optional)*.
* `ip_type` - Enumerated field *(optional)*.
* `ip_addr` - String version of IP address *(optional)*.
* `respond_to_ping` - VIP responds to ping *(Defaults to true)*.

### Restrictions
    ip_type = {"V4", "V6"}
    netmask_type = {"V4", "V6"}







## Virtual Service
### Description
A virtual service describes the configuration details of a port behind a virtual ip.

### List all Virtual Services
    GET /api/virtual_service
### Create a Virtual Service
    POST /api/virtual_service
    {
      "name" : "web-server",
      "description" : "ecommerce site",
      "virtual_ip_ref" : "/api/virtual_ip/super-ip",
      "port" : 80, 
      "snat_enabled" : true,
      "network_logging" : {
          "format" : "NETWORK_LOGGING_TODO",
          "server" : "10.0.0.1:8000",
      },
      "network_profile_ref" : "/api/network_profile/common-web",
      "network_security_profile_ref" : "/api/network_security_profile/strict-acl",
      "traffic_profile_ref" : "/api/traffic_profile/unlimited",
      "pool_ref" : "/api/pool/web-server-pool",
      "rules_ref" : "/api/rules/redirect-plus-sec",
      "http_user_data_ref" : "/api/http_user_data/vs-specific-data",
    }
### Get, Edit, Replace, or Delete existing Virtual Service
    [GET|PUT|PATCH|DELETE] /api/virtual_service/(?P<name>[-\w]+)

### Fields
* `name` - Nickname for virtual service (possibly a FQDN).
* `description` - *(optional)*.
* `virtual_ip_ref` - Reference to virtual IP the virtual service belongs to.
* `port` - Port the virtual service is bound to.* `snat_enabled` -  *(default true)*.
* `network_logging` - *(optional)*.
    * `format` - Enumeration of logging type.
    * `server` - Logging server.
* `network_profile_ref` - Dependent on protocol.
* `network_security_profile_ref` -  *(optional)*.
* `traffic_profile_ref` - *(optional)*.
* `pool_ref` - Reference to pool *(optional)*.
* `rules_ref` - Reference to rules *(optional)*.
* `http_user_data_ref` - Reference to data specific to virtual service *(optional)*.

### Restrictions
    network_logging.format = {
        NETWORK_LOGGING_TODO,
    }





## Pool
### Description
A Pool of servers behind a Virtual Service.
### List all Pools
    GET /api/pool
### Create a Pool
    POST /api/pool
    {
      "name" : "web-server-pool",
      "algorithm" : "LB_ALGORITHM_ROUND_ROBIN",
      "persistence" : "PERSISTENCE_HTTP_COOKIE",
      "server_refs" : [
          "/api/server/server-1",
      ],
      "health_monitor_refs" : [
        "/api/health_monitor/reusable-http-monitor"
      ]
    }
### Get, Edit, Replace, or Delete existing Pool
    [GET|PUT|PATCH|DELETE] /api/pool/(?P<name>[-\w]+)
### Add or Delete a reference to a Server
    [PUT|DELETE] /api/pool/(?P<pool_name>[-\w]+)/server_refs/(?P<server_name>[-\w]+)
### Add or Delete a reference to a Health Monitor
    [PUT|DELETE] /api/pool/(?P<pool_name>[-\w]+)/health_monitor_refs/(?<healthmonitor_name>[-\w]+)
    
### Fields
* `name` - Nickname for pool.
* `description` - *(optional)*.
* `algorithm` - Enumeration for load balancing algorithm.
* `algorithm_hash` - Sub enumeration when algorithm is "LB_ALGORITHM_CONSISTENT_HASH" *(optional)*.
* `algorithm_hash_arg` - Argument when algorithm_hash is set *(optional)*.
* `peristence` - Enumeration for persistence type.
* `server_refs` - Array of references to servers. Also updatable by convenience path.
* `health_monitor_refs` - Array of references to health monitors.  Also updatable by convenience path.

### Restrictions
    algorithm = {
      "LB_ALGORITHM_LEAST_CONNECTIONS",
      "LB_ALGORITHM_ROUND_ROBIN",
      "LB_ALGORITHM_FASTEST",
      "LB_ALGORITHM_COMBINED_LEAST_CONNECTIONS",
      "LB_ALGORITHM_CONSISTENT_HASH"
    }
    algorithm_hash = {
      "LB_ALGORITHM_CONSISTENT_HASH_SOURCE_IP_ADDRESS",
      "LB_ALGORITHM_CONSISTENT_HASH_SOURCE_IP_ADDRESS_AND_PORT",
      "LB_ALGORITHM_CONSISTENT_HASH_URI",
      "LB_ALGORITHM_CONSISTENT_HASH_CUSTOM_HEADER",
    }
    persistence = {
      "PERSISTENCE_IP_ADDR",
      "PERSISTENCE_HTTP_COOKIE",
      "PERSISTENCE_JSESSION_ID",
      "PERSISTENCE_CUSTOM_RULE"
    }






## Server
### Description
Servers may be referenced by a pool.

### List all Servers
    GET /api/server
### Create a Server
    POST /api/server
    {
      "name" : "server1",
      "ip_type" : "V4",
      "ip_addr" : "10.0.0.1",
      "port" : 8080,
      "enabled" : true,
      "graceful_disable_timeout" : 60,
      "ratio" : 50,
      "slow_start_ratio" : 50
    }
    
### Get, Edit, Replace, or Delete existing Pool
    [GET|PUT|PATCH|DELETE] /api/server/(?P<name>[-\w]+)
### Fields
* `name` - Nickname for server.
* `description` - *(optional)*.
* `ip_type` - Enumeration for IP type.
* `ip_addr` - String representation of IP address.
* `port` - Port of server.
* `enabled` - Boolean representing server enabled or not *(optional, default is true)*.
* `graceful_disable_timeout` - Timeout in seconds to wait when disabling a server *(optional)*.
* `ratio` - Load balancing ratio *(optional)*.
* `slow_start_ratio` - Ratio when bringing up server *(optional)*.

### Restrictions
    ip_type = {"V4", "V6"}







## Health Monitor
### Description
A health monitor monitors the servers in a pool. 
### List all Health Monitors
    GET /api/health_monitor
### Create a Health Monitor
    POST /api/health_monitor
    {
        "name" : "heath-bar",
        "status" : "HEALTH_MONITOR_ACTIVE",
        "send_interval" : 60,
        "receive_timeout" : 300,
        "type" : "HEALTH_MONITOR_HTTP",
        "http_monitor" : {
            "method" : "GET",
            "port" : 80,
            "expected_status" : 200, 
        }
    }
### Get, Edit, Replace, or Delete existing Health Monitor
    [GET|PATCH|PUT|DELETE] /api/health_monitor/(?<name>[-\w]+)
### Fields
* `name` - Nickname for health monitor.
* `description` - *(optional)*.
* `status` - Enumeration for health monitor status *(optional, default is active).
* `send_interval` - Number of seconds between health check.
* `receive_timeout` - Number of seconds to wait until health check fails.
* `type` - Enumeration for monitor type.  Controls which optional fields become mandatory.
* `tcp_monitor` - Provided when type = "HEALTH_MONITOR_TCP" *(optional)*.
    * `port` - Port to monitor.
    * `half_open` - Flag.
    * `rst` - Flag.
    * `fin` - Flag.
* `http_monitor` - Provided when type = "HEALTH_MONITOR_HTTP" *(optional).
    * `method` - HTTP method such as GET, POST, etc.
    * `expected_reply` - Server text response to match against *(optional)*.
    * `expected_status` - Server status response *(optional)*.
    * `port` - Port HTTP server is at.
* `https_monitor` - Provided when type = "HEALTH_MONITOR_HTTPS", identical to  `http_monitor` *(optional)*.

### Restrictions
    status = {
        "HEALTH_MONITOR",
        "INLINE_HEALTH_MONITOR"
    }
    type = {
        "HEALTH_MONITOR_TCP",
        "HEALTH_MONITOR_HTTP",
        "HEALTH_MONITOR_HTTPS",
        "HEALTH_MONITOR_UDP",
        "HEALTH_MONITOR_PING",
        "HEALTH_MONITOR_DNS",
        "HEALTH_MONITOR_CUSTOM"
    }






## Traffic Profile
### Description
Traffic settings for a network profile.  Theses settings apply to all protocol types.
### List all created Traffic Profiles
    GET /api/traffic_profile
### Create a Traffic Profile
    POST /api/traffic_profile
    {
        "name" : "traffic-profile",
        "new_connection_per_sec" : 60,
        "max_concurrent_connections" : 100,
        "max_bandwidth" : 1024,
    }
    
### Get, Edit, Replace, or Delete existing Traffic Profile
    [GET|PATCH|PUT|DELETE] /api/traffic_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for traffic profile.
* `description` - *(optional)*.
* `new_connection_per_sec` - New connection rate for Virtual Service.
* `max_concurrent_connections` - Max concurrent connections for Virtual Service.
* `max_bandwidth` - Max bandwidth for Virtual Service.





## TCP Proxy Profile
### Description
Network settings that apply to a TCP proxy.  This resource encapsulated both the client
and server side settings.
### List all created TCP Proxy Profiles
    GET /api/tcp_proxy_profile
### Create a TCP Proxy Profile
    POST /api/tcp_proxy_profile
    {
        "name" : "my-proxy-profile",
        "server" : {
            "connection_timeout" : 300,
        }
        "client" : {
            "connection_timeout" : 300,
        }
    }
### Get, Edit, Replace, or Delete existing TCP proxy Profile
    [GET|PATCH|PUT|DELETE] /api/tcp_proxy_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for profile.
* `description` - *(optional)*.
* `server` - Server settings.
    * `connection_timeout` - Connection timeout *(default is 300 seconds)*.
* `client` - Client settings. 
    * `connection_timeout` - Connection timeout *(default is 300 seconds)*.






## TCP Fast Path Profile
### Description
Network settings that apply to a TCP Fast Path.
### List all created TCP Fast Path Profiles
    GET /api/tcp_fast_path_profile
### Create a TCP Fast Path Profile
    POST /api/tcp_fast_path_profile
    {
        "name" : "my-fast-path-profile",
        "connection_timeout" : 60,
    }
### Get, Edit, Replace, or Delete existing TCP Fast Path Profile
    [GET|PATCH|PUT|DELETE] /api/tcp_fast_path_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for profile.
* `description` - *(optional)*.
* `connection_timeout` - Connection timeout *(default is 300 seconds)*.






## UDP Fast Path Profile
### Description
Network settings that apply to a UDP Fast Path.
### List all created UDP Fast Path Profiles
    GET /api/udp_fast_path_profile
### Create a UDP Fast Path Profile
    POST /api/udp_fast_path_profile
    {
        "name" : "my-fast-path-profile",
        "policy" : "UDP_FAST_PATH_POLICY_PER_PACKET",
        "per_flow_timeout" : 60,
    }

### Get, Edit, Replace, or Delete existing UDP Fast Path Profile
    [GET|PATCH|PUT|DELETE] /api/udp_fast_path_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for policy.
* `description` - *(optional)*.
* `policy` - Enumeration for UDP policy.
* `per_flow_timeout` - When policy is UDP_FAST_PATH_POLICY_PER_FLOW *(optional)*.

### Restrictions
    udp_fast_path_network_profile.policy = {
        "UDP_FAST_PATH_POLICY_PER_PACKET",
        "UDP_FAST_PATH_POLICY_PER_FLOW"
    }

## Network Security Profile
### Description
Describes the security policy to provide firewall description for the transport.
### List all created Network Security Profiles
    GET /api/network_security_profile
### Create a Network Security Profile
    POST /api/network_security_profile
    {
        "name" : "my-security-group",
        "rules" : [
            {
               "action" : "ALLOW",
               "ip_list_ref" : "/api/ip_list/good-guys",
               "log" : false,
               
            },
            {
               "action" : "DENY",
               "ip_list_ref" : "/api/ip_list/bad-guys",
               "log" : true,
            }
        ]
    }
### Get, Edit, Replace, or Delete existing Network Security Profile
    [GET|PATCH|PUT|DELETE] /api/network_security_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for profile.
* `description` - *(optional)*.
* `rules`
    * `action` - Allow or Deny IP list.
    * `ip_list_ref` - Reference to group of IPs.
    * `log` - Log actions.

### Restrictions
    rules.action = {
        "ALLOW",
        "DENY",
    }

    
## Network Profile
### Description
Describes the transport that is being load balanced.
### List all created Network Profiles
    GET /api/network_profile
### Create a Network Profile
    POST /api/network_profile
    {
        "name" : "my-network-profile",
        "type" : "PROTOCOL_TCP_PROXY",
        "tcp_proxy_profile_ref" : "/api/tcp_proxy_profile/tcp-proxy-profile",
        "application_profile_ref" : "/api/application_profile/nginx-profile",
    }

### Get, Edit, Replace, or Delete existing Profile
    [GET|PATCH|PUT|DELETE] /api/network_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for profile object.
* `description` - *(optional)*.
* `type` - Enumeration of profile type *(default = "PROTOCOL_TCP_PROXY")*.
* `tcp_proxy_profile_ref` - Profile when type is PROTOCOL_TCP_PROXY *(optional)*.
* `tcp_fast_path_profile_ref` - Profile when type is PROTOCOL_TCP_FAST_PATH *(optional)*.
* `udp_fast_path_profile_ref` - Profile when type is PROTOCOL_UDP_FAST_PATH *(optional)*.
* `application_profile_ref` - Reference to application profile when type is PROTOCOL_TCP_PROXY *(optional)*.

### Restrictions
    type = {
        "PROTOCOL_TCP_PROXY",
        "PROTOCOL_TCP_FAST_PATH",
        "PROTOCOL_UDP_FAST_PATH"
    }






## Application Profile
### Description
An application profile may be referenced by a network profile when in TCP proxy mode.  Currently, only HTTP is supported.
### List all Application Profiles
    GET /api/application_profile
### Create an Application Profile
    POST /api/application_profile
    {
        "name" : "nginx-profile",
        "type" : "APPLICATION_PROFILE_HTTP",
        "http_profile" : {
            "multiplex_enabled" : true,
            "xff_enabled" : true,
            "xff_alternate_name" : "XFF",
            "chunk_mode" : "CHUNK_MODE_AUTOMATIC",
            "log_format" : "LOG_FORMAT_W3C",
            "http_security_profile_ref" : "/api/http_security_profile/limited-methods",
            "http_caching_profile_ref" : "/api/http_caching_profile/my-caching-profile",
            "http_compression_profile_ref" : "/api/http_compression_profile/so-compressed",
            "http_ssl_termination_profile_ref" : "/api/http_ssl_termination_profile/super-secret",
        },
    }

### Get, Edit, Replace, or Delete existing Application Profile
    [GET|PATCH|PUT|DELETE] /api/http_application_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for application profile.
* `description` - *(optional)*.
* `type` - Application type, currently only HTTP supported.
* `http_profile` -
    * `multiplex_enabled` - *(default = true)*.
    * `xff_enabled` - *(default = true)*.
    * `xff_alternate_name` - *(default = "XFF")*.
    * `chunk_mode` - Enumeration.
    * `http_security_profile_ref` - Security settings *(optional)*
    * `http_caching_profile_ref` - Caching settings *(optional)*. 
    * `http_compression_profile_ref` - Compression settings *(optional)*.
    * `http_ssl_termination_profile_ref` - Reference to SSL termination profile *(optional)*.

### Restrictions
    type = {
        "APPLICATION_PROFILE_NONE",
        "APPLICATION_PROFILE_HTTP"
    }
    http_profile.multiplex_options.mask_type = {"V4", "V6"}
    http_profile.chunk_mode = {
        "CHUNK_MODE_AUTOMATIC",
        "CHUNK_MODE_UNCHUNK",
        "CHUNK_MODE_CONTENT_LENGTH"
    }






## HTTP Security Profile
### Description
An http security profile may be referenced by an application profile.
### List all HTTP Security Profiles
    GET /api/http_security_profile
### Create an HTTP Security Profile
    POST /api/http_security_profile
    {
        "name" : "limited-methods",
        "max_request_header_size" : 49152,
        "max_time_header_received" : 15,
        "cookie_encryption_enabled" : true,
        "server_sanitization" : true,
        "strip_xff" : true,
        "accept_head" : true,
        "accept_get" : true,
        "accept_post" : true,
        "accept_put" : false,
        "accept_patch" : false,
        "accept_delete" : false,
        "accept_http_0_9" : false,
        "accept_http_1_0" : true,
        "accept_http_1_1" : true,
        "allow_spdy" : false,
        "allow_websocket" : false,
    }
### Get, Edit, Replace, or Delete existing HTTP Security Profile
    [GET|PATCH|PUT|DELETE] /api/http_security_profile/(?<name>[-\w]+)

### Fields
* `name` - Nickname for HTTP security profile.
* `description` - *(optional)*.
* `max_request_header_size` - Max request header size *(default = 49152)*.
* `max_time_header_received` - Max time between header received in seconds *(default = 15)*.
* `cookie_encryption_enabled` - Encrypt cookies *(default = true)*.
* `server_sanitization` - Strip out sensitive header information *(default = true)*.
* `strip_xff` - Remove XFF header *(default = true)*.
* `accept_head` - Allow HTTP HEAD method *(default = true)*.
* `accept_get` - Allow HTTP GET method *(default = true)*.
* `accept_post` - Allow HTTP POST method *(default = true)*.
* `accept_put` - Allow HTTP PUT method *(default = false)*.
* `accept_patch` - Allow HTTP PATCH method *(default = false)*.
* `accept_delete` - Allow HTTP DELETE method *(default = false)*.
* `accept_http_0_9` - Honor HTTP .9 requests *(default = false)*.
* `accept_http_1_0` - Honor HTTP 1.0 requests *(default = true)*.
* `accept_http_1_1` - Honor HTTP 1.1 requests *(default = true)*.
* `allow_spdy` - Allow SPDY requests *(default = false)*.
* `allow_websocket` Allow Websockets *(default = false)*.






## HTTP Caching Profile
### Description
Caching profile.
### List all HTTP Caching Profiles
    GET /api/http_caching_profile
### Create an HTTP Caching Profile
    POST /api/http_caching_profile
    {
        "name" : "my-caching-profile",
        "override_cache_control_headers" : true,
        "manually_delete_object" : true,
        "cache_memory_allocation" : false,
    }
### Get, Edit, Replace, or Delete existing HTTP Caching Profile
    [GET|PATCH|PUT|DELETE] /api/http_caching_profile/(?<name>[-\w]+)

### Fields
* `name` - Nickame for profile.
* `description` - *(optional)*.
* `override_cache_control_headers` - Boolean.
* `manually_delete_object` - Boolean.
* `cache_memory_allocation` - Boolean.






## HTTP Compression Profile
### Description
Compression profile.
### List all HTTP Compression Profiles
    GET /api/http_compression_profile
### Create an HTTP Compression Profile
    POST /api/http_compression_profile
    {
        "name" : "so-compressed",
        "compression_type" :  "COMPRESSION_GZIP",
        "override_server_compression" : true,
        "cache_compressed_responses" : true,
        "compression_level" : 0,
    }
### Get, Edit, Replace, or Delete existing HTTP Compression Profile
    [GET|PATCH|PUT|DELETE] /api/http_compression_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickame for profile.
* `description` - *(optional)*.
* `compression_type` - Enumeration.
* `override_server_compression` - Boolean. Remove Accept-Encoding header.
* `cache_compressed_responses` - Boolean.
* `compression_level` - Integer level 0 - 9.

### Restrictions
    compression_type = {
        "COMPRESSION_GZIP",
        "COMPRESSION_DEFLATE",
        "COMPRESSION_SDCH"
    }






## HTTP SSL Termination Profile
### Description
SSL Termination Profile.
### List all HTTP SSL Termination Profiles
    GET /api/http_ssl_termination_profile
### Create an HTTP SSL Termination Profile
    POST /api/http_ssl_termination_profile
    {
        "name" : "secret-keeper",
        "forward_certificate_via_http" : true,
        "accepted_cipher" : "SSL_CIPHER_AES128",
        "accepted_version" : "SSL_VERSION_TLS1",
        "certificate" : "very long string",
        "key" : "very long string",
        "enable_logging" : true,
    }
### Get, Edit, Replace, or Delete existing HTTP Compression Profile
    [GET|PATCH|PUT|DELETE] /api/http_ssl_termination_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for profile.
* `description` - *(optional)*.
* `forward_certificate_via_http` - Boolean *(default = true)*.
* `accepted_cipher` - Enumeration *(default = "SSL_CIPHER_AES128")*.
* `accepted_version` - Enuumeration *(default = SSL_VERSION_TLS1")*.
* `certificate` - Certificate string.
* `key` - Key string.
* `enable_logging` - Log access.

### Restrictions
    ssl_termination.accepted_cipher = {
        "SSL_CIPHER_RC4",
        "SSL_CIPHER_AES128",
        "SSL_CIPHER_AES256"
    }
    ssl_termination.accepted_version = {
        "SSL_VERSION_SSL2",
        "SSL_VERSION_TLS1",
        "SSL_VERSION_TLS1",
        "SSL_VERSION_TLS1_2"
    }





    
## HTTP Content Profile
### Description
The content profile settings allow rewriting requests.
### List all HTTP Content Profiles
    GET /api/http_content_profile
### Create an HTTP Content Profile
    POST /api/http_content_profile
    {
        "name" : "bounce-to-ssl",
        "type" : "HTTP_PROXY_PASS_SWITCHING_RULE",
        "switching_rule" : {
            "match_criteria" : "BEGINS_WITH",
            "match_pattern" : "https",
            "match_resource" : "URI",
            "pool_ref" : "/api/pool/web-server-pool"
        },
    }

### Get, Edit, Replace, or Delete existing HTTP Content Profile
    [GET|PATCH|PUT|DELETE] /api/http_content_profile/(?<name>[-\w]+)
### Fields
* `name` - Nickname for content profile.
* `description` - *(optional)*.
* `type` - Enumeration.
* `switching_rule` - Set when type is "HTTP_PROXY_PASS_SWITCHING_RULE" *(optional)*.
    * `match_criteria` - Enumeration for string operation.
    * `match_pattern` - String with pattern.
    * `match_resource` - String to operate on.
    * `pool_ref` - Pool to switch to when a match occurs.
* `redirect_rule` - Set when type is "HTTP_PROXY_PASS_REDIRECT" *(optional)*.
    * `match_criteria` - Enumeration for string operation.
    * `match_pattern` - String with pattern.
    * `match_resource` - String to operate on.
    * `protocol` - Enumeration. 
    * `status` - HTTP status code to return *(default = 302)*.
    * `destination` - Destination URL.
    * `retain_path` - Boolean *(default = false)*.
    * `retain_query` - Boolean *(default - true)*.
* `rewrite_rule` - Set when type is "HTTP_PROXY_PASS_REWRITE" *(optional)*.

### Constraints
    [switching_rule|redirect_rule].type = {
        "HTTP_PROXY_PASS_SWITCHING_RULE",
        "HTTP_PROXY_PASS_REDIRECT",
        "HTTP_PROXY_PASS_REWRITE",
    }
    [switching_rule|redirect_rule].match_criteria = {
        "BEGINS_WITH",
        "CONTAINS",
        "ENDS_WITH",
        "REGEX",
    }
    rewrite_rule.protocol = {
        "HTTP",
        "HTTPS",
    }
    match_resource = {
        "URI", 
        "URL",
    }






## HTTP User Data
### Description
A container for application data that is likely not sharable because it is specific to the virtual service.
### List all HTTP User Data objects
    GET /api/http_user_data
### Create an HTTP User Data object
    POST /api/http_user_data
    {
        "name" : "virtual-service-data",
        "http_content_profile_refs : [
            "/api/http_content_profile/bounce-to-ssl",
        ],    
    }

### Get, Edit, Replace, or Delete existing HTTP User Data object
    [GET|PATCH|PUT|DELETE] /api/http_user_data/(?<name>[-\w]+)
### Add or Delete an HTTP Content Profile reference
    [PUT|DELETE] /api/http_user_data/(?<user_data_name>[-\w]+)/http_content_profile/(?<content_name>[-\w]+)

### Fields
* `name` - Nickname of user data
* `http_content_profile_refs` - Array of references to content profile rules.






## IP List
### Description
A collection of IP address with no meaning applied.  An IP can be specified as a single address, a mask, or a range.

### List all IP Lists
    GET /api/ip_list

### Create an IP List
    POST /api/ip_list
    {
        "name" : "ip-list-backend",
        "ips" : [
            {
               "type" : "V4",
               "addr" : "192.168.1.0/24",
            }, 
            {
               "type" : "V4",
               "addr" : "10.0.0.1",
            },
            {
               "type" : "V4",
               "addr" : "10.10.0.10-50",
            }
        ],
    }

### Get, Edit, Replace, or Delete existing IP List
    [GET|PATCH|PUT|DELETE] /api/ip_list/(?<name>[-\w]+)
### Fields
* `name` - Nickname for list.
* `description` - *(optional)*.
* `ips` - Array of IP objects.

### Restrictions
    type = {"V4", "V6"}





## Asynchronous Task
### Description
A data structure representing outstanding requests on a resource.
       
    
## Service Engine
### Description
This resource is intended to expose some read-only state describing the status of the service engines.  It
is not fully fleshed out yet.
