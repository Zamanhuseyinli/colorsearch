from setuptools import setup

setup(
    name='colorsearch',
    version='1.0.0',
    description='Search images and videos by dominant color (PyQt6)',
    author='Zaman Huseyinli',
    author_email='zamanhuseynli23@gmail.com',
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
    data_files=[
        ('share/applications', ['colorsearch.desktop']),
        ('share/icons/hicolor/64x64/apps', ['colorsearch.svg']),  
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: X11 Applications :: Qt',
        'Operating System :: POSIX :: Linux',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)
