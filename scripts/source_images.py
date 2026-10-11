"""Download Wikimedia Commons thumbnails and record their attribution.

Run only for missing IDs. Search terms are editorial prompts, not provider claims.
Review the generated contact sheet before publishing.
"""

from html import unescape
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw
import json
import re
import time
import urllib.parse
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/data/experiences"
ASSETS = ROOT / "src/assets/experiences"
MANIFEST = ROOT / "src/data/image-credits.json"
CONTACT = ROOT / "image-contact-sheet.jpg"
UA = "TheSparkQuest/0.1 (personal experience catalogue; contact via Wikimedia Commons)"

# Venue or subject first, then place. The results are illustrative unless the
# Commons description identifies the exact venue or event.
QUERIES = """
001|Fairbanks Alaska aurora borealis
002|Denali flightseeing Alaska winter
004|Alaska dog sled huskies snow
005|Chena Hot Springs Alaska winter
006|World Ice Art Championships Fairbanks
007|musk ox farm Palmer Alaska
008|Alaska Wildlife Conservation Center Portage
009|Fur Rondy Anchorage festival
010|Alaska ice fishing cabin
011|Lamar Valley Yellowstone wolves winter
012|Old Faithful Snow Lodge Yellowstone winter
013|National Elk Refuge sleigh Jackson
014|Lone Mountain Ranch sleigh Montana
015|Breckenridge snow sculpture championships
016|Steamboat Springs Winter Carnival
017|Durango Silverton train Cascade Canyon snow
018|California Zephyr Glenwood Canyon train
019|LIGO Livingston Louisiana observatory
020|Bellagio O Las Vegas theater
022|Bosque del Apache cranes sunrise
023|Aransas whooping cranes Texas
024|Maui humpback whales boat
025|Atlantis submarine Waikiki Hawaii
026|giraffes Fredericksburg Texas Longneck Manor
027|Shark Valley Everglades tram
028|Okefenokee Swamp boat Georgia
029|Turtle Hospital Marathon Florida sea turtles
030|Cumberland Island wild horses Georgia
031|Mosquito Bay Vieques bioluminescence
032|Kilauea Hawaii Volcanoes National Park
033|Na Pali Coast Kauai aerial
034|Grand Canyon South Rim winter sunrise
035|Bryce Canyon snow hoodoos
036|White Sands National Park sunset
037|Carlsbad Caverns Big Room
038|Monument Valley Navajo guide
039|Meteor Crater Arizona
040|Alinea Chicago restaurant
041|New Orleans Mardi Gras parade
042|Courir de Mardi Gras Eunice Louisiana
043|Heard Museum hoop dance Phoenix
044|Sundance Film Festival Boulder Colorado
045|Tucson gem and mineral show
046|Saranac Lake Winter Carnival ice palace
047|Daytona International Speedway race car
048|Fort Worth Stock Show rodeo
049|Gasparilla Pirate Fest Tampa
050|Fiestas de la Calle San Sebastian Puerto Rico
052|New Orleans second line parade brass band
053|Belasco Theatre Broadway New York
054|Grand Ole Opry Nashville stage
055|Sun Studio Memphis recording
056|Ground Zero Blues Club Clarksdale
057|Muscle Shoals Sound Studio Alabama
058|Metropolitan Opera New York auditorium
059|New York City Ballet Lincoln Center
060|Freds Lounge Mamou Louisiana music
061|John C Campbell Folk School Brasstown
062|Corning Museum of Glass glassblowing
063|perfume making New Orleans
064|Hatch Show Print Nashville posters
065|Mardi Gras World New Orleans floats
066|sweetgrass basket weaving Charleston
068|Hawaiian flower lei making Maui
069|Georgia Aquarium sea otters Atlanta
070|Louisiana crawfish boil
071|New Orleans School of Cooking
073|Gullah Geechee food Charleston
074|Bardstown Bourbon Company distillery
075|Buckstaff Bathhouse Hot Springs Arkansas
076|Ten Thousand Waves Santa Fe baths
077|Hawaiian cacao chocolate Kona
078|Steamboat Natchez New Orleans Mississippi
079|Inn at Little Washington Virginia restaurant
080|South Beach Wine Food Festival Miami
081|Kennedy Space Center astronaut Florida
082|Cape Canaveral rocket launch
083|McDonald Observatory Texas night sky
084|Very Large Array radio telescopes New Mexico
085|Phantom of the Opera Broadway mask theater
086|Meow Wolf Santa Fe House Eternal Return
087|Dinosaur National Monument fossil quarry
088|Biosphere 2 Arizona interior
089|Sphere Las Vegas exterior
090|Musical Instrument Museum Phoenix
091|New York Botanical Garden orchids
092|Longwood Gardens winter conservatory
093|Weeki Wachee mermaids Florida
094|National Aviary Pittsburgh sloth
095|Florida Aquarium African penguins Tampa
096|Taliesin West Scottsdale Arizona
097|Library of Congress interior Washington
098|National Comedy Center Jamestown New York
099|International Spy Museum Washington DC
100|Equal Justice Initiative Legacy Museum Montgomery
102|Niagara Falls winter ice
110|Key West Literary Seminar Florida
"""
SEARCHES = dict(line.split("|", 1) for line in QUERIES.strip().splitlines())
BAD = re.compile(r"\b(logo|map|diagram|poster|icon|flag|banner|seal|coat of arms|screenshot|svg)\b", re.I)
FALLBACK = {
    '002': 'Denali Alaska aircraft', '010': 'ice fishing Alaska',
    '011': 'Yellowstone wolf snow', '014': 'sleigh ride Montana',
    '017': 'Durango Silverton railroad train', '019': 'LIGO Livingston Louisiana',
    '020': 'Cirque du Soleil O Bellagio',
}


def read_url(url, attempts=5):
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read(), response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                time.sleep(12 * (attempt + 1))
            else:
                time.sleep(2 * (attempt + 1))
            if attempt == attempts - 1:
                raise
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(2 * (attempt + 1))


def clean_html(value):
    return unescape(re.sub("<[^>]+>", "", value or "")).strip()


def candidates_for(query):
    params = {
        "action": "query", "generator": "search", "gsrsearch": "filetype:bitmap " + query,
        "gsrnamespace": 6, "gsrlimit": 8, "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": 960, "format": "json", "formatversion": 2,
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    payload, _ = read_url(url)
    pages = json.loads(payload).get("query", {}).get("pages", [])
    candidates = []
    for rank, page in enumerate(pages):
        infos = page.get("imageinfo", [])
        if not infos or BAD.search(page["title"]):
            continue
        info = infos[0]
        metadata = info.get("extmetadata", {})
        license_name = clean_html(metadata.get("LicenseShortName", {}).get("value"))
        allowed = license_name in {"Public domain", "CC0"} or license_name.startswith("CC BY ") or license_name.startswith("CC BY-SA ")
        if not allowed or info.get("width", 0) < 650 or info.get("height", 0) < 350:
            continue
        thumb = info.get("thumburl")
        if not thumb or not info.get("mime", "").startswith("image/"):
            continue
        title_words = set(re.findall(r"[a-z]{4,}", query.lower()))
        name_words = set(re.findall(r"[a-z]{4,}", page["title"].lower()))
        score = len(title_words & name_words) * 4 - rank
        if info["width"] >= info["height"]:
            score += 2
        candidates.append((score, page, info, metadata, license_name))
    return candidates


def fetch_one(id, query):
    candidates = candidates_for(query)
    if not candidates:
        candidates = candidates_for(FALLBACK.get(id, " ".join(query.split()[:3])))
    if not candidates:
        raise RuntimeError("No suitable licensed image")
    candidates.sort(key=lambda item: item[0], reverse=True)
    _, page, info, metadata, license_name = candidates[0]
    data, mime = read_url(info["thumburl"])
    image = Image.open(BytesIO(data)).convert("RGB")
    if image.width < 650 or image.height < 350:
        raise RuntimeError("Downloaded thumbnail too small")
    target = ASSETS / f"{id}.jpg"
    image.save(target, "JPEG", quality=82, optimize=True, progressive=True)
    title = page["title"].removeprefix("File:").rsplit(".", 1)[0].replace("_", " ")
    return id, {
        "file": f"{id}.jpg",
        "alt": f"Photograph: {title}",
        "title": title,
        "author": clean_html(metadata.get("Artist", {}).get("value")) or "Wikimedia Commons contributor",
        "license": license_name,
        "licenseUrl": clean_html(metadata.get("LicenseUrl", {}).get("value")),
        "sourceUrl": info["descriptionurl"],
        "note": "Illustrative photo; the pictured scene may differ from the named experience.",
    }


def make_contact_sheet(credits):
    ids = sorted(credits)
    width, height = 220, 168
    sheet = Image.new("RGB", (width * 7, height * ((len(ids) + 6) // 7)), "#f7f3ea")
    draw = ImageDraw.Draw(sheet)
    for index, id in enumerate(ids):
        path = ASSETS / credits[id]["file"]
        if not path.exists():
            continue
        photo = Image.open(path)
        photo.thumbnail((width - 8, height - 37))
        x = (index % 7) * width
        y = (index // 7) * height
        sheet.paste(photo, (x + (width - photo.width) // 2, y + 2))
        draw.text((x + 5, y + height - 33), id + " " + credits[id]["title"][:28], fill="#20334a")
    sheet.save(CONTACT, quality=82)


def main():
    credits = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    tasks = {id: query for id, query in SEARCHES.items() if id not in credits}
    for id, query in tasks.items():
        try:
            key, credit = fetch_one(id, query)
            credits[key] = credit
            print(id, credit["title"], flush=True)
        except Exception as exc:
            print(id, "ERROR", exc, flush=True)
        MANIFEST.write_text(json.dumps(dict(sorted(credits.items())), indent=2) + "\n")
        time.sleep(5)
    make_contact_sheet(credits)
    print(f"Saved {len(credits)} images; contact sheet: {CONTACT}")


if __name__ == "__main__":
    main()
