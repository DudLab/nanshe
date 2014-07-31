__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Jul 30, 2014 19:35:11 EDT$"


import numpy

import nanshe.expanded_numpy

import nanshe.advanced_image_processing


class TestAdvancedImageProcessing(object):
    def test_remove_zeroed_lines_1(self):
        a = numpy.ones((1, 100, 100))
        p = 0.2
        erosion_shape = [ 21, 1 ]
        dilation_shape = [ 1, 3 ]

        r = numpy.array([[0, 0, 0], [a.shape[1]-2, 3, 4]]).T.copy()

        print(r)

        ar = a.copy()
        for each_r in r:
            nanshe.expanded_numpy.index_axis_at_pos(nanshe.expanded_numpy.index_axis_at_pos(ar, 0, each_r[0]), -1, each_r[-1])[:] = 0

        b = nanshe.advanced_image_processing.remove_zeroed_lines(ar, erosion_shape=erosion_shape, dilation_shape=dilation_shape)

        assert((a == b).all())

    def test_remove_zeroed_lines_2(self):
        a = numpy.ones((1, 100, 100))
        p = 0.2
        erosion_shape = [ 21, 1 ]
        dilation_shape = [ 1, 3 ]

        r = numpy.array([[0, 0, 0], [1, 3, 4]]).T.copy()

        print(r)

        ar = a.copy()
        for each_r in r:
            nanshe.expanded_numpy.index_axis_at_pos(nanshe.expanded_numpy.index_axis_at_pos(ar, 0, each_r[0]), -1, each_r[-1])[:] = 0

        b = nanshe.advanced_image_processing.remove_zeroed_lines(ar, erosion_shape=erosion_shape, dilation_shape=dilation_shape)

        assert((a == b).all())


    def test_remove_zeroed_lines_3(self):
        a = numpy.ones((1, 100, 100))
        p = 0.2
        erosion_shape = [ 21, 1 ]
        dilation_shape = [ 1, 3 ]

        nr = numpy.random.geometric(p)

        r = numpy.array([numpy.repeat(0, nr), numpy.random.random_integers(1, a.shape[1] - 2, nr)]).T.copy()

        print(r)

        ar = a.copy()
        for each_r in r:
            nanshe.expanded_numpy.index_axis_at_pos(nanshe.expanded_numpy.index_axis_at_pos(ar, 0, each_r[0]), -1, each_r[-1])[:] = 0

        b = nanshe.advanced_image_processing.remove_zeroed_lines(ar, erosion_shape=erosion_shape, dilation_shape=dilation_shape)

        assert((a == b).all())