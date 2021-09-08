import matplotlib.pyplot as plt

import numpy as np
import skimage.transform
import skimage.io
from sklearn.cluster import KMeans
import scipy.misc
import PIL
from PIL import Image, ImageFont, ImageDraw

import numpy as np

from multiprocessing import Pool
import time
import random
import warnings

from defs import *

def multi_threaded_prime_generator(resized_image, kmeans, filename, threads=4, log_process=True):
    image_generator = (create_numbered_image(resized_image, kmeans) for _ in range(1000000))
    start = time.time() 
    with Pool(threads) as pool:
        results = pool.imap_unordered(is_good_prime_portrait, image_generator)
        total_results = 0
        
        for result in results:
            total_results += 1
            
            # Possibly log time spend searching this prime number
            if log_process and total_results%10==0:
                elapsed = time.time()
                elapsed = elapsed - start
                print("Seconds spent in (function name) is {} time per result: {}".format(str(elapsed), str(elapsed/total_results)))

                
            if result != None: 
                # Found a prime number, print it and save it!
                integer, string, n_image = result
                print_result(string, n_image)
                normal_image = numbered_image_to_normal_image(n_image, kmeans)
                plt.imshow(normal_image)
                plt.show()
                show_and_save_image(normal_image, n_image, result_filename(filename))
                break
                
                
def search_prime_portrait(filename, resize_factor=16, log_process=True, threads=4):
    resized_image = load_and_resize_image(filename, resize_factor=resize_factor)
    print("Working with size " + str(resized_image.shape))
    kmeans = get_k_means(resized_image)
    multi_threaded_prime_generator(resized_image, kmeans, filename, log_process=log_process, threads=threads)

if __name__ == "__main__":
    search_prime_portrait('cropped.jpg', resize_factor=32, log_process=True, threads=4)

