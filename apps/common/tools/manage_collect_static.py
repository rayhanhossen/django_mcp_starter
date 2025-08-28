"""
This file is needed only when we are using django.contrib.staticfiles.storage.ManifestStaticFilesStorage.
The primary objective of this file is to generate synthetic files when executing the collectstatic method to resolve conflicts with missing asset files.
Execute this file from the directory where the "manage.py" file is located.
"""

import os
import subprocess
import re

def manage_collect_static():
        try:
                process = subprocess.Popen(
                        ["python", "manage.py", "collectstatic", "--clear", "--noinput"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                )

                stdout, stderr = process.communicate()
                exit_code = process.returncode

                if exit_code != 0:
                        error_lines = [line for line in stderr.splitlines() if "ValueError:" in line]
                        raise Exception(error_lines[0])
                else:
                        print("Method CollectStatic ended successfully.")

        except Exception as e:
                print(e)
                print("Generating empty file...")

                text = str(e)
                pattern = r"'(.*?)'"
                file_paths = re.findall(pattern, text)

                absolute_file_path = os.getcwd() + '/home/static/' + file_paths[0]
                directory = os.path.dirname(absolute_file_path)

                if not os.path.exists(directory):
                        os.makedirs(directory)

                with open(absolute_file_path, 'w') as new_file:
                        new_file.write("This is file is generated to resolve conflicts with asset file redirection when executing the collectstatic method.")

                print(f"File '{absolute_file_path}' has been created.")
                print("Retrying CollectStatic...")

                return manage_collect_static()

manage_collect_static()
