import numpy as np
from numba import njit
from numba.cuda import jit as cjit
import inspect
from numba import cuda


def make_copy(dtype=np.float64, shape=(3, 3), mode="python"):
    nr, nc = shape

    def my_dumb_copy(A, B):
        """
        a function that copies A
        """
        if mode == "cuda":
            C = cuda.local.array(shape, dtype=dtype)
        elif mode == "python":
            C = np.empty(shape, dtype=dtype)
        for r in range(nr):
            for c in range(nc):
                C[r, c] = A[r, c]
        for r in range(nr):
            for c in range(nc):
                B[r, c] = C[r, c]

    return my_dumb_copy


def make_kernel(ccopy, size=(3, 3), dtype="f8", mode="cuda"):
    nr, nc = size

    @cjit
    def kernel(Ad, Bd):
        tx = cuda.threadIdx.x
        ty = cuda.blockIdx.x

        block_size = cuda.blockDim.x
        grid_size = cuda.gridDim.x

        start = tx + ty * block_size
        stride = block_size * grid_size

        float_type = np.float64
        for calc in range(start, 1, stride):
            if mode == "cuda":
                A = cuda.local.array(size, dtype=dtype)
                B = cuda.local.array(size, dtype=dtype)
            elif mode == "python":
                A = np.empty(size, dtype=dtype)
                B = np.empty(size, dtype=dtype)

            for r in range(nr):
                for c in range(nc):
                    A[r, c] = Ad[r, c]
            ccopy(A, B)
            for r in range(3):
                for c in range(3):
                    Bd[r, c] = B[r, c]

    return kernel


ccopy = cjit(make_copy(mode="cuda"), device=True)
pcopy = make_copy(mode="python")
ncopy = njit(make_copy(mode="python"))

A = np.arange(9).reshape(3, 3).astype(dtype=np.float64)
A = np.ascontiguousarray(A)
B = np.zeros_like(A)


def test_python():
    pcopy(A, B)
    assert np.all(A - B == 0)


def test_numba_jit():
    ncopy(A, B)
    assert np.all(A - B == 0)


def test_numba_cuda():
    threads_per_block = 256
    blocks_per_grid = 512
    cuda.synchronize()
    Ad = cuda.to_device(A)
    Bd = cuda.to_device(np.zeros((3, 3)))
    kernel = make_kernel(ccopy)
    kernel[blocks_per_grid, threads_per_block](Ad, Bd)
    cuda.synchronize()
    B = Bd.copy_to_host()
    assert np.all(A - B == 0)


if __name__ == "__main__":
    print("PURE PYTHON")
    pcopy(A, B)
    print(A - B)

    print("NJIT")
    ncopy(A, B)
    print(A - B)

    print("CUDA")
    kernel = make_kernel(ccopy)

    threads_per_block = 256
    blocks_per_grid = 512

    cuda.synchronize()
    Ad = cuda.to_device(A)
    Bd = cuda.to_device(np.zeros((3, 3)))
    kernel[blocks_per_grid, threads_per_block](Ad, Bd)
    cuda.synchronize()
    B = Bd.copy_to_host()
    print(A - B)
