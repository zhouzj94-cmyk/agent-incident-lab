import argparse
import zipfile
import urllib.request
from pathlib import Path


def download_file(url: str, output_path: Path) -> None:
    print(f"Downloading from {url}...")
    urllib.request.urlretrieve(url, output_path)
    print(f"Downloaded to {output_path}")


def extract_zip(zip_path: Path, extract_to: Path) -> None:
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted to {extract_to}")


def main():
    parser = argparse.ArgumentParser(description="Download LogHub datasets")
    parser.add_argument("--dataset", default="BGL", choices=["BGL", "HDFS"], help="Dataset to download")
    parser.add_argument("--output", default="data/raw", help="Output directory")

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dataset == "BGL":
        print("BGL dataset must be downloaded manually from LogHub:")
        print("https://github.com/logpai/loghub")
        print("\nSteps:")
        print("1. Visit https://github.com/logpai/loghub")
        print("2. Follow instructions to download BGL dataset")
        print(f"3. Place BGL.log in {output_dir}/BGL/BGL.log")
        print("\nNote: LogHub datasets require agreeing to their license terms.")

    elif args.dataset == "HDFS":
        print("HDFS dataset must be downloaded manually from LogHub:")
        print("https://github.com/logpai/loghub")
        print("\nSteps:")
        print("1. Visit https://github.com/logpai/loghub")
        print("2. Follow instructions to download HDFS dataset")
        print(f"3. Place HDFS.log in {output_dir}/HDFS/HDFS.log")


if __name__ == "__main__":
    main()
