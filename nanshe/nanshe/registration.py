__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Jan 28, 2015 11:25:47 EST$"



import itertools
import warnings

import numpy

try:
    import pyfftw.interfaces.numpy_fft as fft
except Exception as e:
    warnings.warn(str(e) + ". Falling back to NumPy FFTPACK.", ImportWarning)
    import numpy.fft as fft

import additional_generators
import expanded_numpy

# Need in order to have logging information no matter what.
import debugging_tools


# Get the logger
logger = debugging_tools.logging.getLogger(__name__)



@debugging_tools.log_call(logger)
def register_mean_offsets(frames2reg, max_iters=-1, include_shift=False, block_frame_length=-1):
    """
        This algorithm registers the given image stack against its mean projection. This is done by computing
        translations needed to put each frame in alignment. Then the translation is performed and new translations are
        computed. This is repeated until no further improvement can be made.

        The code for translations can be found in find_mean_offsets.

        Notes:
            Adapted from code provided by Wenzhi Sun with speed improvements provided by Uri Dubin.

        Args:
            frames2reg(numpy.ndarray):           Image stack to register (time is the first dimension uses C-order tyx
                                                 or tzyx).
            max_iters(int):                      Number of iterations to allow before forcing termination if stable
                                                 point is not found yet. Set to -1 if no limit. (Default -1)
            include_shift(bool):                 Whether to return the shifts used, as well. (Default False)
            block_frame_length(int):             Number of frames to work with at a time.
                                                 By default all. (Default -1)

        Returns:
            (numpy.ndarray):                     an array containing the translations to apply to each frame.

        Examples:
            >>> a = numpy.zeros((5, 3, 4)); a[:,0] = 1; a[2,0] = 0; a[2,2] = 1; a
            array([[[ 1.,  1.,  1.,  1.],
                    [ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.]],
            <BLANKLINE>
                   [[ 1.,  1.,  1.,  1.],
                    [ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.]],
            <BLANKLINE>
                   [[ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.],
                    [ 1.,  1.,  1.,  1.]],
            <BLANKLINE>
                   [[ 1.,  1.,  1.,  1.],
                    [ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.]],
            <BLANKLINE>
                   [[ 1.,  1.,  1.,  1.],
                    [ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.]]])

            >>> register_mean_offsets(a, include_shift=True)
            (masked_array(data =
             [[[1.0 1.0 1.0 1.0]
              [0.0 0.0 0.0 0.0]
              [0.0 0.0 0.0 0.0]]
            <BLANKLINE>
             [[1.0 1.0 1.0 1.0]
              [0.0 0.0 0.0 0.0]
              [0.0 0.0 0.0 0.0]]
            <BLANKLINE>
             [[-- -- -- --]
              [0.0 0.0 0.0 0.0]
              [0.0 0.0 0.0 0.0]]
            <BLANKLINE>
             [[1.0 1.0 1.0 1.0]
              [0.0 0.0 0.0 0.0]
              [0.0 0.0 0.0 0.0]]
            <BLANKLINE>
             [[1.0 1.0 1.0 1.0]
              [0.0 0.0 0.0 0.0]
              [0.0 0.0 0.0 0.0]]],
                         mask =
             [[[False False False False]
              [False False False False]
              [False False False False]]
            <BLANKLINE>
             [[False False False False]
              [False False False False]
              [False False False False]]
            <BLANKLINE>
             [[ True  True  True  True]
              [False False False False]
              [False False False False]]
            <BLANKLINE>
             [[False False False False]
              [False False False False]
              [False False False False]]
            <BLANKLINE>
             [[False False False False]
              [False False False False]
              [False False False False]]],
                   fill_value = 0.0)
            , array([[0, 0],
                   [0, 0],
                   [1, 0],
                   [0, 0],
                   [0, 0]]))
    """

    if block_frame_length == -1:
        block_frame_length = len(frames2reg)

    space_shift = numpy.zeros((len(frames2reg), frames2reg.ndim-1), dtype=int)

    frames2reg_fft = numpy.empty(frames2reg.shape, dtype=complex)
    for i, j in additional_generators.lagged_generators_zipped(itertools.chain(xrange(0, len(frames2reg), block_frame_length), [len(frames2reg)])):
        frames2reg_fft[i:j] = fft.fftn(frames2reg[i:j], axes=range(1, frames2reg.ndim))
    template_fft = numpy.empty(frames2reg.shape[1:], dtype=complex)

    negative_wave_vector = numpy.asarray(template_fft.shape, dtype=float)
    numpy.reciprocal(negative_wave_vector, out=negative_wave_vector)
    negative_wave_vector *= 2*numpy.pi
    numpy.negative(negative_wave_vector, out=negative_wave_vector)

    template_fft_indices = expanded_numpy.cartesian_product([numpy.arange(_) for _ in template_fft.shape])

    unit_space_shift_fft = template_fft_indices * negative_wave_vector
    unit_space_shift_fft = unit_space_shift_fft.T.copy()
    unit_space_shift_fft = unit_space_shift_fft.reshape((template_fft.ndim,) + template_fft.shape)

    # Repeat shift calculation until there is no further adjustment.
    num_iters = 0
    squared_magnitude_delta_space_shift = 1.0
    while (squared_magnitude_delta_space_shift != 0.0):
        squared_magnitude_delta_space_shift = 0.0

        template_fft[:] = 0
        for i, j in additional_generators.lagged_generators_zipped(itertools.chain(xrange(0, len(frames2reg), block_frame_length), [len(frames2reg)])):
            frames2reg_shifted_fft_ij = numpy.exp(1j * numpy.tensordot(space_shift[i:j], unit_space_shift_fft, axes=[-1, 0]))
            frames2reg_shifted_fft_ij *= frames2reg_fft[i:j]
            template_fft += numpy.sum(frames2reg_shifted_fft_ij, axis=0)
        template_fft /= len(frames2reg)

        this_space_shift = numpy.empty_like(space_shift)
        for i, j in additional_generators.lagged_generators_zipped(itertools.chain(xrange(0, len(frames2reg), block_frame_length), [len(frames2reg)])):
            this_space_shift[i:j] = find_offsets(frames2reg_fft[i:j], template_fft)

        # Remove global shifts.
        this_space_shift_mean = numpy.round(
            this_space_shift.mean(axis=0)
        ).astype(int)
        for i, j in additional_generators.lagged_generators_zipped(itertools.chain(xrange(0, len(frames2reg), block_frame_length), [len(frames2reg)])):
            expanded_numpy.find_relative_offsets(
                this_space_shift[i:j],
                this_space_shift_mean,
                out=this_space_shift[i:j]
            )

        # Find the shortest roll possible (i.e. if it is going over halfway switch direction so it will go less than half).
        # Note all indices by definition were positive semi-definite and upper bounded by the shape. This change will make
        # them bound by the half shape, but with either sign.
        for i, j in additional_generators.lagged_generators_zipped(itertools.chain(xrange(0, len(frames2reg), block_frame_length), [len(frames2reg)])):
            expanded_numpy.find_shortest_wraparound(
                this_space_shift[i:j],
                frames2reg_fft.shape[1:],
                out=this_space_shift[i:j]
            )

        delta_space_shift = numpy.empty_like(space_shift)
        for i, j in additional_generators.lagged_generators_zipped(itertools.chain(xrange(0, len(frames2reg), block_frame_length), [len(frames2reg)])):
            delta_space_shift[i:j] = this_space_shift[i:j] - space_shift[i:j]
            squared_magnitude_delta_space_shift += numpy.dot(
                delta_space_shift[i:j], delta_space_shift[i:j].T
            ).sum()

        space_shift = this_space_shift

        if max_iters != -1:
            num_iters += 1
            if num_iters >= max_iters:
                break

    # Adjust the registered frames using the translations found.
    # Mask rolled values.
    reg_frames = numpy.ma.empty_like(frames2reg)
    reg_frames.mask = numpy.ma.getmaskarray(reg_frames)
    reg_frames.set_fill_value(reg_frames.dtype.type(0))
    for i, j in additional_generators.lagged_generators_zipped(itertools.chain(xrange(0, len(frames2reg), block_frame_length), [len(frames2reg)])):
        for k in xrange(i, j):
            reg_frames[k] = expanded_numpy.roll(frames2reg[k], space_shift[k], to_mask=True)

    if include_shift:
        return(reg_frames, space_shift)
    else:
        return(reg_frames)


@debugging_tools.log_call(logger)
def find_offsets(frames2reg_fft, template_fft):
    """
        Computes the convolution of the template with the frames by taking advantage of their FFTs for faster
        computation that an ordinary convolution ( O(N*lg(N)) vs O(N^2) )
        < https://ccrma.stanford.edu/~jos/ReviewFourier/FFT_Convolution_vs_Direct.html >.
        Once computed the maximum of the convolution is found to determine the best overlap of each frame with the
        template, which provides the needed offset. Some corrections are performed to make reasonable offsets.

        Notes:
            Adapted from code provided by Wenzhi Sun with speed improvements provided by Uri Dubin.

        Args:
            frames2reg(numpy.ndarray):           image stack to register (time is the first dimension uses C-order tyx
                                                 or tzyx).
            template_fft(numpy.ndarray):         what to register the image stack against (single frame using C-order
                                                 yx or zyx).

        Returns:
            (numpy.ndarray):                     an array containing the translations to apply to each frame.

        Examples:
            >>> a = numpy.zeros((5, 3, 4)); a[:,0] = 1; a[2,0] = 0; a[2,2] = 1; a
            array([[[ 1.,  1.,  1.,  1.],
                    [ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.]],
            <BLANKLINE>
                   [[ 1.,  1.,  1.,  1.],
                    [ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.]],
            <BLANKLINE>
                   [[ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.],
                    [ 1.,  1.,  1.,  1.]],
            <BLANKLINE>
                   [[ 1.,  1.,  1.,  1.],
                    [ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.]],
            <BLANKLINE>
                   [[ 1.,  1.,  1.,  1.],
                    [ 0.,  0.,  0.,  0.],
                    [ 0.,  0.,  0.,  0.]]])

            >>> af = numpy.fft.fftn(a, axes=range(1, a.ndim)); af
            array([[[ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ]],
            <BLANKLINE>
                   [[ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ]],
            <BLANKLINE>
                   [[ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [-2.+3.46410162j,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [-2.-3.46410162j,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ]],
            <BLANKLINE>
                   [[ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ]],
            <BLANKLINE>
                   [[ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ],
                    [ 4.+0.j        ,  0.+0.j        ,  0.+0.j        ,  0.+0.j        ]]])

            >>> tf = numpy.fft.fftn(a.mean(axis=0)); tf
            array([[ 4.0+0.j        ,  0.0+0.j        ,  0.0+0.j        ,  0.0+0.j        ],
                   [ 2.8+0.69282032j,  0.0+0.j        ,  0.0+0.j        ,  0.0+0.j        ],
                   [ 2.8-0.69282032j,  0.0+0.j        ,  0.0+0.j        ,  0.0+0.j        ]])

            >>> find_offsets(af, tf)
            array([[ 0,  0],
                   [ 0,  0],
                   [-2,  0],
                   [ 0,  0],
                   [ 0,  0]])
    """

    # If there is only one frame, add a singleton axis to indicate this.
    frames2reg_fft_added_singleton = (frames2reg_fft.ndim == template_fft.ndim)
    if frames2reg_fft_added_singleton:
        frames2reg_fft = frames2reg_fft[None]

    # Compute the product of the two FFTs (i.e. the convolution of the regular versions).
    frames2reg_template_conv_fft = frames2reg_fft * template_fft.conj()[None]

    # Find the FFT inverse (over all spatial dimensions) to return to the convolution.
    frames2reg_template_conv = fft.ifftn(frames2reg_template_conv_fft, axes=range(1, frames2reg_fft.ndim))

    # Find where the convolution is maximal. Will have the most things in common between the template and frames.
    frames2reg_template_conv_max, frames2reg_template_conv_max_indices = expanded_numpy.max_abs(
        frames2reg_template_conv, axis=range(1, frames2reg_fft.ndim), return_indices=True
    )

    # First index is just the frame, which will be in sequential order. We don't need this so we drop it.
    frames2reg_template_conv_max_indices = frames2reg_template_conv_max_indices[1:]

    # Convert indices into an array for easy manipulation.
    frames2reg_template_conv_max_indices = numpy.array(frames2reg_template_conv_max_indices).T.copy()

    # Shift will have to be in the opposite direction to bring everything to the center.
    numpy.negative(frames2reg_template_conv_max_indices, out=frames2reg_template_conv_max_indices)

    return(frames2reg_template_conv_max_indices)
