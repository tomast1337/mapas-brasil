import os
from bs4 import BeautifulSoup
from tqdm import tqdm
import subprocess
import random

random.seed(42)


def clean_svg_file(filepath: str):
    """
    Clean a single SVG file using svgo.
    """
    try:
        # Run svgo to clean the SVG file
        subprocess.run(["svgo", filepath], check=True)
        print(f"Cleaned: {filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clean {filepath}: {e}")
    except FileNotFoundError:
        print("svgo is not installed. Please install it using 'npm install -g svgo'.")


input_dir = "outputs"
if not os.path.exists(input_dir):
    exit("Output directory does not exist")

svg_files = [f for f in os.listdir(input_dir) if f.endswith(".svg")]
# sort randomly
random.shuffle(svg_files)

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
    output_file = f"{output_dir}/{name}.svg"
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

    # remove all use tags
    for use in svg.find_all("use"):
        use.decompose()

    # flat all groups
    for g in svg.find_all("g"):
        g.unwrap()

    # get blue color from the SVG
    water = svg.find_all("path", fill="#3333FF")
    # move to the bottom of the SVG
    for w in water:
        w.extract()
        svg.insert(0, w)

    # find path with style="fill:none;stroke:#000"
    streets = svg.find_all("path", style="fill:none;stroke:#000")
    # move to the top of the SVG
    for s in streets:
        s.extract()
        svg.append(s)

    # Add City and State text to the SVG file in centered position
    text = soup.new_tag("text")
    text["x"] = "50%"
    text["y"] = "50%"
    text["text-anchor"] = "middle"
    text["font-size"] = "32"
    text["fill"] = "black"
    text["font-family"] = "Arial, sans-serif"
    text["font-weight"] = "bold"
    text["outline"] = "#FFFFFF"
    text["stroke"] = "#FFFFFF"
    text["stroke-width"] = "2"  # Increased stroke width for thicker outline
    text["fill"] = "#000000"
    text.append(f"{city}, {state}")
    svg.append(text)

    # get string representation of the SVG
    data = str(svg)
    # replace table lookups with actual colors
    feature_colors = {
        "#3333FF": "#4A80F5",
        "#F4A460": "#EDE2A5",
        "#32CD32": "#32cd32",
        "#006400": "#2db92d",
        "#008000": "#28a428",
        "#90EE90": "#239023",
        "#9ACD32": "#1e7b1e",
        "#D3D3D3": "#C3C2C0",
        "#A9A9A9": "#ABAAA8",
        "#696969": "#7A7A78",
        "#000": "#313130",
    }
    for old_color, new_color in feature_colors.items():
        data = data.replace(old_color, new_color)

    # Save the SVG file
    with open(output_file, "w") as f:
        f.write(data)

    # Clean the SVG file
    clean_svg_file(output_file)

    print(f"Processed {city}, {state}, saved to {output_file}")
    return


def main():
    for svg_file in tqdm(svg_files):
        process_svg(svg_file)


if __name__ == "__main__":
    main()
