from setuptools import setup, find_packages
import sys, os

version = '1.3'
shortdesc ="bdajax integration for Plone."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(name='bda.plone.ajax',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Environment :: Web Environment',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python', 
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',        
      ],
      keywords='',
      author='Robert Niederreiter',
      author_email='dev@bluedynamics.com',
      url=u'',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
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
