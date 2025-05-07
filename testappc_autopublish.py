#!/usr/bin/python3

import os
import time


# Define the subdirectories - todo: check ROOT_DIR_POSIX when taking to production
ROOT_DIR_POSIX      = "/mnt/c/Users/janne.saarikettu/source/repos/misc/AppcAutoPublish/AutoPublish/"   # For production in Linux
ROOT_DIR_NT         = r"C:\Users\janne.saarikettu\source\repos\misc\AppcAutoPublish\AutoPublish"       # For testing in Windows
ROOT_DIR            = "" # Set to empty string to be set later based on OS

DATA_DIR            = "data"
BUILD_REPO_DIR      = "build_environment/NidTestAppCenter/repo"
BUILD_METADATA_DIR  = "build_environment/NidTestAppCenter/metadata" 
RUN_BACKUP_DIR      = "run_environment/backup"
RUN_REPO_DIR        = "run_environment/repo"

DB_FILE = "" # Placeholder for the database file path"

SUPPORTED_REPOS_FILE = os.path.join(DATA_DIR, "supported_repos")

# Import database, GitHub and... functions
from installed_versions_db import *
from githubber import *

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
            repo += repo.strip()
            print(f"Checking {repo}...")

            latestRelease = getRelease(repo, 'latest')
            URL, relname, filename, version, date, relnotes  = parse_release_data(latestRelease)

            # Check if the release is already in the database
            if release_exist(DB_FILE, repo, relname):
                print(f"Release {relname} already exists in the database.")
                continue
            
            # The release is not in the database - download its APK file
            print(f"Release {relname} not found in the database. Downloading APK file...")
            download_apk_file(URL, filename)

            if False == os.path.exists(filename):
                print(f"Problem in downloading file {filename}. Skipping this release.")
                continue


        print("Checking done. Waining for 5 minutes before next check...")
        time.sleep(5 * 60)


 
