import json
import os
import re
import subprocess
import time

import requests


def initialize_githubber():
    global token
    token = os.environ['GITHUB_TOKEN']

def communicate(url):
    """Communicates with the GitHub API to fetch release data."""
    for retry in range(3):
        if (os.name == 'nt'):   # Testing in Windows
            proc = subprocess.Popen(['curl', '-H' 'Authorization: token {}'.format(token), url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:                   # Running in Linux
            proc = subprocess.Popen(['/usr/bin/curl', '-H' 'Authorization: token {}'.format(token), url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()
        if proc.returncode == 0:
            try:
                return json.loads(stdout.decode('utf-8'))
            except:
                pass
        if retry < 2:
            print('curl: ' + stderr.decode('utf-8'))
            time.sleep(10)
            print('Retrying...')
    print('curl: ' + stderr.decode('utf-8'))


def getRelease(repo, version):
    """Fetches the release data from the GitHub API."""
    if version != 'latest':
        rels = communicate('https://api.github.com/repos/{}/releases'.format(repo))
        try:
            for rel in rels:
                if rel['tag_name'] == version:
                    release = rel
                    break
        except:
            print(json.dumps(rels))
    else:
        release = communicate('https://api.github.com/repos/{}/releases/latest'.format(repo))

    return release

def parse_release_data(release):
    """Parses the release data and returns relevant information.
    Returns:
        URL: The URL of the release asset.
        relname: The name of the release.
        filename: The name of the release asset.
        version: The version of the release.
        date: The release date.
        relnotes: The release notes.
        html_url """""

    for asset in release['assets']:
        if '.apk' in asset['name']:

            # Pick the first asset with .apk in its name
            # Some special handling will needed if the correct 
            # asset is to be picked from among multiple assets
            URL = asset['url'].strip()
            relname = release['name'].strip()
            filename = asset['name'].strip()
            version = release['tag_name'].strip()
            date = release['published_at'].strip()

            html_url = release['html_url'].strip()
            # Remove "releases" and everything after it
            if "releases" in html_url:
                html_url = html_url[:html_url.index("releases")]

            relnotes = ''
            relnote_text_to_parse = release['body'].strip()

            # Testing in Windows - convert line endings to Linux style
            if os.name == 'nt':   
                relnote_text_to_parse = relnote_text_to_parse.replace('\r\n', '\n')

            # Change potential asteriskes (*) into dashes (-) in the beginnings of the lines
            # relnote_text_to_parse = relnote_text_to_parse.replace('\n*', '\n')
            relnote_text_to_parse = re.sub('\n *\\* ', '\n- ', relnote_text_to_parse)

            # Multiline matching lines starting with dash
            data = re.compile(r'^ *\-.*$', re.MULTILINE) 
            matches = data.finditer(relnote_text_to_parse)
            for match in matches:
                # print(match.group()) # Just printing match does not seem to print the whole match, therefore group()
                relnotes += match.group() + "\n"

            relnotes = relnotes.strip()

            return URL, relname, filename, version, date, relnotes, html_url
        
    return None, None, None, None, None, None, None

# Running in Linux
def download_Linux(url, name): 
    """Downloads a file from a given URL using wget with authentication."""
    for retry in range(3):

        proc = subprocess.Popen(['sh', '-c', "wget -nv --header='Accept:application/octet-stream' --header='Authorization: token {}' -O {} {}".format(token, name, url)], stderr=subprocess.PIPE)
        _, stderr = proc.communicate()
        if proc.returncode == 0:
            if retry > 0:
                print('Success')
            return
        if retry < 2:
            print(stderr.decode('utf-8'))
            time.sleep(10)
            print('Retrying...')
    print(stderr.decode('utf-8'))

# Testing in Windows
def download_Windows(URL, filename): 
    """Downloads a file from a given URL using requests with authentication."""
    headers = {
        "Accept": "application/octet-stream",
        "Authorization": f"token {token}"
    }

    # Send the GET request
    response = requests.get(URL, headers=headers, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the file
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloading {filename} completed successfully.")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")


def download_apk_file(URL, filename):
    if (os.name == 'nt'):   # Testing in Windows
        download_Windows(URL, filename)
    else:                   # Running in Linux
        download_Linux(URL, filename)

