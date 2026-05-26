#include <iostream>
#include "kernel.hpp"

#define CUDA_CHECK(call) do {                                              \
    cudaError_t err = (call);                                              \
    if (err != cudaSuccess) {                                              \
        std::cerr << "CUDA error at " << __FILE__ << ":" << __LINE__       \
                  << " — " << cudaGetErrorString(err) << std::endl;        \
        std::exit(1);                                                      \
    }                                                                      \
} while (0)

extern int global_block_x, global_block_y;

__host__ __device__ int checkPointForJuliaSet(int x, int y, Complex c, float scale, int res_x, int res_y, int max_iter, float max_mag, float x_scale, float y_scale){
    float scaledX = scale * x_scale * (float) (x - res_x / 2) / (res_x / 2);
    float scaledY = scale * y_scale * (float) (y - res_y / 2) / (res_y / 2);

    Complex z(scaledX, scaledY);

    int i = 0;
    for(i = 0; i < max_iter; i++) {
        z = z * z + c;
        if(z.magnitude2() > max_mag)
            break;
    }
    return i; 
 }


__global__ void julia_kernel_device(float *julia_set, Complex c, float scale, int res_x, int res_y, int max_iter, float max_mag, float x_scale, float y_scale) {
  int x = blockIdx.x * blockDim.x + threadIdx.x;
  int y = blockIdx.y * blockDim.y + threadIdx.y;

  if (x >= res_x || y >= res_y) return; // safety guard
  float juliaShade = ((float) checkPointForJuliaSet(x, y, c, scale, res_x, res_y, max_iter, max_mag, x_scale, y_scale)) / max_iter;
  julia_set[x*res_y + y] = juliaShade;
}


void julia_kernel(float *julia_set, Complex c, float scale, int res_x, int res_y, int max_iter, float max_mag, float x_scale, float y_scale) {
  // compute a good default block size
  int bx = (global_block_x > 0) ? global_block_x : 16;
  int by = (global_block_y > 0) ? global_block_y : 16;
  dim3 block(bx, by);
  dim3 grid((res_x + bx - 1) / bx, (res_y + by - 1) / by);

  // allocate device buffer
  float *d_julia_set;
  size_t bytes = (size_t) res_x * res_y * sizeof(float);
  cudaMalloc(&d_julia_set, bytes);
  
  // launch
  CUDA_CHECK(cudaMalloc(&d_julia_set, bytes));
  julia_kernel_device<<<grid, block>>>(d_julia_set, c, scale, res_x, res_y, max_iter, max_mag, x_scale, y_scale);
  CUDA_CHECK(cudaGetLastError());            // catches kernel launch config errors
CUDA_CHECK(cudaMemcpy(julia_set, d_julia_set, bytes, cudaMemcpyDeviceToHost));
CUDA_CHECK(cudaFree(d_julia_set));
  // copy back, synchronize
  cudaMemcpy(julia_set, d_julia_set, bytes, cudaMemcpyDeviceToHost);

  // free
  cudaFree(d_julia_set);
}
















