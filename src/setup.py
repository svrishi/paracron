from distutils.core import setup

setup(
    name='ParaCron',
    version='0.1dev',
    packages=['paracron', 'paracron.models'],
    package_data={
        # Include jinja2 template files
        '': ['templates/*.jinja2']
    },
    license='BSD license',
    long_description=open('README.txt').read(),
    install_requires=[
        'schedule', 'aiohttp', 'aiohttp_jinja2', 'validators'
      ]
)
