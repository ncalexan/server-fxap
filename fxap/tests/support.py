from pyramid.config import Configurator

from cornice import Service
from cornice.tests import CatchErrors

import fxap

def includeme(config):
    config.include("cornice")
    config.scan("fxap.views")

def main(global_config, **settings):
    config = Configurator(settings={})
    config.include(fxap.includeme)
    return CatchErrors(config.make_wsgi_app())
