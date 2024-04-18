from setuptools import find_packages
from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '2.0.2.dev0'
shortdesc = "bdajax integration for Plone."
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


setup(
    name='bda.plone.ajax',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 6.0',
        'Framework :: Plone :: Addon',
        'Framework :: Zope',
        'Framework :: Zope :: 5',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
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
        'Products.CMFPlone>=5.1',
        'bdajax>=1.10',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
