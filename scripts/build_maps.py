"""Cache approximate locations and generate lightweight static map SVGs.

The one-time geocoding run respects Nominatim's 1 request/second policy.
Runtime pages make no map or geocoding requests.
"""

from pathlib import Path
import json
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/data/experiences"
CACHE = ROOT / "src/data/map-coordinates.json"
MAPS = ROOT / "public/maps"
LAND = ROOT / "scripts/ne_110m_land.geojson"
UA = "TheSparkQuest/0.1 (static personal map artwork; contact via GitHub project page)"
OVERRIDES = {
    "003": "Anchorage, Alaska", "018": "Denver, Colorado",
    "038": "Monument Valley, Arizona", "023": "Aransas National Wildlife Refuge, Texas",
    "024": "Lahaina, Maui, Hawaii", "025": "Waikiki, Honolulu, Hawaii",
    "033": "Na Pali Coast, Kauai, Hawaii", "042": "Eunice, Louisiana",
    "046": "Yosemite National Park, California", "047": "Daytona Beach, Florida",
    "053": "Theatre District, Manhattan, New York City",
    "059": "Lincoln Center, New York City", "073": "Charleston, South Carolina",
    "080": "Miami Beach, Florida", "082": "Cape Canaveral, Florida",
    "110": "Key West, Florida",
    "011": "Yellowstone National Park, Wyoming", "026": "Fredericksburg, Texas",
    "029": "Marathon, Florida", "030": "Cumberland Island, Georgia",
    "031": "Vieques, Puerto Rico", "049": "Tampa, Florida",
    "050": "San Juan, Puerto Rico", "057": "Sheffield, Alabama",
    "060": "Mamou, Louisiana", "063": "New Orleans, Louisiana",
    "064": "Nashville, Tennessee", "068": "Maui, Hawaii",
    "070": "Kaplan, Louisiana", "077": "Kailua-Kona, Hawaii",
    "079": "Town of Washington, Rappahannock County, Virginia",
    "085": "Manhattan, New York City, New York", "088": "Oracle, Arizona",
    "095": "Tampa, Florida",
}


def read_url(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def geocode():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    records = [json.loads(path.read_text()) for path in sorted(DATA.glob("*.json"))]
    for record in records:
        id = record["id"]
        if id in cache:
            continue
        label = record["location"]["label"]
        query = OVERRIDES.get(id, label)
        params = urllib.parse.urlencode({"q": query, "format": "jsonv2", "limit": 1, "countrycodes": "us,pr"})
        try:
            result = json.loads(read_url("https://nominatim.openstreetmap.org/search?" + params))
            if not result:
                fallback = record["location"]["placeGroup"].replace("DC", "Washington, DC")
                params = urllib.parse.urlencode({"q": fallback, "format": "jsonv2", "limit": 1, "countrycodes": "us,pr"})
                time.sleep(1.3)
                result = json.loads(read_url("https://nominatim.openstreetmap.org/search?" + params))
            if not result:
                print(id, "NO RESULT", query, flush=True)
                continue
            first = result[0]
            cache[id] = {"lat": round(float(first["lat"]), 5), "lon": round(float(first["lon"]), 5), "query": query, "matched": first["display_name"], "approximate": True}
            CACHE.write_text(json.dumps(dict(sorted(cache.items())), indent=2) + "\n")
            print(id, query, "->", first["display_name"][:70], flush=True)
        except Exception as exc:
            print(id, "ERROR", exc, flush=True)
        time.sleep(1.3)
    return cache


def polygons(geometry):
    if geometry["type"] == "Polygon":
        yield from geometry["coordinates"][:1]
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            yield from polygon[:1]


def map_svg(lat, lon, land):
    # A broad local view keeps the marker geographic while making inland places
    # recognizable by nearby coastlines. It is explicitly approximate.
    span_lon = 13 if abs(lat) < 50 else 19
    span_lat = 7 if abs(lat) < 50 else 9
    west, east = lon - span_lon, lon + span_lon
    south, north = lat - span_lat, lat + span_lat
    width, height = 520, 245
    def xy(point):
        x, y = point
        return ((x - west) / (east - west) * width, (north - y) / (north - south) * height)
    shapes = []
    for feature in land["features"]:
        for ring in polygons(feature["geometry"]):
            if not ring or max(x for x, _ in ring) < west or min(x for x, _ in ring) > east or max(y for _, y in ring) < south or min(y for _, y in ring) > north:
                continue
            points = [xy(point) for point in ring]
            d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points) + " Z"
            shapes.append(f'<path d="{d}" fill="#d7dfcf" stroke="#b7c9b8" stroke-width="1.1"/>')
    grid = []
    for x in range(0, 521, 65):
        grid.append(f'<path d="M{x} 0V245" stroke="#dce6df" stroke-width=".7"/>')
    for y in range(0, 246, 49):
        grid.append(f'<path d="M0 {y}H520" stroke="#dce6df" stroke-width=".7"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 245" role="img" aria-label="Approximate location map">
<rect width="520" height="245" fill="#e8f0eb"/>
{''.join(grid)}
<g clip-path="url(#frame)">{''.join(shapes)}</g>
<defs><clipPath id="frame"><rect width="520" height="245"/></clipPath></defs>
<circle cx="260" cy="122.5" r="17" fill="#b46e56" opacity=".18"/>
<circle cx="260" cy="122.5" r="7" fill="#b46e56" stroke="white" stroke-width="3"/>
<text x="487" y="28" fill="#49636a" font-family="sans-serif" font-size="14" font-weight="700">N</text>
<path d="M493 34v20m0-20-5 7m5-7 5 7" stroke="#49636a" stroke-width="1.4" fill="none"/>
</svg>'''


def main():
    cache = geocode()
    if not LAND.exists():
        url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson"
        LAND.write_bytes(read_url(url))
    land = json.loads(LAND.read_text())
    MAPS.mkdir(exist_ok=True, parents=True)
    for id, point in cache.items():
        (MAPS / f"{id}.svg").write_text(map_svg(point["lat"], point["lon"], land))
    print("Generated", len(cache), "maps", flush=True)


if __name__ == "__main__":
    main()
