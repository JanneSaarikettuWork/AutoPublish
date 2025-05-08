#!/usr/bin/python3

import os
import time

# This file contains the configuration for the application, including directory paths and other constants.
from config import *

DB_FILE = "" # Placeholder for the database file path"
SUPPORTED_REPOS_FILE = os.path.join(DATA_DIR, "supported_repos")

# Import database, GitHub and... functions
from installed_versions_db import *
from githubber import *
from apk_checker import *
from fdroid_builder import *

def check_directories():
    # Are we running in Windows or Linux?
    global ROOT_DIR
    if (os.name == 'nt'):           # Testing in Windows
        ROOT_DIR = ROOT_DIR_NT
    else:
        ROOT_DIR = ROOT_DIR_POSIX

    # Check if the root directory exists and change to it
    if not os.path.exists(ROOT_DIR):
        print(f"Directory {ROOT_DIR} does not exist.")
        return False

    os.chdir(ROOT_DIR)

    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} does not exist.")
        return False
    if not os.path.exists(BUILD_REPO_DIR):
        print(f"Directory {BUILD_REPO_DIR} does not exist.")
        return False
    if not os.path.exists(BUILD_METADATA_DIR):
        print(f"Directory {BUILD_METADATA_DIR} does not exist.")
        return False
    if not os.path.exists(RUN_BACKUP_DIR):
        print(f"Directory {RUN_BACKUP_DIR} does not exist.")
        return False
    if not os.path.exists(RUN_REPO_DIR):
        print(f"Directory {RUN_REPO_DIR} does not exist.")
        return False

    return True


def read_supported_repos():
    """Reads all lines from the specified file."""
    if not os.path.exists(SUPPORTED_REPOS_FILE):
        raise FileNotFoundError(f"The file '{SUPPORTED_REPOS_FILE}' does not exist.")
    with open(SUPPORTED_REPOS_FILE, 'r') as file:
        return file.readlines()
    


if __name__ == "__main__":
    if not check_directories():
        raise Exception("One or more directories do not exist - cannot proceed.")
    else:
        print("Directories check OK")

    try:
        supported_repos = read_supported_repos()
    except:
        raise Exception("Error in reading list of supported repositories - cannot proceed.")
    
    if (os.name == 'nt'):           # Testing in Windows
        print("Supported Repositories:")
        for repo in supported_repos:
            print(repo.strip())
    
    try:
        DB_FILE = initialize_db(DATA_DIR)
    except:
        raise Exception("Error in initializing database - cannot proceed.")

    try:
        initialize_githubber()
    except:
        raise Exception("Error in initializing githubber - cannot proceed.")

    if (os.name == 'nt'):           # Testing in Windows
        print(f"Sqlite3 database '{DB_FILE}' initialized successfully.")

    # Application main loop
    while True:
        print ("Checking for new published GitHub releases in supported repos...")

        # Release checking main loop
        for repo in supported_repos:
            repo = repo.strip()
            print(f"Checking {repo}...")

            # Get the latest release data from the repository and parse it
            try:
                latestRelease = getRelease(repo, 'latest')
                URL, relname, filename, version, date, relnotes, html_url  = parse_release_data(latestRelease)
            except:
                print(f"Error in getting latest release data from {repo}. Skipping this repository.")
                continue

            # Is this a development release?
            if False == ("-dev" in relname or "_dev" in relname):
                print(f"Release {relname} is not a development release. Skipping...")
                continue

            # Check if the release is already in the database
            try:
                if release_exist(DB_FILE, repo, relname):
                    print(f"Release {relname} already exists in the database.")
                    continue
            except:
                print(f"Error in checking if release {relname} exists in the database. Skipping this release.")
                continue
            
            # Download the APK file of the release (the first file with .apk in its name)
            try:
                print(f"Release {relname} not found in the database. Downloading APK file...")
                download_apk_file(URL, filename)
            except:
                print(f"Error in downloading apk file {filename}. Skipping this release {relname}.")
                continue

            # Double-check that the file was downloaded successfully
            if not os.path.exists(filename):
                print(f"Problem in downloading file {filename}. Skipping this release {relname}.")
                continue

            # Get metadata from the APK file
            try:
                apk_packageName, apk_versionName, apk_versionCode, apk_application = get_apk_info(filename)
            except:
                print(f"Error in getting APK info from {filename}. Skipping this release {relname}.")
                continue

            orgfilename = filename

            # Make sure the apk file name contain the version name in it
            try:
                if False == (apk_versionName in filename):
                    # Fix the filename to contain the version name and version code
                    new_filename = filename.replace(".apk", "")
                    new_filename = new_filename + "-v" + apk_versionName + "." +  apk_versionCode + ".apk"
                    os.rename(filename, new_filename)
                    filename = new_filename
                    print(f"Renamed {filename} to {new_filename}")
            except:
                print(f"Error in renaming file {orgfilename}. Skipping this release {relname}.")
                continue

            """
            filename = 'com.nordicid.yarfid-1.1.0.5.apk'
            orgfilename = 'com.nordicid.yarfid-1.1.0.5.apk'
            apk_versionName = '1.1.0'
            apk_versionCode = '5'
            apk_packageName = 'com.nordicid.yarfid'
            apk_application = 'YARFID'
            html_url = 'https://github.com/NordicID/YARFID/'
            """

            try:
                add_apk_to_fdroid(filename, apk_versionName, apk_versionCode, apk_packageName, apk_application, html_url, relnotes)
            except:
                print(f"Error in adding APK file {filename} to fdroid. Skipping this release {relname}.")
                continue






        print("Checking done. Waining for 5 minutes before next check...")
        time.sleep(5 * 60)


 
