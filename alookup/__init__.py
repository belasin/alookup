from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
    	#Set up Caching
        if not "cache.regions" in settings:
            #Set default cache regions (if not set)
            settings["cache.regions"] = "default_term, second, short_term, long_term"
        config.include('.lib.caching')
    	#Setup Views
        config.include('.views')
        #Scan for decorator configs
        config.scan()

    return config.make_wsgi_app()
