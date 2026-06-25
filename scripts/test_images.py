"""
Sequential image testing script.

Tests all images in a given directory against the bg-removal API endpoint.
Reports timing, success rate, and output sizes.

Usage:
    python scripts/test_images.py                          # test images/test/
    python scripts/test_images.py --dir path/to/images
    python scripts/test_images.py --url http://localhost:8000
    python scripts/test_images.py --json                   # JSON output
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def test_image(url: str, image_path: str, timeout: int = 120) -> dict:
    filename = os.path.basename(image_path)
    filesize = os.path.getsize(image_path)
    result = {
        "file": filename,
        "path": image_path,
        "size_bytes": filesize,
        "status": None,
        "error": None,
        "elapsed_ms": None,
        "output_size_bytes": None,
    }
    try:
        with open(image_path, "rb") as f:
            if HAS_REQUESTS:
                start = time.perf_counter()
                resp = requests.post(url, files={"file": (filename, f, "image/png")}, timeout=timeout)
                elapsed = (time.perf_counter() - start) * 1000
                result["status"] = resp.status_code
                result["elapsed_ms"] = round(elapsed, 2)
                if resp.status_code == 200:
                    data = resp.json()
                    b64 = data.get("image", "")
                    result["output_size_bytes"] = len(b64)
                else:
                    result["error"] = resp.text[:200]
            else:
                boundary = "----FormBoundary7MA4YWxkTrZu0gW"
                with open(image_path, "rb") as fimg:
                    file_data = fimg.read()
                body = (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                    f"Content-Type: image/png\r\n\r\n"
                ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
                req = urllib.request.Request(
                    url,
                    data=body,
                    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                    method="POST",
                )
                start = time.perf_counter()
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    elapsed = (time.perf_counter() - start) * 1000
                    result["status"] = resp.status
                    result["elapsed_ms"] = round(elapsed, 2)
                    body = resp.read().decode()
                    data = json.loads(body)
                    b64 = data.get("image", "")
                    result["output_size_bytes"] = len(b64)
    except Exception as e:
        result["error"] = str(e)[:200]
        if result["status"] is None:
            result["status"] = 0
    return result


def main():
    parser = argparse.ArgumentParser(description="Test images against bg-removal API")
    parser.add_argument("--dir", default=None, help="Directory with test images")
    parser.add_argument("--url", default="http://localhost:8000/remove-bg/", help="API endpoint URL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--timeout", type=int, default=120, help="Request timeout in seconds")
    args = parser.parse_args()

    if args.dir:
        image_dir = args.dir
    else:
        image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "test")

    if not os.path.isdir(image_dir):
        print(f"Error: directory not found: {image_dir}")
        print("Run `python scripts/generate_test_images.py` first to create test images.")
        sys.exit(1)

    extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
    images = sorted(
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if os.path.splitext(f)[1].lower() in extensions
    )

    if not images:
        print(f"No image files found in {image_dir}")
        sys.exit(1)

    results = []
    total_start = time.perf_counter()

    print(f"\n  Testing {len(images)} images against {args.url}\n")
    print(f"  {'Image':<30} {'Size':>10} {'Status':>8} {'Time (ms)':>10} {'Output':>10}")
    print(f"  {'-'*30} {'-'*10} {'-'*8} {'-'*10} {'-'*10}")

    for img_path in images:
        r = test_image(args.url, img_path, args.timeout)
        results.append(r)
        size_kb = r["size_bytes"] / 1024
        out_kb = (r["output_size_bytes"] or 0) / 1024
        elapsed = r["elapsed_ms"] if r["elapsed_ms"] is not None else 0
        status = r["status"] if r["status"] else "ERR"
        if r["error"]:
            print(f"  {r['file']:<30} {size_kb:>8.1f}K {str(status):>8} {elapsed:>10.0f}  ERROR: {r['error'][:50]}")
        else:
            print(f"  {r['file']:<30} {size_kb:>8.1f}K {str(status):>8} {elapsed:>10.0f} {out_kb:>8.1f}K")

    total_elapsed = (time.perf_counter() - total_start) * 1000
    success = [r for r in results if r["status"] == 200]
    failed = [r for r in results if r["status"] != 200]

    print(f"\n  {'='*70}")
    print(f"  Summary: {len(success)}/{len(results)} succeeded, {len(failed)} failed")
    print(f"  Total time: {total_elapsed:.0f} ms")
    if success:
        avg_time = sum(r["elapsed_ms"] for r in success) / len(success)
        print(f"  Average response time: {avg_time:.0f} ms")
    print()

    if args.json:
        print(json.dumps({"results": results, "total_ms": total_elapsed, "success": len(success), "failed": len(failed)}, indent=2))

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
