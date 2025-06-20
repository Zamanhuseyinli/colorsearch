import sys
from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

data_files = []
if sys.platform.startswith("linux"):
    data_files = [
        ('share/applications', ['colorsearch.desktop']),
        ('share/icons/hicolor/64x64/apps', ['icons/colorsearch.svg']),
    ]
elif sys.platform == "darwin":
    data_files = [
        ('Resources', ['icons/colorsearch.icns']),  
    ]
elif sys.platform == "win32":
    data_files = [
        ('', ['icons/colorsearch.ico']),  
    ]

setup(
    name='colorsearch',
    version='1.0.1',
    description='Search images and videos by dominant color (PyQt6)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Zaman Huseyinli',
    author_email='zamanhuseynli23@gmail.com',
    url='https://github.com/Zamanhuseyinli/colorsearch',
    project_urls={
        'Source Code': 'https://github.com/Zamanhuseyinli/colorsearch',
        'Bug Tracker': 'https://github.com/Zamanhuseyinli/colorsearch/issues',
    },
    py_modules=['colorsearch'],
    install_requires=[
        'Pillow>=9.0.0',
        'PyQt6>=6.4.0',
    ],
    entry_points={
        'console_scripts': [
            'colorsearch=colorsearch:main',
        ],
    },
    data_files=data_files,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: X11 Applications :: Qt',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)
