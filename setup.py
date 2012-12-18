""" Setup file.
"""
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

requires = ['cornice', 'metlog-py', 'mozsvc', 'PasteScript', 'waitress', 'PyBrowserID', 'Requests', 'webtest']

setup(name='fxap',
    version=0.1,
    description='fxap',
    long_description=README,
    license='MPLv2.0',
    classifiers=[
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
    ],
    keywords="web services",
    author='',
    author_email='',
    url='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points = """\
    [paste.app_factory]
    main = fxap:main
    """,
    paster_plugins=['pyramid'],
)
