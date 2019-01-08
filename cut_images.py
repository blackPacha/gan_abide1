#!/bin/python

'''
Script to cut 3D MRIs
'''


import nibabel as nib
import numpy as np
import os


def get_sub_ids_abide1(list_of_imgs_files):
    sub_ids = []
    for el in list_of_imgs_files:
        sub_ids.append(el.split("_")[0].split("-")[-1])
    return sub_ids


def cut_3d_image(img, x_size_of_filter, y_size_of_filter, z_size_of_filter):
    '''

    :param img:
    :return:
    '''
    # test if it is a 3D img
    try:
        check_img_size(img)
    except:
        return "Error of entry in cut_3d_image: The image has to be 3 dimensional"

    try:
        check_size_of_filter(x_size_of_filter)
        check_size_of_filter(y_size_of_filter)
        check_size_of_filter(z_size_of_filter)
    except:
        return "Error of entry in cut_3d_image: The size of filter has to be an integer"

    x = img.shape[0]
    y = img.shape[1]
    z = img.shape[2]
    new_img = []

    while x / x_size_of_filter > 0:
        while y / y_size_of_filter > 0:
            while z / z_size_of_filter > 0:
                new_img.append(img[range(x - x_size_of_filter, x), :, :][:, range(y - y_size_of_filter, y), :][:, :,
                               range(z - z_size_of_filter, z)])
                z -= z_size_of_filter
            y -= y_size_of_filter
            z = img.shape[2]
        x -= x_size_of_filter
        y = img.shape[1]

    return new_img


def check_img_size(img):
    assert len(img.shape) == 3


def check_size_of_filter(size_of_filter):
    assert type(size_of_filter) == int


def build_new_imgs(list_of_imgs_files, x_size_of_filter, y_size_of_filter, z_size_of_filter):
    new_imgs = []
    sum_imgs = []
    for file in list_of_imgs_files:
        img = nib.load(file).get_data()
        new_img = cut_3d_image(img, x_size_of_filter, y_size_of_filter, z_size_of_filter)
        sum_imgs.append(list(map(lambda x: np.sum(x), new_img)))
        new_imgs.append(new_img)

    # test length of new_imgs
    try:
        check_new_imgs_len(new_imgs, list_of_imgs_files)
    except:
        return "Error in build_new_imgs: missing original images in new_imgs"
    # test all the same size to build array
    try:
        check_new_imgs_shapes(new_imgs)
    except:
        return "Error in build_new_imgs: cannot sum imgs with not the same length"
    return new_imgs


def check_new_imgs_len(new_imgs, list_of_imgs_files):
    print(type(len(new_imgs)), type(len(list_of_imgs_files)))
    assert len(new_imgs) == len(list_of_imgs_files)


def check_new_imgs_shapes(new_imgs_shape):
    for i in range(len(new_imgs_shape)-1):
        for j in range(i+1, len(new_imgs_shape)):
            assert len(new_imgs[i]) == len(new_imgs[j])


def sum_new_img(new_img):
    return list(map(lambda x: np.sum(x), new_img))
    #L = []
    #for i in range(len(new_img)):
    #    print(i)
    #    L.append(np.sum(new_img[i]))
    #return L


def build_sum_imgs(new_imgs):
    sum_imgs = []
    for new_img in new_imgs:
        sum_imgs.append(sum_new_img(new_img))
    return list(np.sum(np.array(sum_imgs), 0))


def builg_affine_list(list_of_imgs_files):
    affine_list = []
    for file in list_of_imgs_files:
        affine_list.append(nib.load(file).affine)
    return affine_list


def transform_into_nifti(img_array, affine):
    img_nii = nib.Nifti1Image(img_array, affine)
    return img_nii


def build_save_new_imgs_nifti(new_imgs, affine_list, sum_imgs, outdir, sub_ids):
    for i in range(len(new_imgs)):
        affine = affine_list[i]

        # add condition: if sum_list[i] positive ok

        for j, img_array in enumerate(new_imgs[i]):
            if sum_imgs[j] > 0:
                img_nii = transform_into_nifti(img_array, affine)
                outpath = outdir + "/" + sub_ids[i] + "_" + str(j) + ".nii.gz"
                save_new_img(img_nii, outpath)


def save_new_img(img_nii, outpath):
    nib.save(img_nii, outpath)


if __name__ == '__main__':
    list_of_imgs_files = list(map(lambda x: "/anatpreproc/ABIDE_1/cpac_registered/" + x, os.listdir("/anatpreproc/ABIDE_1/cpac_registered")))[0:3]
    outdir = '/anatpreproc/ABIDE_1/cpac_sampling/'
    x_size_of_filter = 16
    y_size_of_filter = 16
    z_size_of_filter = 16

    sub_ids = get_sub_ids_abide1(list_of_imgs_files)
    affine_list = builg_affine_list(list_of_imgs_files)
    # build a list of new cut images for each original image, and put it in a list
    new_imgs = build_new_imgs(list_of_imgs_files, x_size_of_filter, y_size_of_filter, z_size_of_filter)
    # to check if several new images can be removed (zero images)
    #sum_imgs = build_sum_imgs(new_imgs)
    #build_save_new_imgs_nifti(new_imgs, affine_list, sum_imgs, outdir, sub_ids)

