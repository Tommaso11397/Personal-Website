from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
MAX_LONG_EDGE = 1800
JPEG_QUALITY = 84

COLLECTION_NOTES = {
    "miscellanea": "Loose studies, fragments, and images outside a single category.",
    "natura": "Natural forms, open air, and quiet encounters with the landscape.",
    "riflesso": "Reflections, surfaces, and doubled light.",
    "urban": "Street edges, buildings, and fragments of the city.",
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    return slug or "collection"


def image_files(folder: Path) -> list[Path]:
    files = [
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(files, key=lambda path: path.name.lower())


def fit_image(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    image.thumbnail((MAX_LONG_EDGE, MAX_LONG_EDGE), Image.Resampling.LANCZOS)

    if image.mode in {"RGBA", "LA"}:
        background = Image.new("RGB", image.size, "#f4f2ec")
        background.paste(image, mask=image.getchannel("A"))
        return background

    return image.convert("RGB")


def build_collection(source_folder: Path, output_root: Path) -> dict[str, object]:
    title = source_folder.name
    slug = slugify(title)
    output_folder = output_root / slug
    output_folder.mkdir(parents=True, exist_ok=True)

    images = []
    for index, source_image in enumerate(image_files(source_folder), start=1):
        output_name = f"{index:02d}.jpg"
        output_path = output_folder / output_name

        with Image.open(source_image) as image:
            fitted = fit_image(image)
            fitted.save(
                output_path,
                "JPEG",
                quality=JPEG_QUALITY,
                optimize=True,
                progressive=True,
            )

        images.append(
            {
                "src": f"photos/{slug}/{output_name}",
                "alt": f"{title} photograph {index}",
            }
        )

    return {
        "slug": slug,
        "title": title,
        "meta": f"{len(images)} photographs",
        "note": COLLECTION_NOTES.get(slug, f"Selected photographs from {title}."),
        "images": images,
    }


def write_collections_js(collections: list[dict[str, object]], destination: Path) -> None:
    payload = json.dumps(collections, ensure_ascii=False, indent=2)
    destination.write_text(f"window.NESSUNO_COLLECTIONS = {payload};\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Nessuno web photo collections.")
    parser.add_argument(
        "source",
        nargs="?",
        default=r"C:\Users\User\Dropbox\Foto\Best Pics",
        help="Folder whose direct child folders are photo collections.",
    )
    parser.add_argument(
        "--site",
        default=str(Path(__file__).resolve().parents[1]),
        help="Path to the Nessuno site folder.",
    )
    args = parser.parse_args()

    source_root = Path(args.source).expanduser().resolve()
    site_root = Path(args.site).expanduser().resolve()
    photos_root = site_root / "photos"
    collections_js = site_root / "assets" / "collections.js"

    if not source_root.exists():
        raise FileNotFoundError(f"Source folder does not exist: {source_root}")

    collection_folders = sorted(
        [path for path in source_root.iterdir() if path.is_dir()],
        key=lambda path: path.name.lower(),
    )

    if not collection_folders:
        raise ValueError(f"No collection folders found in {source_root}")

    if photos_root.exists():
        shutil.rmtree(photos_root)
    photos_root.mkdir(parents=True)

    collections = [
        build_collection(folder, photos_root)
        for folder in collection_folders
        if image_files(folder)
    ]
    write_collections_js(collections, collections_js)

    image_count = sum(len(collection["images"]) for collection in collections)
    print(f"Built {len(collections)} collections with {image_count} images.")
    print(f"Photos: {photos_root}")
    print(f"Data: {collections_js}")


if __name__ == "__main__":
    main()
