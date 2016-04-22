from setuptools import setup, find_packages

setup(
    name='django-helpers',
    version='0.1a',
    author='Derugin Anton',
    author_email='anton.derugin@gmail.com',
    packages=['helpers', 'helpers/markup', 'helpers/templatetags'],
    install_requires=[
        'requests',
        'python-slugify',
        'django-autoslug'
    ],
    include_package_data=True,
    url='https://github.com/aderugin/django-helpers',
    license='MIT',
    description='Django application',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
