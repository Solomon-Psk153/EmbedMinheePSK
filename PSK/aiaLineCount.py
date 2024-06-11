from __future__ import print_function
from __future__ import division

import glob
import ntpath
import os
import shutil
import zipfile

def unzip(source_filename, dest_dir):
    '''
    Source: http://stackoverflow.com/questions/12886768/how-to-unzip-file-in-python-on-all-oses
    '''
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)

def list_subdirectories(dir):
    '''
    Source: http://stackoverflow.com/questions/800197/get-all-of-the-immediate-subdirectories-in-python
    '''
    return list(filter(os.path.isdir, [os.path.join(dir, f) for f in os.listdir(dir)]))

def path_leaf(path):
    '''
    Source: http://stackoverflow.com/questions/8384737/python-extract-file-name-from-path-no-matter-what-the-os-path-format
    '''
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def bky_count_blocks(bky_filename):
    return open(bky_filename).read().count('<block ')

def aia_count_blocks(aia_filename):
    '''
    Count blocks in an AIA project 
    '''

    # unzip
    temp_folder = 'temp_aia'
    unzip(aia_filename, temp_folder)

    # Build path to .bky files, which contains all blocks for each screen of the AI2 project
    bky_files_path = os.path.join(temp_folder, 'src', 'appinventor')
    for i in range(6): 
        subdirs = list_subdirectories(bky_files_path)
        if not subdirs:
            raise Exception("Unable to find .bky files path, directory structure may be incorrect.")
        bky_files_path = subdirs[0] # walk inside...

    # Count
    total_blocks_count = 0
    bky_filenames = glob.glob(os.path.join(bky_files_path, '*.bky'))
    for bky_filename in bky_filenames:
        bky_block_count = bky_count_blocks(bky_filename)
        print('Screen {0} contains {1} blocks'.format(path_leaf(bky_filename), bky_block_count))
        total_blocks_count += bky_block_count
    print('The AIA project {0} contains {1} blocks spread across {2} screens.'.format(aia_filename, total_blocks_count, len(bky_filenames)))

    # Clean temp files
    shutil.rmtree(temp_folder)

def main():
    '''
    This is the main function
    '''
    aia_filename = 'seaSecretBox.aia'
    aia_count_blocks(aia_filename)

if __name__ == "__main__":
    main()
    #cProfile.run('main()') # if you want to do some profiling
