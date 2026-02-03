import torch

def torch_gpu_status():
    if not torch.cuda.is_available():
        return False, "CUDA not available"

    return True, {
        "device_count": torch.cuda.device_count(),
        "device_index": torch.cuda.current_device(),
        "device_name": torch.cuda.get_device_name(0),
        "capability": torch.cuda.get_device_capability(0),
        "cuda_version": torch.version.cuda,
        "torch_version": torch.__version__,
    }

ok, info = torch_gpu_status()
print(ok, info)