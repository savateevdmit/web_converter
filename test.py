from converter import IMAConverter
from os import listdir
from os.path import isfile, join
import time, os, zipfile, shutil


def conv(upload):
    archive = f'media/{upload}'
    with zipfile.ZipFile(archive, 'r') as zip_file:
        zip_file.extractall(archive.split('.')[0])


    file_name = archive.split('.')[0]
    only_ima = [f for f in listdir(file_name) if isfile(join(file_name, f)) and '.IMA' in join(file_name, f)]

    directory = f'{file_name}++{int(time.time()) + 86400}'
    os.makedirs(directory, exist_ok=True)

    # number = 1
    # last_description = ''
    count = 0

    for name in only_ima:
        ima_converter = IMAConverter(join(file_name, name))
        metadata = ima_converter.IMA_MetaData_ToDict()

        # if last_description != metadata.SeriesDescription:
        #     number = 1

        path_to_image = f"{directory}/{str(metadata.SeriesDescription).split('] ')[-1].replace(' ', '_')} {count}.png"
        # number += 1
        count += 1

        # last_description = metadata.SeriesDescription

        ima_converter.save_IMA_ImageFrame(path_to_image)

    shutil.rmtree(file_name)

    old_files = [f for f in listdir('media') if '++' in f]

    for file in old_files:
        if 'zip' not in file:
            if int(file.split('++')[-1]) <= time.time():
                shutil.rmtree(f'media/{file}')
        else:
            if int(file.split('++')[-1].split('.')[0]) <= time.time():
                os.remove(f'media/{file}')

    return directory.split('/')[-1]