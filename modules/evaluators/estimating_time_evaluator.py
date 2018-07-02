# -*- coding: utf-8 -*-
""" Evaluate estimating time. """

import os
import time
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from modules.evaluators import chainer, pytorch


class EstimatingTimeEvaluator(object):
    """ Evaluate estimating time of pose net by chainer and pytorch.

    Args:
        Nj (int): Number of joints.
        gpu (int): GPU ID (negative value indicates CPU).
        chainer_model_file (str): Chainer model parameter file.
        pytorch_model_file (str): Pytorch model parameter file.
        filename (str): Image-pose list file.
        output (str): Output directory.
        debug (bool): Debug mode.
    """

    def __init__(self, **kwargs):
        self.output = kwargs['output']
        self.Nj = kwargs['Nj']
        try:
            os.makedirs(self.output)
        except OSError:
            pass
        self.estimator = {
            #'chainer': chainer.PoseEstimator(
            #    kwargs['Nj'], kwargs['gpu'], kwargs['chainer_model_file'], kwargs['filename']),
            'pytorch': pytorch.PoseEstimator(
                kwargs['Nj'], kwargs['gpu'], kwargs['pytorch_model_file'], kwargs['filename'])}
        self.debug = kwargs['debug']

    def plot(self, samples, title):
        """ Plot estimating time of chainer and pytorch. """
        time_mean = []
        time_std = []
        for estimator in tqdm(self.estimator.values(), desc='testers'):
            random_index = np.random.randint(0, estimator.get_dataset_size(), samples)
            dataset_size = estimator.get_dataset_size()
            compute_time = []
            # get compute time.
            #for index in tqdm(random_index, desc='samples'):
            for index in tqdm(range(dataset_size), desc='samples'):
                start = time.time()
                image, pose, testPose = estimator.estimate(index)
                pose = pose.view(-1, self.Nj, 2)
                _, size, _ = image.shape

                testdat = testPose.cpu().numpy()
                testdat *= size
                testdat_x, testdat_y = zip(*testdat)

                dat = pose.data[0].cpu().numpy()
                dat *= size
                dat_x, dat_y = zip(*dat)

                # pose *= size
                # pose_x, pose_y = zip(*pose)
                # plot image and pose.
                fig = plt.figure(figsize=(2.56, 2.56))
                #print(pose.data[0])
                #print(pose.data[0][:, 0])
                #print(pose.data[0][:, 1])
                img = image.numpy().transpose(1, 2, 0)
                plt.imshow(img, vmin=0., vmax=1.)
                for i in range(14):   
                    #plt.scatter(testdat_x[i], testdat_y[i], color=cm.hsv(i/14.0), s=7)
                    plt.scatter(dat_x[i], dat_y[i], color=cm.hsv(i/14.0),  s=5)
                plt.axis("off")
                plt.savefig(os.path.join(self.output, '{}.png'.format(index)))
                plt.close(fig)

                compute_time.append(time.time() - start)
            # calculate mean and std.
            time_mean.append(np.mean(compute_time))
            time_std.append(np.std(compute_time))
        # plot estimating time.
        plt.bar(range(len(time_mean)), time_mean, yerr=time_std,
                width=0.3, align='center', ecolor='black', tick_label=self.estimator.keys())
        # plot settings.
        plt.title(title)
        plt.ylabel('estimating time [sec]')
        # save plot.
        if self.debug:
            plt.show()
        else:
            filename = '_'.join(title.split(' ')) + '.png'
            plt.savefig(os.path.join(self.output, filename))
