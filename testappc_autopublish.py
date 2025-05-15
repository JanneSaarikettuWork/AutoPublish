#!/usr/bin/python3

import os
from sys import exception
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
        logger.debug(f"Directory {ROOT_DIR} does not exist.")
        return False

    os.chdir(ROOT_DIR)

    if not os.path.exists(DATA_DIR):
        logger.error(f"Directory {DATA_DIR} does not exist.")
        return False
    if not os.path.exists(BUILD_REPO_DIR):
        logger.error(f"Directory {BUILD_REPO_DIR} does not exist.")
        return False
    if not os.path.exists(BUILD_METADATA_DIR):
        logger.error(f"Directory {BUILD_METADATA_DIR} does not exist.")
        return False
    if not os.path.exists(RUN_BACKUP_DIR):
        logger.error(f"Directory {RUN_BACKUP_DIR} does not exist.")
        return False
    if not os.path.exists(RUN_REPO_DIR):
        logger.error(f"Directory {RUN_REPO_DIR} does not exist.")
        return False

    return True

def read_supported_repos():
    """Reads all lines from the specified file."""
    if not os.path.exists(SUPPORTED_REPOS_FILE):
        raise FileNotFoundError(f"The file '{SUPPORTED_REPOS_FILE}' does not exist.")
    with open(SUPPORTED_REPOS_FILE, 'r') as file:
        return file.readlines()


if __name__ == "__main__":

    # Set up the logger to log to both console and file
    log_dir_path  = os.path.join(ROOT_DIR, LOG_DIR)
    log_file_path = os.path.join(log_dir_path, LOG_FILE)
    try:
        if not os.path.exists(log_dir_path):
            os.makedirs(log_dir_path)
        setup_logging(logger, log_file_path)    
    except Exception as e:
        error_msg = f"Error in setting up logging to directory {log_dir_path} - cannot proceed"
        print(f"{error_msg}: {e}")
        raise
    else:
        logger.info("")
        logger.info("************************ Starting the application ************************")
        logger.info(f"Logging set up successfully in '{log_file_path}'")

    # Initial checks - stop if any of the checks fail
    # Directories
    if not check_directories():
        error_msg = "One or more directories do not exist - cannot proceed."
        logger.critical(error_msg)
        raise Exception(error_msg)
    else:
        logger.debug("Directories check OK")

    # Supported repositories
    try:
        supported_repos = read_supported_repos()
    except Exception as e:
        error_msg = "Error in reading list of supported repositories - cannot proceed" 
        logger.exception(error_msg)
        raise # re-raise the original exception to stop the program
    else:
        logger.debug("Supported repositories read successfully.")

    repos_str = "\n\tSupported repositories:"
    for repo in supported_repos:
        repos_str += f"\n\t - {repo.strip()}"
    logger.info(repos_str)

    # logger.debug("Supported Repositories:")
    # for repo in supported_repos:
    #     logger.debug(repo.strip())

    # Database
    try:
        DB_FILE = initialize_db(DATA_DIR)
    except:
        error_msg = "Error in initializing Sqlite3 database '{DB_FILE}' - cannot proceed"
        logger.exception(error_msg)
        raise
    else:
        logger.debug(f"Sqlite3 database '{DB_FILE}' initialized successfully.")
    
    # GitHub access
    try:
        initialize_githubber()
    except:
        error_msg = "Error in initializing githubber - cannot proceed."
        logger.exception(error_msg)
        raise
    else:
        logger.debug("Githubber initialized successfully.")

    logger.info("Initialization and initial checking done")

    # ---------------------
    # Application main loop
    # ---------------------
    while True:
        logger.info("----------------------------------------------------------------")
        logger.info("Checking for new published GitHub releases in supported repos...")
        changes_made_to_fdroid = False

        # The main loop - continue and try again if any of the checks fail
        try:
            supported_repos = read_supported_repos()
        except:
            error_msg = "Error in reading list of supported repositories. Retry in 60 seconds..."
            logger.exception(error_msg)
            time.sleep(60)
            continue

        # ---------------------
        # Release checking main loop
        # ---------------------
        for repo in supported_repos:
            repo = repo.strip()
            logger.info(f"Checking {repo}...")

            # Get the latest release data from the repository and parse it
            try:
                latestRelease = getRelease(repo, 'latest')
                URL, relname, filename, version, date, relnotes, html_url  = parse_release_data(latestRelease)
            except Exception as e:
                error_msg = f"Error in getting latest release data from {repo}. Skipping this repository"
                logger.exception(error_msg)
                continue
            else:
                logger.debug(f"Latest release data from {repo} parsed successfully.")

            # Is this a development release?
            if False == ("-dev" in relname or "_dev" in relname):
                logger.debug(f"Release {relname} is not a development release. Skipping...")
                continue
            else:
                logger.debug(f"Release {relname} is a development release. Proceeding...")

            # Check if the release is already in the database
            try:
                if release_exist(DB_FILE, repo, relname):
                    logger.debug(f"{repo} release {relname} already exists in the database. Skip.")
                    continue
            except Exception as e:
                error_msg = f"Error in checking if release {relname} exists in the database. Skipping this release {relname}."
                logger.exception(error_msg)
                continue
            else:
                logger.debug(f"Release {relname} not found in the database. Proceeding...")

            # Download the APK file of the release (the first file with .apk in its name)
            try:
                logger.debug(f"Start downloading APK file of release {relname}...")
                download_apk_file(URL, filename)
            except Exception as e:
                error_msg = f"Error in downloading APK file {filename}. Skipping this release {relname}."
                logger.exception(error_msg)
                continue
            else:
                logger.debug(f"APK file {filename} of release {relname} downloaded successfully.")

            # Double-check that the file was downloaded successfully
            if not os.path.exists(filename):
                logger.error(f"Problem in accessing file {filename}. Skipping this release {relname}.")
                continue

            # Get metadata from the APK file
            try:
                apk_packageName, apk_versionName, apk_versionCode, apk_application = get_apk_info(filename)
            except Exception as e:
                error_msg = f"Error in extracting APK info from {filename}. Skipping this release {relname}."
                logger.exception(error_msg)
                continue
            else:
                logger.debug(f"APK info from {filename} extracted successfully.")

            orgfilename = filename

            # Make sure the apk file name contain the version name in it
            try:
                if False == (apk_versionName in filename):
                    # Fix the filename to contain the version name and version code
                    new_filename = filename.replace(".apk", "")
                    new_filename = new_filename + "-v" + apk_versionName + "." +  apk_versionCode + ".apk"
                    os.rename(filename, new_filename)
                    filename = new_filename
                    logger.debug(f"Renamed {orgfilename} to {filename}")
            except Exception as e:
                error_msg = f"Error in renaming file {orgfilename} to {filename}. Skipping this release {relname}."
                logger.exception(error_msg)
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

            # Add the APK file to the F-Droid build directory and update metadata
            try:
                add_apk_to_fdroid(filename, apk_versionName, apk_versionCode, apk_packageName, apk_application, html_url, relnotes)
            except Exception as e:
                error_msg = f"Error in adding APK file {filename} to fdroid. Skipping this release {relname}."
                logger.exception(error_msg)
                continue
            else:
                logger.debug(f"APK file {filename} added to fdroid successfully.")

            # All successfully done - add the release to the database
            try:
                insert_record(DB_FILE, repo, relname, apk_packageName, apk_versionName, apk_versionCode, date)
            except Exception as e:
                error_msg = f"Error in adding release {relname} to the database. Skipping this release {relname}."
                logger.exception(error_msg)
                continue
            else:
                logger.debug(f"Release {relname} added to the database successfully.")

            formatted_db_info = f"""
            Added new release to the database:
            - GitHub repo:  {repo}
            - Release:      {relname}
            - PackageName:  {apk_packageName}
            - VersionName:  {apk_versionName}
            - VersionCode:  {apk_versionCode}
            - Release date: {date}"""
            logger.info(formatted_db_info)

            changes_made_to_fdroid = True
            #--------------------------------
            # Release checking main loop - end
            #--------------------------------

        # Application main loop
        # If changes were made to the F-Droid repository, run the fdroid update command,
        # make a backup of the current run environment and copy the build result as a 
        # new run environment
        if changes_made_to_fdroid:
            try:
                update_fdroid_Linux()
            except Exception as e:
                error_msg = f"Error in updating F-Droid repository. Skipping this round."
                logger.exception(error_msg)
                continue
            else:
                logger.info("F-Droid repository updated successfully.")

            try:
                backup_and_copy_build_to_run_environment()
            except Exception as e:
                error_msg = f"Error in backing up old run environment and/or copying build to run environment. Skipping this round."
                logger.exception(error_msg)
                continue
            else:
                logger.info("Old run environment backed up and build copied as a new run environment.")

        logger.info("Checking done. Waiting for 5 minutes before next check...")
        time.sleep(5 * 60)
        


