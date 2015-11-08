from setuptools import setup


setup(
    name='Flask-NARF',
    version='0.0.3',
    url='https://github.com/Nizebulous/flask-narf',
    license='MIT',
    author='Damian Hites',
    author_email='nizebulous@gmail.com',
    description='A Simple but Customizable REST Framework',
    long_description=__doc__,
    # py_modules=['flask_narf'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=['flask_narf'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
