import pydicom
import pydicom._storage_sopclass_uids
import matplotlib.pyplot as plt


class IMAConverter:
    def __init__(self, ima_file_path):
        self.ima_file_path = ima_file_path

    def save_IMA_ImageFrame(self, path):
        # you can use this function to show your IMA file image frames
        dcm_dataset = pydicom.dcmread(self.ima_file_path)
        plt.imsave(path, dcm_dataset.pixel_array, cmap='gray')

    # -------------------------------------------------------------------------
    def IMA_MetaData_ToDict(self):
        dcm_dataset = pydicom.dcmread(self.ima_file_path)
        return dcm_dataset
