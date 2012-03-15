from distutils.core import setup

setup(
    name='django-submodel',
    version='0.1',
    license='MIT',
    author='Li Meng',
    author_email='liokmkoil@gmail.com',
    packages=['submodel'],
    description='A Django model field which value works like a model instance and supports seamless inline editing in Django admin.',
    long_description=open('README.rst').read(),
    url='https://github.com/liokm/django-submodel',
    download_url='https://github.com/liokm/django-submodel',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
