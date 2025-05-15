import re
import subprocess

# pip install pyaxmlparser - https://pypi.org/project/pyaxmlparser/
from pyaxmlparser import APK

from config import *


"""
This is interesting. This is what CoPilot suggested for the function. 
Might work in Linux, but not in Windows because of the aapt command.


Extracts package name, version name, and version code from an APK file.

def get_apk_info(filename):
    try:
        # Use aapt to get the APK info
        output = subprocess.check_output(['aapt', 'dump', 'badging', filename]).decode('utf-8')
        
        # Extract package name
        package_name = re.search(r'package: name=\'([^\']+)\'', output).group(1)
        
        # Extract version name
        version_name = re.search(r'versionName=\'([^\']+)\'', output).group(1)
        
        # Extract version code
        version_code = re.search(r'versionCode=\'([^\']+)\'', output).group(1)
        
        return package_name, version_name, version_code
    except Exception as e:
        logger.info(f"Error extracting APK info: {e}")
        return None, None, None

"""    

def get_apk_info(filename):
    """Extracts package name, version name, and version code from an APK file using aapt."""
    
    # Problem: leaves the file open and does not close it
    # apk = APK(filename)

    with open(filename, 'rb') as f:   # Open the file in binary mode  
        apk = APK(f.read(), raw=True)
        apk_package       = apk.package
        apk_version_name  = apk.version_name
        apk_version_code  = apk.version_code
        apk_application   = apk.application
  
    logger.debug(f"Package name: {apk_package}, version name: {apk_version_name}, version code: {apk_version_code}, application: {apk_application}")

    return apk_package, apk_version_name, apk_version_code, apk_application






