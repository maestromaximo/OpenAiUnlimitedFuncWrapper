from setuptools import setup, find_packages

setup(
    name='openaiunlimitedfun',
    version='0.1.0',  # Update the version number for new releases
    author='Alejandro Garcia Polo',  # Replace with your name or organization name
    author_email='alejandrogarcia2423@hotmail.com',  # Replace with your email
    description='A wrapper for OpenAI API gpt with the ability to have unlimited function calling or phseudo functions',  # Short description of your project
    long_description=open('README.md').read(),  # Long description read from the the readme file
    long_description_content_type='text/markdown',  # Type of long_description, e.g., markdown or rst
    url='https://github.com/maestromaximo/OpenAiUnlimitedFuncWrapper',  # Replace with the URL to your project
    packages=find_packages(),  # Automatically find all packages and subpackages
    install_requires=[
        'annotated-types==0.6.0',
        'anyio==4.2.0',
        'certifi==2023.11.17',
        'charset-normalizer==3.3.2',
        'colorama==0.4.6',
        'distro==1.9.0',
        'h11==0.14.0',
        'httpcore==1.0.2',
        'httpx==0.26.0',
        'idna==3.6',
        'numpy==1.26.3',
        'openai==1.6.1',
        'pandas==2.1.4',
        'pydantic==2.5.3',
        'pydantic_core==2.14.6',
        'python-dateutil==2.8.2',
        'python-dotenv==1.0.0',
        'pytz==2023.3.post1',
        'regex==2023.12.25',
        'requests==2.31.0',
        'six==1.16.0',
        'sniffio==1.3.0',
        'tenacity==8.2.3',
        'tiktoken==0.5.2',
        'tqdm==4.66.1',
        'typing_extensions==4.9.0',
        'tzdata==2023.4',
        'urllib3==2.1.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Choose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',  # Again, choose the license appropriate for your project
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.6',  # Minimum version requirement of the package
    keywords='openai, api, wrapper, function_calling, vectors, pseudo_func',  # Short description of your package
    # You can also include entry_points to define command-line scripts, etc.
)
