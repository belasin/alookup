from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from ..lib import glookup


@view_config(route_name='root', renderer='json')
def perform_lookup(request):
    request_payload = None
    try:
        request_payload = request.json_body
    except ValueError, exc:
        raise HTTPBadRequest(str(exc))

    return glookup.perform_lookup(request_payload)

def includeme(config):
    config.add_route('root', '/')
