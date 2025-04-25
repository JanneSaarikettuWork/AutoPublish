#!/usr/bin/python3

import os


# Define the subdirectories - todo: check ROOT_DIR_POSIX when taking to production
ROOT_DIR_POSIX      = "/mnt/c/Users/janne.saarikettu/source/repos/misc/AppcAutoPublish/TestAppC_AutoPublish/"   # For production in Linux
ROOT_DIR_NT         = r"C:\Users\janne.saarikettu\source\repos\misc\AppcAutoPublish\AutoPublish"                # For testing in Windows
ROOT_DIR            = "" # Set to empty string to be set later based on OS

DATA_DIR            = "data"
BUILD_REPO_DIR      = "build_environment/repo"
BUILD_METADATA_DIR  = "build_environment/metadata" 
RUN_BACKUP_DIR      = "run_environment/backup"
RUN_REPO_DIR        = "run_environment/repo"

SUPPORTED_REPOS_FILE = os.path.join(DATA_DIR, "supported_repos")


def check_directories():
    """Check if a directory exists."""
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

    # Are we running in Windows or Linux?
    global ROOT_DIR
    if (os.name == 'nt'):           # Testing in Windows
        ROOT_DIR = ROOT_DIR_NT
    else:
        ROOT_DIR = ROOT_DIR_POSIX

    # Check if the root directory exists
    if not os.path.exists(ROOT_DIR):
        print(f"Directory {ROOT_DIR} does not exist.")
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

    os.chdir(ROOT_DIR)

    try:
        supported_repos = read_supported_repos()
    except:
        raise Exception("Error in reading list of supported repositories - cannot proceed.")
    
    if (os.name == 'nt'):           # Testing in Windows
        print("Supported Repositories:")
        for repo in supported_repos:
            print(repo.strip())
    

    