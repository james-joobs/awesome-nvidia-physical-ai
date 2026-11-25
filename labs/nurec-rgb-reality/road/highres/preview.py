"""Preview a rebuilt bridge package in the site's existing Reality View on localhost."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE = "/awesome-nvidia-physical-ai/"
BRIDGE = BASE + "showcase/reality-kitscenes/road/"
LAB = BASE + "labs/nurec-rgb-reality/"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True, help="Rebuilt browser/road folder")
    parser.add_argument("--site", type=Path, default=Path("site/dist"))
    parser.add_argument("--port", type=int, default=8128)
    args = parser.parse_args()
    site, package = args.site.resolve(), args.package.resolve()
    lab = LAB.removeprefix(BASE)
    if not (site/lab/"index.html").is_file():
        parser.error("Build the site first: npm --prefix site run build")
    for item in ("road.json", "surround.json", "tracks.json", "scene.spz"):
        if not (package/item).is_file():
            parser.error(f"Local package is missing {item}")

    class PreviewHandler(SimpleHTTPRequestHandler):
        def translate_path(self, path):
            url_path = unquote(urlsplit(path).path)
            if url_path.startswith(BRIDGE):
                root, prefix = package, BRIDGE
            elif url_path.startswith(BASE):
                root, prefix = site, BASE
            else:
                return str(site/"__missing_preview_path__")
            target = (root/url_path[len(prefix):]).resolve()
            return str(target if target.is_relative_to(root) else root/"__missing_preview_path__")

    with ThreadingHTTPServer(("127.0.0.1", args.port), PreviewHandler) as server:
        for locale in ("", "ko/"):
            print(f"http://127.0.0.1:{server.server_port}{BASE}{locale}{lab}#frankfurt-3d", flush=True)
        print("Select Downtown bridge / 도심 교량 to see your package.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
