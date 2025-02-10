import os
import shutil
import tarfile
import argparse
import subprocess
import sys

PACKAGES_DIR = os.path.expanduser("~/.lepkg/.packages")

def create_package(source_dir, output_file=None):
    if not os.path.exists(source_dir):
        print(f"Directory {source_dir} does not exist.")
        return

    if output_file is None:
        output_file = f"{os.path.basename(source_dir)}.lepkg"

    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

    print(f"Package {output_file} created successfully.")

def find_makefile(directory):
    for root, _, files in os.walk(directory):
        if "Makefile" in files:
            return os.path.join(root, "Makefile")
    return None

def extract_package(package_file):
    if not os.path.exists(package_file):
        print(f"File {package_file} does not exist.")
        return

    package_name = os.path.splitext(os.path.basename(package_file))[0]
    extract_dir = os.path.join(PACKAGES_DIR, package_name)

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    os.makedirs(extract_dir, exist_ok=True)

    with tarfile.open(package_file, "r:gz") as tar:
        members = tar.getmembers()
        total_files = len(members)
        for i, member in enumerate(members, 1):
            tar.extract(member, path=extract_dir)
            sys.stdout.write(f"\rExtracting: [{i}/{total_files}] {member.name}")
            sys.stdout.flush()
        print()

    print(f"Package {package_file} extracted to {extract_dir}.")

    makefile_path = find_makefile(extract_dir)
    if makefile_path:
        print(f"Makefile found: {makefile_path}")
        print("Running sudo make install...")
        try:
            process = subprocess.Popen(
                ["sudo", "make", "install"],
                cwd=os.path.dirname(makefile_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    sys.stdout.write(output)
                    sys.stdout.flush()
            print("Installation completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error during sudo make install: {e}")
            print(f"stderr: {e.stderr}")
            print(f"stdout: {e.stdout}")
        except FileNotFoundError:
            print("Error: 'make' or 'sudo' not found. Ensure they are installed.")
    else:
        print("Makefile not found, installation skipped.")

def main():
    parser = argparse.ArgumentParser(description="Utility for managing .lepkg packages.")
    parser.add_argument("-z", metavar="DIRECTORY", help="Pack a directory into a .lepkg package.")
    parser.add_argument("-i", metavar="PACKAGE", help="Install and extract a .lepkg package.")

    args = parser.parse_args()

    if args.z:
        create_package(args.z)
    elif args.i:
        extract_package(args.i)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
