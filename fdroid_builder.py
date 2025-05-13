import datetime
import os
import shutil
import subprocess
import zipfile

from config import *

def add_apk_to_fdroid(filename, apk_versionName, apk_versionCode, apk_packageName, apk_application, html_url, relnotes):
    """Adds the APK file to F-Droid build directory and updates the metadata."""
    
    # Check if packageName subdirectory exits in the fdroid metadata directory
    packageName_subdirectory = os.path.join(BUILD_METADATA_DIR, apk_packageName)
    if not os.path.exists(packageName_subdirectory):
        print(f"Creating directory {packageName_subdirectory} and subdirectories")
        os.makedirs(packageName_subdirectory)
    else:
        print(f"Directory {packageName_subdirectory} exists")

    # Check (& create if needed) the rest of the packageName subdirectories
    enUS_subdirectory = os.path.join(packageName_subdirectory, "en-US")
    if not os.path.exists(enUS_subdirectory):
        os.makedirs(enUS_subdirectory)
    changelog_subdirectory = os.path.join(enUS_subdirectory, "changelog")
    if not os.path.exists(changelog_subdirectory):
        os.makedirs(changelog_subdirectory)
    screenshots_subdirectory = os.path.join(enUS_subdirectory, "phoneScreenshots")
    if not os.path.exists(screenshots_subdirectory):
        os.makedirs(screenshots_subdirectory)
        # Copy sample screenshots the created directory
        for sample_screenshot in os.listdir(DATA_DIR):
            if sample_screenshot.lower().endswith(('.jpg', '.png')):
                src = os.path.join(DATA_DIR, sample_screenshot)
                dst = os.path.join(screenshots_subdirectory, sample_screenshot)
                if not os.path.exists(dst):
                    print(f"Copying {src} to {dst}")
                    shutil.copy(src, dst)

    # Add release notes to the changelog file, if it does not exist
    changelog_file = os.path.join(changelog_subdirectory, f"{apk_versionCode}.txt")
    if not os.path.exists(changelog_file):
        with open(changelog_file, 'w') as f:
            f.write(f"{relnotes}\n")

    # Check if packageName.yml file exits in the fdroid metadata directory
    packageName_yml_file = os.path.join(BUILD_METADATA_DIR, apk_packageName+".yml")

    if not os.path.exists(packageName_yml_file):
        print(f"Creating draft {packageName_yml_file} file")
        with open(packageName_yml_file, 'w') as f:
            f.write(f"AuthorName: 'Brady'\n")
            f.write(f"Categories:\n- TestAppCenter\n")
            f.write(f"CurrentVersionCode: {apk_versionCode}\n")
            f.write(f"Name: {apk_application}\n")
            f.write(f"SourceCode: '{html_url}'\n")
            f.write(f"Summary: '{apk_application} ({apk_packageName}).'\n")
            f.write(f"Description: 'Development release of {apk_application}.'\n")
            f.write(f"License: proprietary\n")
            
    else:
        # Update the yml file with the new version code
        print(f"File {packageName_yml_file} exists. Updating it with the new version code.")
        temp_yml_file = packageName_yml_file + ".tmp"

        with open(packageName_yml_file, "r") as infile:
            with open(temp_yml_file, "w") as outfile:
                for line in infile:
                    # Check if the line contains the version code
                    if "CurrentVersionCode:" in line:
                        new_line = f'CurrentVersionCode: {str(apk_versionCode)}\n'
                        outfile.write(new_line)
                    else:
                        outfile.write(line)

        ## Sanity check - not used for now
        # org_size = os.path.getsize(packageName_yml_file)
        # new_size = os.path.getsize(temp_yml_file)
        # margin = 5 # just in case if original file had some extra whitespace

        # if (new_size + margin < org_size):
        #     raise Exception(f"Something bad happened in converting {packageName_yml_file} to {temp_yml_file}")

        # Replace the original yml file with the updated temp file
        os.replace(temp_yml_file, packageName_yml_file)
        print(f"Successfully updated {packageName_yml_file} with the new version code {apk_versionCode}")


    # Move the APK file to the fdroid repo directory
    destination_apk_path = os.path.join(BUILD_REPO_DIR, os.path.basename(filename))
    # 'rename' raises exception if the file already exists, 'replace' does not
    os.replace(filename, destination_apk_path)
    print(f"Moved APK file to {destination_apk_path}")

def update_fdroid_Linux():
    """Runs the 'fdroid update' command. NOTE: This works only in Linux."""

    # Testing in Windows - cannot run fdroid update
    if (os.name == 'nt'):           
        print(f"Cannot run fdroid update in Windows. Perform this manually in Linux:\n  cd {BUILD_DIR}\n  fdroid update")
        return

    # Check if the fdroid build directory exists
    if not os.path.exists(BUILD_DIR):
        print(f"F-Droid build directory {BUILD_DIR} does not exist.")
        raise Exception(f"BUILD_DIR {BUILD_DIR} does not exist - cannot proceed.")

    # Change to the F-Droid build directory
    os.chdir(BUILD_DIR)

    # Run the fdroid build command
    # os.system("fdroid update")  # Update the repository
    try:
        result = subprocess.run(["fdroid", "update"], check=True, text=True, capture_output=True)
        print("Command output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error occurred while running 'fdroid update'")
        os.chdir(ROOT_DIR)
        raise Exception(f"Error occurred while running 'fdroid update':", e.stderr)

    # Change back to the original directory
    os.chdir(ROOT_DIR)

    print("F-Droid repository built successfully.")

def backup_and_copy_build_to_run_environment():
    """Backs up the current run environment and copies build repo directory it to the run environment."""

    # Check if the run directores exists
    if not os.path.exists(RUN_REPO_DIR):
        print(f"Run repo directory {RUN_REPO_DIR} does not exist - creating it.")
        os.makedirs(RUN_REPO_DIR)
    if not os.path.exists(RUN_BACKUP_DIR):
        print(f"Run backup directory {RUN_BACKUP_DIR} does not exist - creating it.")
        os.makedirs(RUN_BACKUP_DIR)

    # Zip the contents of current RUN_REPO_DIR
    datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"repo_{datetime_str}.zip"
    zip_filepath = os.path.join(RUN_BACKUP_DIR, zip_filename)

    print(f"Creating backup zip file of the current run environment: {zip_filepath}")

    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(RUN_REPO_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, RUN_REPO_DIR)
                zipf.write(file_path, arcname)
   
    # Empty the run repo directory
    shutil.rmtree(RUN_REPO_DIR)

    # Copy the build repo directory to the run environment
    print(f"Copying build repo directory to the run environment: {RUN_REPO_DIR}")
    shutil.copytree(BUILD_REPO_DIR, RUN_REPO_DIR)

    print(f"Backup and copy of build to run environment completed successfully.")

