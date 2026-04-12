from setuptools import setup

APP = ['main.py']
DATA_FILES = ['icon/MyIcon.icns']
OPTIONS = {
    'iconfile': 'icon/MyIcon.icns',
    'plist': {
        'CFBundleName': 'RRBoss',
        'CFBundleIdentifier': 'com.wiley.steve.rrboss',
    },
    'packages': ['pydantic'],
    'includes': ['pydantic'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
)

