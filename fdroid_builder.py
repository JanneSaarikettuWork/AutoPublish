import os

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

    # Add release notes to the changelog file
    changelog_file = os.path.join(changelog_subdirectory, f"{apk_versionCode}.txt")
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
            f.write(f"SourceCode: {html_url}\n")
            f.write(f"Summary: 'Development release of {apk_application}.\n")
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
    os.rename(filename, destination_apk_path)
    print(f"Moved APK file to {destination_apk_path}")


