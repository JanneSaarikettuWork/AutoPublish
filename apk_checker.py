import re
import subprocess

# pip install pyaxmlparser - https://pypi.org/project/pyaxmlparser/
from pyaxmlparser import APK


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
        print(f"Error extracting APK info: {e}")
        return None, None, None

"""    

def get_apk_info(filename):
    """Extracts package name, version name, and version code from an APK file using aapt."""
    apk = APK(filename)
    print("package name:\t" + apk.package)
    print("version name:\t" + apk.version_name)
    print("version code:\t" + apk.version_code)
    print("apk.application: " + apk.application)

    return apk.package, apk.version_name, apk.version_code, apk.application






