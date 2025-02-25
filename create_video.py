from tqdm import tqdm
import os
import sys
import shutil

input_dir = "outputs-processed"
# get all png files in the input_dir directory
png_files = [f for f in os.listdir(input_dir) if f.endswith(".png")]
if not png_files:
    print("No png files found in the current directory.")
    sys.exit()

# copy the png files to the output_video directory and rename them to frame_0000.png, frame_0001.png, etc.
output_dir = "output_video"
os.makedirs(output_dir, exist_ok=True)
for i, f in enumerate(tqdm(png_files, desc="Copying files")):
    output_file = os.path.join(output_dir, f"frame_{i:04d}.png")
    if not os.path.exists(output_file):
        shutil.copy(os.path.join(input_dir, f), output_file)

frame_rate = 20

print(
    f"The video will be {(len(png_files) / frame_rate) // 60} minutes and {(len(png_files) / frame_rate) % 60 } seconds long."
)

continue_a = input("Do you want to continue? [y/n] ")
if continue_a.lower() != "y":
    sys.exit()

# create the video from the png files with ffmpeg
os.system(
    f"ffmpeg -r {frame_rate}  -i {output_dir}/frame_%04d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p output.mp4"
)
print("Video created successfully!")
