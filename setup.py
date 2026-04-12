from setuptools import setup

APP = ['main.py']
DATA_FILES = ['mainWindow.ui', 'icon/MyIcon.icns']
OPTIONS = {
    'iconfile': 'icon/MyIcon.icns',
    'plist': {
        'CFBundleName': 'RRBoss',
        'CFBundleIdentifier': 'com.wiley.steve.rrboss',
        'NSContactsUsageDescription': 'App needs access to Contacts',
    },
    'packages': ['pydantic'],
    'includes': ['pydantic'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
)

