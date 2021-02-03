from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from ..lib.glookup import perform_lookup
from ..lib.glookup import InvalidAPRequest


@view_config(route_name='root', renderer='json')
def lookup_view(request):
    """Summary
    
    Args:
        request (pyramid.request): ...
    
    Returns:
        LIST: Description
    
    Raises:
        HTTPBadRequest: On an error in the request, an HTTPBadRequest is raised
    """
    request_payload = None
    try:
        request_payload = request.json_body
    except ValueError, exc:
        raise HTTPBadRequest(str(exc))

    try:
        return perform_lookup(request_payload)
    except InvalidAPRequest, exc:
        raise HTTPBadRequest(str(exc))

def includeme(config):
    config.add_route('root', '/')
