"""
Uses the spams package:

http://spams-devel.gforge.inria.fr/index.html

Use with python via e.g https://anaconda.org/conda-forge/python-spams
"""

from __future__ import division

import numpy as np
import cv2 as cv
import spams
import matplotlib.pyplot as plt
from numba import njit
import time
import logging


##########################################

def read_image(path):
    """
    Read an image to RGB uint8
    :param path:
    :return:
    """
    im = cv.imread(path)
    im = cv.cvtColor(im, cv.COLOR_BGR2RGB)
    return im


def show_colors(C):
    """
    Shows rows of C as colors (RGB)
    :param C:
    :return:
    """
    n = C.shape[0]
    for i in range(n):
        if C[i].max() > 1.0:
            plt.plot([0, 1], [n - 1 - i, n - 1 - i], c=C[i] / 255, linewidth=20)
        else:
            plt.plot([0, 1], [n - 1 - i, n - 1 - i], c=C[i], linewidth=20)
        plt.axis('off')
        plt.axis([0, 1, -1, n])


def show(image, now=True, fig_size=(10, 10)):
    """
    Show an image (np.array).
    Caution! Rescales image to be in range [0,1].
    :param image:
    :param now:
    :param fig_size:
    :return:
    """
    image = image.astype(np.float32)
    m, M = image.min(), image.max()
    if fig_size != None:
        plt.rcParams['figure.figsize'] = (fig_size[0], fig_size[1])
    plt.imshow((image - m) / (M - m), cmap='gray')
    plt.axis('off')
    if now == True:
        plt.show()


def build_stack(tup):
    """
    Build a stack of images from a tuple of images
    :param tup:
    :return:
    """
    N = len(tup)
    if len(tup[0].shape) == 3:
        h, w, c = tup[0].shape
        stack = np.zeros((N, h, w, c))
    if len(tup[0].shape) == 2:
        h, w = tup[0].shape
        stack = np.zeros((N, h, w))
    for i in range(N):
        stack[i] = tup[i]
    return stack


def patch_grid(ims, width=5, sub_sample=None, rand=False, save_name=None):
    """
    Display a grid of patches
    :param ims:
    :param width:
    :param sub_sample:
    :param rand:
    :return:
    """
    N0 = np.shape(ims)[0]
    if sub_sample == None:
        N = N0
        stack = ims
    elif sub_sample != None and rand == False:
        N = sub_sample
        stack = ims[:N]
    elif sub_sample != None and rand == True:
        N = sub_sample
        idx = np.random.choice(range(N), sub_sample, replace=False)
        stack = ims[idx]
    height = np.ceil(float(N) / width).astype(np.uint16)
    plt.rcParams['figure.figsize'] = (18, (18 / width) * height)
    plt.figure()
    for i in range(N):
        plt.subplot(height, width, i + 1)
        im = stack[i]
        show(im, now=False, fig_size=None)
    if save_name != None:
        plt.savefig(save_name)
    plt.show()


######################################

def standardize_brightness(I):
    """

    :param I:
    :return:
    """
    p = np.percentile(I, 90)
    return np.clip(I * 255.0 / p, 0, 255).astype(np.uint8)


def remove_zeros(I):
    """
    Remove zeros, replace with 1's.
    :param I: uint8 array
    :return:
    """
    mask = (I == 0)
    I[mask] = 1
    return I


def RGB_to_OD(I):
    """
    Convert from RGB to optical density
    :param I:
    :return:
    """
    I = remove_zeros(I)
    return -1 * np.log(I / 255)


def OD_to_RGB(OD):
    """
    Convert from optical density to RGB
    :param OD:
    :return:
    """
    return (255 * np.exp(-1 * OD)).astype(np.uint8)


def normalize_rows(A):
    """
    Normalize rows of an array
    :param A:
    :return:
    """
    return A / np.linalg.norm(A, axis=1)[:, None]


def notwhite_mask(I, thresh=0.8):
    """
    Get a binary mask where true denotes 'not white'
    :param I:
    :param thresh:
    :return:
    """
    I_LAB = cv.cvtColor(I, cv.COLOR_RGB2LAB)
    L = I_LAB[:, :, 0] / 255.0
    return (L < thresh)


def sign(x):
    """
    Returns the sign of x
    :param x:
    :return:
    """
    if x > 0:
        return +1
    elif x < 0:
        return -1
    elif x == 0:
        return 0

from sklearn.feature_extraction.image import extract_patches_2d
from patchify import patchify


@njit
def transform_return(source_concentrations, stain_matrix_target, maxC_target, maxC_source):
    source_concentrations *= (maxC_target / maxC_source)
    # return (255 * np.exp(-1 * np.dot(source_concentrations, stain_matrix_target).reshape(I_shape))).astype(
    #     np.uint8)
    return (255 * np.exp(-1 * np.dot(source_concentrations, stain_matrix_target))).astype( #removed reshape, should be right format already
        np.uint8)



def get_concentrations_target(I, stain_matrix, lamda=0.01):
    """
    Get concentrations, a npix x 2 matrix
    :param I:
    :param stain_matrix: a 2x3 stain matrix
    :return:
    """
    OD = RGB_to_OD(I).reshape((-1, 3))
    try:
        temp = spams.lasso(OD.T, D=stain_matrix.T, mode=2, lambda1=lamda, pos=True).toarray().T
    except Exception as e:
        print(e)
        temp = None
    return temp

# def _get_concentrations_source_patch(patch, stain_matrix, patch_list, order_list, idx, lamda=0.01):
#     OD = RGB_to_OD(patch).reshape((-1, 3)) #.astype('float32') #change from float64 to float32, half memory

#     try:
#         temp = spams.lasso(OD.T, D=stain_matrix.T, mode=2, lambda1=lamda, pos=True).toarray().T 
#     except Exception as e:
#         print(e)
#         temp = None

#     patch_list.append(temp) #save into list to unpatchify later

#     #clean up memory just in case
#     del temp
#     del OD

#     return temp


from concurrent import futures
from tqdm import tqdm
from typing import Dict, Tuple
import os

def get_concentrations_source(I, stain_matrix, lamda=0.01):
    """
    Split the image I into big patches, loop over them, to OD + reshape, norm, reshape to I
    and in the end stitch the big patches together for the entire image again

    Get concentrations, a npix x 2 matrix
    :param I:
    :param stain_matrix: a 2x3 stain matrix
    :return:
    """

    # logging.basicConfig(filename='norm-log.txt')
    # print = logging.info
    # patchify returns a NumPy array with shape (n_rows, n_cols, 1, H, W, N), if image is N-channels.
    # H W N is Height Width N-channels of the extracted patch
    # n_rows is the number of patches for each column and n_cols is the number of patches for each row
    I_shape = I.shape
    print(f"Size of WSI: {I_shape}")

    if (I_shape[0] + I_shape[1]) > 30e3: #bigger than 30k edge pixels combined, i.e. 15k x 15k
        split=True
        x = 2
        print(f'Splitting WSI into {x*x} for normalisation...')
        begin = time.time()
        # print("Going into RGB->OD and spams Lasso function...")
        patches_shape = (I_shape[0]//x, I_shape[1]//x)
        # patches = []
        patches_shapes_list=[]
        patch_list =[]
        begin_time_list = []
        with futures.ThreadPoolExecutor(min(32, os.cpu_count())) as executor:
            future_coords: Dict[futures.Future, int] = {}
            for i in range(I_shape[0]//patches_shape[0]):
                for j in range(I_shape[1]//patches_shape[1]):
                    patch = I[(i*patches_shape[0]):(i*patches_shape[0]+patches_shape[0]), (j*patches_shape[1]):(j*patches_shape[1]+patches_shape[1])]
                    patches_shapes_list.append(patch.shape) #TODO: Reorder this before returning it out of this fcn
                    future = executor.submit(
                        get_concentrations_target, patch, stain_matrix)
                    print(f'Submitted patch #{2*i+j} into thread...')
                    begin_time_list.append(time.time())
                    future_coords[future] = 2*i + j # index 0 - 3. (0,0) = 0, (0,1) = 1, (1,0) = 2, (1,1) = 3
                    #print(2*i + j)
                    # patches.append(patch)
                    # patches_shapes_list.append(patch.shape)
        begin = time.time()
        patch_list = np.zeros((x*x, I_shape[0]//x*I_shape[1]//x, 2), dtype=np.float64)

        for tile_future in futures.as_completed(future_coords):
            i = future_coords[tile_future]
            print(f'Received normalised patch #{i} from thread in {time.time()-begin_time_list[i]} seconds')
            patch = tile_future.result()
            # patch_list.append(patch)
            # # idx_list.append((i,j))
            # # print(i,j)
            # a = I_shape[0]//x * i
            # b = I_shape[1]//x * j
            patch_list[i] = patch
        
        # patches = np.array(patches)
        #breakpoint()

        del I

        
        #TODO: Enable multithreading for each tile in the normalisation
        # with futures.ThreadPoolExecutor(min(32, os.cpu_count())) as executor:
        #     future_coords: Dict[futures.Future, Tuple[int, int]] = {}
        #     for i in range(x*x):
        #         patch = patches[i]
        #         future = executor.submit(
        #             get_concentrations_target, patch, stain_matrix)
        #         future_coords[future] = (i,j)

        # for tile_future in tqdm(futures.as_completed(future_coords), total=x*x, desc=f'Normalising {x*x} WSI tiles', leave=False):
        #     i, j = future_coords[tile_future]
        #     patch = tile_future.result()
        #     patch_list.append(patch)
        #     idx_list.append((i,j))


        # idx_list_1d = []
        # for idx in idx_list:
        #     if idx == (0,0):
        #         idx_list_1d.append(0)
        #     elif idx == (0,1):
        #         idx_list_1d.append(1)
        #     elif idx == (1,0):
        #         idx_list_1d.append(2)
        #     elif idx == (1,1):
        #         idx_list_1d.append(3)           

        # patch_list = np.array(patch_list)
        # patch_list = patch_list[np.array(idx_list_1d)] #(1, 0, 2, 3)
        # patchshape_list = np.array(patchshape_list)
        # patchshape_list = patchshape_list[idx_list]

        end = time.time()
        print(f"\nFinished RGB->OD and spams Lasso function: {end-begin}")
        return patch_list, patches_shapes_list, len(patches_shapes_list), split
    
    else:
        print('Normalising WSI as a whole...')
        split=False
        begin = time.time()
        print("Going into RGB->OD and spams Lasso function...")
        temp = get_concentrations_target(I, stain_matrix)
        end = time.time()
        print(f"Finished RGB->OD and spams Lasso function: {end-begin}")

        return temp, None, None, split

