"""Keep PDF wording for audit while preparing calm visitor-facing notes."""

from pathlib import Path
import json
import re

DATA = Path(__file__).resolve().parents[1] / "src/data/experiences"

NOTES = {
    '002': 'Winter flightseeing is weather dependent. The earlier research listed flights around one hour and fares from $325; confirm current prices, boarding and weight policies with the operator.',
    '004': 'The sled ride can be bumpy. Ask the operator about boarding, weight limits and how the ride feels before reserving.',
    '006': 'Earlier research listed the 2027 competition beginning February 15, with judging into March. Confirm the current program and prepare for cold outdoor walking.',
    '009': 'Earlier research listed February 25 to March 7, 2027. Confirm the program, and choose a seated or shorter event if that suits you.',
    '010': 'Winter outings are commonly offered from November into early April. The catch and any aurora sighting will depend on conditions.',
    '011': 'Viewing happens mainly from a vehicle, with optional cold outdoor stops. Wildlife sightings are always unpredictable.',
    '012': 'Earlier research listed a December 16, 2026 to March 7, 2027 lodge season. Confirm the current season, snowcoach transfers and conditions on paths.',
    '013': 'Earlier research listed a season from December 19 to April 3, subject to conditions. Ask about boarding, bumps and the cold before reserving.',
    '014': 'Ask about the winter schedule, sleigh boarding, bumps and cabin access before reserving.',
    '015': 'Earlier research listed January 23 to February 2, 2027. Confirm dates and prepare for altitude, cold and possibly icy footing.',
    '016': 'Earlier research listed February 2 to 7, 2027. Check the current program and choose a comfortable viewing spot.',
    '019': 'Earlier research listed Science Saturdays on January 2 and February 6, 2027. The tour was free and about 90 minutes, with accessible facilities; confirm dates, route and tour areas.',
    '020': 'This is a seated theater performance and needs no swimming. Confirm the current schedule; the earlier research listed Wednesday to Sunday shows and February 14, 2027 as a dark date.',
    '021': 'Winter gatherings vary with the weather. Confirm current viewing access and shuttle arrangements. The idea is to watch from land, without swimming.',
    '023': 'Ask about boat boarding and sea conditions. Wild whooping crane sightings cannot be promised.',
    '024': 'January and February are often good months for whale watching. Confirm boat access and sea conditions; whale behavior varies, and no swimming is needed.',
    '025': 'The earlier research described about 45 minutes underwater within a 1 hour 45 minute outing, and a fare around $168 per adult. Confirm current details and whether boat transfers and ladders are manageable.',
    '026': 'The earlier research listed a two-night minimum and a Giraffe Suite rate around $1,600 per night. The suite requires stairs; ask about villa access and which encounters are included.',
    '030': 'The earlier research listed a premium nightly rate that included meals, ferry and guided outings, plus a January 18 to 22, 2027 photo trip. Confirm current prices and availability; roads can be bumpy and the inn has stairs.',
    '031': 'Choose a boat outing if you prefer to stay out of the water. A moonless night can make the glow easier to see; confirm boat operation, boarding and life jackets.',
    '032': 'An eruption is never promised. Check current park alerts, air quality, viewpoint access and visibility before visiting.',
    '040': 'Reservations may open about two months ahead; confirm the current booking window, format and any dietary needs.',
    '041': 'Mardi Gras falls on February 9, 2027. Check individual parade schedules and make viewing arrangements in advance.',
    '044': 'Earlier research listed January 21 to 31, 2027 for the Boulder edition. Confirm the current program, reserve specific screenings and plan for winter weather.',
    '045': 'Earlier research listed showcase dates from January 27 to February 14, 2027. Check the final program and choose a few venues if you prefer a shorter visit.',
    '046': 'Earlier research listed February 5 to 14, 2027. Confirm the program and prepare for cold and slippery ground.',
    '047': 'The ride involves window entry, acceleration, vibration and strong G-forces. Ask the operator about participation requirements; confirm current dates and prices.',
    '049': 'Earlier research listed January 30, 2027. Confirm the parade date and consider a reserved waterfront or brunch viewpoint for a calmer visit.',
    '050': 'Earlier research listed January 21 to 24, 2027. This festival can be crowded; choose a comfortable viewing base and confirm the final program.',
    '052': 'A stationary viewing spot can be easier than following the whole parade. Confirm the Sunday schedule before going.',
    '053': 'Earlier research listed performances through February 28, 2027. Check the current run and seating before planning a visit.',
    '059': 'Earlier research listed a January 19 to February 28, 2027 winter season. Choose a current program and seats that suit you.',
    '061': 'Earlier research indicated January to June 2027 classes were open. Confirm the class schedule, level of exertion and accommodation access.',
    '062': 'Short sessions may be available. Confirm the current studio schedule, class format and access before reserving.',
    '063': 'A gentle sensory workshop. Check reservations and any fragrance sensitivities before attending.',
    '068': 'The earlier research described a two-hour experience. Dancing can be enjoyed or skipped.',
    '069': 'The earlier research described a small-group encounter of about 30 minutes. There is no swimming; touching an animal is never guaranteed. Confirm current access and participation rules.',
    '070': 'Winter crawfish supply varies with the weather. Confirm the current season, private format and availability well ahead.',
    '071': 'The earlier research listed a three-hour class around $149 per person. Confirm current cost, standing time and dietary options.',
    '074': 'Special sessions happen periodically. Check the winter calendar; tasting alcohol is optional.',
    '080': 'Earlier research listed February 25 to 28, 2027 for the festival. Check the final event calendar and reserve a specific dinner.',
    '081': 'The astronaut program is offered periodically. Confirm dates and access; simulator elements can be skipped if unsuitable.',
    '082': 'Launches can move or be cancelled. Plan this as part of a longer Space Coast visit and choose a seated viewing option.',
    '085': 'The earlier research listed tickets from $199 and performances through March 28, 2027. The experience involves moving between floors and standing; ask about elevator access and current details.',
    '089': 'Shows are seated but can have powerful visual and sound effects. Check the specific production if you are sensitive to motion or sensory intensity.',
    '090': 'This is a large museum. Give yourself time for rests and check current opening hours.',
    '091': 'Earlier research listed February 6 to April 25, 2027 for the Orchid Show. Confirm the exhibition, tickets and conservatory route.',
    '092': 'Earlier research listed a January 22 to March 21, 2027 season with selected February evenings. Confirm dates and indoor walking routes.',
    '094': 'Animal encounters depend on the animals and staff. Earlier research listed $99 and daily sessions except Tuesdays; confirm current availability and price.',
    '095': 'The earlier research described a 45-minute small-group encounter at $75 plus admission. Check the current schedule, price and participation rules. No swimming is required.',
    '097': 'Choose a current Library of Congress evening program and confirm seating and access before visiting.',
    '100': 'These sites address painful history. Give yourself time and choose a manageable visit with room to reflect afterward.',
    '102': 'The falls do not freeze solid. Check the trolley schedule, weather and icy footing on the day you visit.',
    '110': 'Earlier research listed January 7 to 10, 2027. Confirm the final program and reserve admission and lodging early.',
}

PROVIDERS = {
    '002': ('Talkeetna Air Taxi', 'https://www.talkeetnaair.com/flightseeing/'),
    '003': ('Alaska Railroad', 'https://www.alaskarailroad.com/ride-a-train/our-trains/aurora-winter'),
    '007': ('Musk Ox Farm', 'https://www.muskoxfarm.org/'),
    '010': ("Rod's Alaskan Guide Service", 'https://rodsalaskanguideservice.com/ice-fishing/'),
    '019': ('LIGO Livingston', 'https://www.ligo.caltech.edu/LA/page/Science-Saturdays'),
    '020': ('Bellagio', 'https://bellagio.mgmresorts.com/en/entertainment/o-by-cirque-du-soleil.html'),
    '025': ('Atlantis Adventures', 'https://www.atlantisadventures.com/waikiki/'),
    '026': ('Longneck Manor', 'https://www.longneckmanor.com/giraffe-suite'),
    '030': ('Greyfield Inn', 'https://greyfieldinn.com/'),
    '040': ('Alinea', 'https://alinearestaurant.com/'),
    '047': ('NASCAR Racing Experience', 'https://nascarracingexperience.com/speedways/daytona-international-speedway/'),
    '061': ('John C. Campbell Folk School', 'https://www.folkschool.org/'),
    '068': ('Makoa Quest', 'https://www.makoaquest.org/quest-details/hawaiian-hula-lei-making'),
    '069': ('Georgia Aquarium', 'https://www.georgiaaquarium.org/experience/sea-otter-encounter/'),
    '070': ('Crawfish Haven', 'https://www.crawfishhaven.net/'),
    '081': ('Kennedy Space Center', 'https://www.kennedyspacecenter.com/explore-attractions/meet-an-astronaut/fly-with-an-astronaut/'),
    '085': ('Masquerade', 'https://masqueradenyc.com/'),
    '094': ('National Aviary', 'https://www.aviary.org/programs-encounters/animal-encounters/sloth-encounter/'),
    '095': ('The Florida Aquarium', 'https://www.flaquarium.org/visit/experiences/penguin-encounter/'),
    '102': ('Niagara Falls State Park', 'https://www.niagarafallsstatepark.com/park-information/itineraries/winter-itinerary/'),
    '110': ('Key West Literary Seminar', 'https://www.kwls.org/seminar/'),
}

TEASERS = {
    '002': 'See snowy Denali and its glaciers from a small aircraft.',
    '008': 'Meet rescued Alaskan animals in spacious habitats.',
    '019': 'Visit the observatory that detects ripples in space-time.',
    '024': 'Watch humpback whales and listen for their underwater song.',
    '031': 'Watch a bioluminescent bay glow from a guided boat.',
    '040': 'Turn dinner into an evening of theatrical surprises.',
    '073': 'Discover the flavors and stories of Gullah Geechee cooking.',
    '081': 'Tour Kennedy Space Center with an experienced astronaut.',
    '085': 'Step into a masked world inspired by The Phantom of the Opera.',
    '086': 'Open a door into Meow Wolf’s surreal story worlds.',
    '096': 'See Frank Lloyd Wright’s desert home and design laboratory.',
    '100': 'Make space for reflection at Montgomery’s Legacy Sites.',
    '110': 'Share four days of poetry, conversation and island air.',
}

def calm(note):
    note = re.sub(r'^(SECONDARY OPTION|SECONDARY / CONDITIONAL|CONDITIONAL THRILL)\.\s*', '', note)
    note = note.replace('Supplied dates:', 'Earlier research listed these dates:')
    note = note.replace('Supplied season:', 'Earlier research listed this season:')
    note = note.replace('Supplied showcase:', 'Earlier research listed this showcase:')
    note = note.replace('Supplied festival:', 'Earlier research listed this festival:')
    note = note.replace('Supplied winter season:', 'Earlier research listed this winter season:')
    note = note.replace('Supplied schedule:', 'Earlier research listed this schedule:')
    note = note.replace('supplied research', 'earlier research')
    note = note.replace('No swimming.', 'No swimming is needed.')
    note = note.replace('Check ', 'Before you go, check ', 1) if note.startswith('Check ') else note
    note = note.replace('Confirm ', 'Before you go, confirm ', 1) if note.startswith('Confirm ') else note
    note = note.replace('Verify ', 'Before you go, verify ', 1) if note.startswith('Verify ') else note
    return note

for path in sorted(DATA.glob('*.json')):
    record = json.loads(path.read_text())
    id = record['id']
    record['goodToKnow'] = NOTES.get(id, record.get('goodToKnow') or calm(record['practicalNoteOriginal']))
    record['whyItMightDelightYou'] = record.get('whyItMightDelightYou') or record['teaser']
    if id in TEASERS:
        record['teaser'] = TEASERS[id]
    if id in PROVIDERS:
        name, url = PROVIDERS[id]
        record['provider'] = {'name': name, 'url': url}
    record.pop('practicalNoteOriginal', None)
    if id == '063':
        record['description'] = 'Spend time experimenting with perfume oils and guided blending to create a personal fragrance.'
        record['teaser'] = 'Blend perfume oils into a fragrance of your own.'
        record['whyItMightDelightYou'] = 'A small sensory adventure that leaves you with something personal.'
    if id == '091':
        record['description'] = 'Explore a conservatory filled with orchids, color and imaginative displays during the seasonal flower show.'
        record['teaser'] = 'Step into a warm indoor world of orchids and color.'
        record['whyItMightDelightYou'] = 'A garden in bloom can feel like a different season for an afternoon.'
    if id == '097':
        record['teaser'] = 'Spend an evening among books, performances and grand interiors.'
        record['whyItMightDelightYou'] = 'The Library becomes a place to linger, listen and discover.'
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
