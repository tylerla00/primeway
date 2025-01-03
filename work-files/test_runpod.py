import runpod

runpod.api_key = "1BWA440QUYLETAH8X614UGY6X1JJHDV58NPD1VL5"

# print(runpod.get_gpus())


pod = runpod.create_pod(
    name="gemma-finetuning", 
    image_name="xbackgroundbuild/image-test-from-library:latest", 
    gpu_type_id="NVIDIA RTX A5000",
    gpu_count=1,
    container_disk_in_gb=10,
)
print("pod", pod)