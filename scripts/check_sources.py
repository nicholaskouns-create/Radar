"""Inspect authoritative public dataset sources without silently downloading huge archives."""
import argparse
import json
import urllib.request

SOURCES = {
    "radial": "https://github.com/valeoai/RADIal",
    "gao_raw_adc": "https://github.com/Xiangyu-Gao/Raw_ADC_radar_dataset_for_automotive_object_detection",
    "cruw": "https://www.cruwdataset.org/download",
    "carrada": "https://arthurouaknine.github.io/codeanddata/carrada",
    "radr": "https://huggingface.co/datasets/gtaxcenter/radr",
}

def main():
    parser = argparse.ArgumentParser(description="Source reachability check; NOT an ADC download")
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()
    records = []
    for name, url in SOURCES.items():
        row = {"dataset": name, "url": url, "acquired": False}
        try:
            request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Radar-research/1.0"})
            with urllib.request.urlopen(request, timeout=args.timeout) as response:
                row["http_status"] = response.status
                row["reachable"] = response.status < 400
        except Exception as exc:
            row["reachable"] = False
            row["error_type"] = type(exc).__name__
        records.append(row)
    print(json.dumps(records, indent=2))

if __name__ == "__main__":
    main()
