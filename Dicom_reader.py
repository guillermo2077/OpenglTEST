import pydicom
import numpy as np
import os

# slice thickness: in mm
# pixel spaciong: separacion real entre [filas, columnas] en mm

# assign directory


class DicomParse:

    def __init__(self, path):

        # Class attributes
        self.pixel_data_xyz = None
        self.pixel_data_after_threshold = None

        # Count number of valid dicom files
        count = 0
        for file in os.scandir(path):
            count += 1

        # Obtain parameters in first iter and fill pixel data for each file
        parameters_obtained = False
        for i, filename in enumerate(os.scandir(path)):
            ds = pydicom.dcmread(filename)

            if not parameters_obtained:
                self.pixel_spacing = ds[0x0028, 0x0030].value
                self.slice_thickness = ds[0x0018, 0x0050].value
                self.shape = [count, ds[0x0028, 0x0010].value, ds[0x0028, 0x0011].value]

                vol_shape = tuple(self.shape)
                print("Niveles, filas, columnas" + str(vol_shape))
                self.pixel_data = np.empty(shape=vol_shape, dtype=np.ubyte)

                parameters_obtained = True

            self.pixel_data[i] = ds.pixel_array

    def getPixelData(self):
        return self.pixel_data

    def obtainThresholdImage(self, upper=255, lower=0):
        self.pixel_data_after_threshold = (self.pixel_data <= upper) * (self.pixel_data >= lower)
        print("pixel data shape {}".format(self.pixel_data_after_threshold))
        print(sum(self.pixel_data_after_threshold))
        self.pixel_data_xyz = np.argwhere(self.pixel_data_after_threshold > 0).flatten().astype('float32')
        # self.pixel_data_xyz = np.rot90(self.pixel_data_xyz, 1, axes=(0,))
        print("pixel data shape {}".format(self.pixel_data_xyz.shape))


    def getPixelDataAfterThreshold(self):
        return self.pixel_data_after_threshold

    def getPixelDataXYZ(self):
        return self.pixel_data_xyz

    def centerXYZ(self):
        mean_z = min(self.pixel_data_xyz[0::3]) + max(self.pixel_data_xyz[0::3])/2
        z = (self.pixel_data_xyz[0::3] - mean_z)/20
        mean_x = min(self.pixel_data_xyz[1::3]) + max(self.pixel_data_xyz[1::3])/2
        x = (self.pixel_data_xyz[1::3] - mean_x)/20
        mean_y = min(self.pixel_data_xyz[2::3]) + max(self.pixel_data_xyz[2::3])/2
        y = (self.pixel_data_xyz[2::3] - mean_y)/20

        self.pixel_data_xyz[0::3] = x
        self.pixel_data_xyz[1::3] = y
        self.pixel_data_xyz[2::3] = z

# d1 = DicomParse("dicomFiles/ANGIO-CT")

# d1.obtainThresholdImage(150, 110)

# image1 = d1.getPixelDataAfterThreshold()[100]
# image2 = d1.getPixelData()[100]

# print(d1.getPixelDataXYZ())
