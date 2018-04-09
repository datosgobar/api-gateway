#
# This is an example VCL file for Varnish.
#
# It does not do anything by default, delegating control to the
# builtin VCL. The builtin VCL is called when there is no explicit
# return statement.
#
# See the VCL chapters in the Users Guide at https://www.varnish-cache.org/docs/
# and https://www.varnish-cache.org/trac/wiki/VCLExamples for more examples.

# Marker to tell the VCL compiler that this VCL has been adapted to the
# new 4.0 format.
vcl 4.0;
import directors;

# Default backend definition. Set this to point to your content server.

{% for backend in loadbalancer_backends %}
backend {{ backend.name }} {
    .host = "{{ backend.host }}";
    .port = "{{ backend.port }}";
}
{% endfor %}

sub vcl_init {
    new apimgmt = directors.round_robin();
    {% for backend in loadbalancer_backends %}
        apimgmt.add_backend({{ backend.name }});
    {% endfor %}
}

sub vcl_pass {
    return(fetch); # Request to server
}

sub vcl_recv {
    # Happens before we check if we have this in cache already.
    #
    # Typically you clean up the request here, removing cookies you don't need,
    # rewriting the request, etc.
    # send all traffic to the bar director:
    set req.backend_hint = apimgmt.backend(); # Loadbalancing
    return(pass); # Ignore cache

}

sub vcl_backend_response {
    # Happens after we have read the response headers from the backend.
    #
    # Here you clean the response headers, removing silly Set-Cookie headers
    # and other mistakes your backend does.
}

sub vcl_deliver {
    # Happens when we have all the pieces we need, and are about to send the
    # response to the client.
    #
    # You can do accounting or modifying the final object here.
}
