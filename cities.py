import os
import subprocess
import matplotlib
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from shapely.geometry import shape
from shapely.ops import transform
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import numpy as np
import time
import datetime

random.seed(42)
np.random.seed(42)

# Set Matplotlib to use a non-interactive backend
matplotlib.use("Agg")


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


def simplify_geometry(geometry, tolerance=0.000001):
    """
    Simplify geometry using the Douglas-Peucker algorithm.
    """
    return geometry.simplify(tolerance, preserve_topology=True)


def process_city(row, output_dir):
    """
    Process a single city: fetch data, plot, and save as SVG.
    """
    uf = row["uf"]
    municipio = row["municipio"]
    longitude = float(row["longitude"])
    latitude = float(row["latitude"])

    dist = 5000  # Radius in meters
    filename = f"{municipio}_{uf}.svg"
    filepath = os.path.join(output_dir, filename)
    print(
        f"Processing {municipio} ({uf}) Timestamp: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
    )
    if os.path.exists(filepath):
        print(f"Already processed: {filepath}")
        return

    try:
        graph = fetch_osm_graph(latitude, longitude, dist)
        data = fetch_osm_features(latitude, longitude, dist, municipio, uf)
        save_plot(graph, data, filepath)
        clean_svg_file(filepath)
        print(
            f"Saved, cleaned, and titled: {filepath} Timestamp: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
        )
    except Exception as e:
        print(f"Failed to process {municipio} ({uf}): {e}")


def fetch_osm_graph(latitude, longitude, dist):
    """Fetch OSM road network graph."""
    return ox.graph_from_point(
        (latitude, longitude), dist=dist, network_type="all", simplify=True
    ).to_undirected()


def fetch_osm_features(latitude, longitude, dist, municipio, uf):
    """Fetch additional OSM features like water, parks, and buildings."""
    try:
        data = ox.features.features_from_point(
            (latitude, longitude),
            tags={
                "natural": ["water", "wood", "grassland", "tree", "beach"],
                "leisure": ["park", "garden", "pitch", "sports_centre"],
                "landuse": [
                    "forest",
                    "meadow",
                    "recreation_ground",
                    "residential",
                    "commercial",
                ],
                "building": True,
            },
            dist=dist,
        )
        data["geometry"] = data["geometry"].apply(simplify_geometry)
        return data
    except Exception as e:
        print(f"Failed to fetch additional data for {municipio} ({uf}): {e}")
        return None


def save_plot(graph, data, filepath):
    """Generate and save the SVG plot."""
    fig, ax = plt.subplots(figsize=(10, 10))
    ox.plot_graph(
        graph,
        ax=ax,
        show=False,
        close=False,
        node_size=0,
        bgcolor="none",
        edge_color="black",
        figsize=(10, 10),
        dpi=300,
    )

    feature_colors = {
        "water": "blue",
        "wood": "darkgreen",
        "grassland": "lightgreen",
        "tree": "green",
        "beach": "sandybrown",
        "park": "green",
        "garden": "limegreen",
        "pitch": "lightgreen",
        "sports_centre": "darkgreen",
        "forest": "darkgreen",
        "meadow": "lightgreen",
        "recreation_ground": "yellowgreen",
        "residential": "lightgray",
        "commercial": "gray",
        "building": "darkgray",
    }

    if data is not None:
        for feature_type, color in feature_colors.items():
            try:
                if "natural" in data.columns and feature_type in data["natural"].values:
                    data[data["natural"] == feature_type].plot(
                        ax=ax, color=color, alpha=0.8, label=feature_type
                    )
                if "leisure" in data.columns and feature_type in data["leisure"].values:
                    data[data["leisure"] == feature_type].plot(
                        ax=ax, color=color, alpha=0.8, label=feature_type
                    )
                if "landuse" in data.columns and feature_type in data["landuse"].values:
                    data[data["landuse"] == feature_type].plot(
                        ax=ax, color=color, alpha=0.8, label=feature_type
                    )
                if "building" in data.columns and feature_type == "building":
                    data[data["building"].notnull()].plot(
                        ax=ax, color=color, alpha=0.8, label=feature_type
                    )
            except KeyError:
                continue

    ax.set_aspect(1)
    plt.savefig(filepath, format="svg", pad_inches=0)
    plt.close()


def main():
    # Create an outputs directory if it doesn't exist
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Load city data from CSV
    cities_df = pd.read_csv("cities.csv", delimiter=";", encoding="utf-8")

    # Process cities sequentially
    for _, row in tqdm(
        cities_df.iterrows(), total=len(cities_df), desc="Processing Cities"
    ):
        process_city(row, output_dir)

    print("Done!")


if __name__ == "__main__":
    main()
