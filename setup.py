import os
from setuptools import setup
from setuptools import find_packages


version = '1.7'
shortdesc ="``bdajax`` integration for Plone."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'CHANGES.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()


setup(
    name='bda.plone.ajax',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='plone ajax javascript bdajax',
    author='Robert Niederreiter',
    author_email='dev@bluedynamics.com',
    url=u'https://pypi.org/project/bda.plone.ajax/',
    license='GNU General Public Licence',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['bda', 'bda.plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Plone',
        'plone.app.jquerytools',
        'bdajax>=1.4',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
