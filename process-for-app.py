import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

input_dir = "outputs"
if not os.path.exists(input_dir):
    exit("Output directory does not exist")

svg_files = [f for f in os.listdir(input_dir) if f.endswith(".svg")]
# sort the files by size, so that the largest files are processed first
svg_files.sort(key=lambda f: os.path.getsize(f"{input_dir}/{f}"), reverse=True)

# get only the first 10 files
svg_files = svg_files[:10]

print(f"Processing SVG {len(svg_files)} files in {input_dir} directory")


output_dir = "outputs-processed"
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)


def process_svg(svg_file):
    name = svg_file.split(".")[0]
    # Name of the city_STATE
    [city, state] = name.split("_")
    print(f"Processing {city}, {state}")
    output_file = f"{output_dir}/{name}.png"
    input_file = f"{input_dir}/{svg_file}"
    # open the SVG file
    with open(input_file, "r") as f:
        soup = BeautifulSoup(f, "xml")

    # Find the SVG tag
    svg = soup.find("svg")
    # Zoom in the SVG file by 30% and keep the aspect ratio
    svg["width"] = "130%"
    svg["height"] = "130%"
    # Remove the width and height attributes from the SVG tag
    svg.attrs.pop("width", None)
    svg.attrs.pop("height", None)

    # Add City and State text to the SVG file in centered position
    text = soup.new_tag("text")
    text["x"] = "50%"
    text["y"] = "50%"
    text["text-anchor"] = "middle"
    text["font-size"] = "24"
    text["fill"] = "black"
    text.append(f"{city}, {state}")
    svg.append(text)

    # remove all g tags that have a g with use tags
    for g in svg.find_all("g"):
        if g.find("use"):
            g.decompose()

    # remove all use tags
    for use in svg.find_all("use"):
        use.decompose()

    # push shapes that have black stroke to the front
    for shape in svg.find_all("path"):
        if shape.get("stroke") == "black":
            shape.decompose()
            svg.insert(0, shape)

    # Save the SVG file
    with open(input_file, "w") as f:
        f.write(str(svg))

    print(f"Processed {city}, {state}")


print("Done")


def main():
    # Set the pool size
    pool_size = 4

    with ThreadPoolExecutor(max_workers=pool_size) as executor:
        futures = [executor.submit(process_svg, svg_file) for svg_file in svg_files]
        for future in as_completed(futures):
            future.result()

    print("Done")
