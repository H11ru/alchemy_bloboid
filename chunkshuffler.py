import sys
import PIL
from PIL import Image
import argparse
import random
import os

def parse_chunk_size(chunk_size_str):
    try:
        w, h = chunk_size_str.lower().split('x')
        return int(w), int(h)
    except Exception:
        raise argparse.ArgumentTypeError("Chunk size must be in the format WxH, e.g., 2x2")

def get_random_pixel(img):
    x = random.randint(0, img.width - 1)
    y = random.randint(0, img.height - 1)
    return img.getpixel((x, y))

def fill_extra_chunk(chunk, img, chunk_w, chunk_h, img_w, img_h, left, upper):
    for y in range(chunk_h):
        for x in range(chunk_w):
            if left + x >= img_w or upper + y >= img_h:
                chunk.putpixel((x, y), get_random_pixel(img))
    return chunk

def main():
    parser = argparse.ArgumentParser(description="Shuffle image chunks.")
    parser.add_argument('--path', required=True, help='Path to image')
    parser.add_argument('--chunk-size', required=True, type=parse_chunk_size, help='Chunk size WxH, e.g., 2x2')
    parser.add_argument('--output-path', help='Output path for shuffled image (default: <path>_shuffled_WxH.png)')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: File {args.path} does not exist.")
        sys.exit(1)

    try:
        img = Image.open(args.path)
    except Exception as e:
        print(f"Error opening image: {e}")
        sys.exit(1)

    chunk_w, chunk_h = args.chunk_size
    img_w, img_h = img.size

    n_chunks_x = (img_w + chunk_w - 1) // chunk_w
    n_chunks_y = (img_h + chunk_h - 1) // chunk_h

    perfect_fit = (img_w % chunk_w == 0) and (img_h % chunk_h == 0)
    if not perfect_fit:
        print("WARNING: Image size does not fit perfectly into chunks.")
        print(f"Image size: {img_w}x{img_h}, chunk size: {chunk_w}x{chunk_h}")
        resp = input("Fill extra space with random pixels from the image? (y/n): ").strip().lower()
        if resp != 'y':
            print("Aborting.")
            sys.exit(0)
        print("Proceeding with random fill.")

    in_path_abs = os.path.abspath(args.path)
    out_path_abs = os.path.abspath(args.output_path) if args.output_path else None
    if in_path_abs == out_path_abs:
        print("WARNING: Input and output paths are the same. This will overwrite the original image.")
        resp = input("Are you sure you want to continue? (y/n): ").strip().lower()
        if resp != 'y':
            print("Aborting.")
            sys.exit(0)
        print("Proceeding with overwrite.")

    # Extract chunks
    chunks = []
    for by in range(n_chunks_y):
        for bx in range(n_chunks_x):
            left = bx * chunk_w
            upper = by * chunk_h
            right = min(left + chunk_w, img_w)
            lower = min(upper + chunk_h, img_h)
            chunk = img.crop((left, upper, right, lower))
            # If chunk is smaller, pad with random pixels
            if chunk.size != (chunk_w, chunk_h):
                padded_chunk = Image.new(img.mode, (chunk_w, chunk_h))
                padded_chunk.paste(chunk, (0, 0))
                padded_chunk = fill_extra_chunk(padded_chunk, img, chunk_w, chunk_h, img_w, img_h, left, upper)
                chunk = padded_chunk
            chunks.append(chunk)

    # Shuffle chunks
    random.shuffle(chunks)

    # Create output image
    out_img = Image.new(img.mode, (n_chunks_x * chunk_w, n_chunks_y * chunk_h))
    idx = 0
    for by in range(n_chunks_y):
        for bx in range(n_chunks_x):
            out_img.paste(chunks[idx], (bx * chunk_w, by * chunk_h))
            idx += 1

    # Crop to original size
    out_img = out_img.crop((0, 0, img_w, img_h))
    out_path = os.path.splitext(args.path)[0] + f"_shuffled_{chunk_w}x{chunk_h}.png" if not args.output_path else args.output_path
    out_img.save(out_path)
    print(f"Shuffled image saved to {out_path}")

if __name__ == "__main__":
    main()