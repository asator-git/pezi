#!/usr/bin/env python3
"""Extrahiert die Fragen aus fragen.txt (MacRoman) nach questions.json.

Wortlaut wird exakt uebernommen (inkl. Austriazismen, Skalen, Tippfehler).
Aufruf: python3 tools/extract_questions.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- Rohtext dekodieren und in Zeilen zerlegen ----------------------------
raw = (ROOT / "fragen.txt").read_bytes().decode("mac-roman")
raw = raw.replace("\r\n", "\n").replace("\r", "\n")
lines = [ln.strip() for ln in re.sub(r"\n{2,}", "\n", raw).split("\n")]

# Der Fragenblock des Buches, abgegrenzt durch die Krizzel-Aufforderung
# davor und "Fin der bohrenden Fragen." danach.
start = lines.index("Egal ob alleine oder gemeinsam.") + 1
end = lines.index("Fin der bohrenden Fragen.")
block = lines[start:end]

# Zeilen im Block, die keine Frage sind, sondern Zusatz zur Zeile davor.
NOTES = {
    "(Bittegerne hier zeichnerisch austoben und mir unbedingt schicken :D)",
    "* Jo, i kumm aus der Steiermoark!",
}

# Die eine Frage, die im Vorwort steht, aber zum Kanon gehoert.
PREFACE = (
    "Was ist eigentlich dein Lieblingsgefühl?",
    "(Die Frage hab‘ ich tatsächlich zum ersten Mal in der Kloschlange gestellt.)",
)

# --- Fragen + notes sammeln ----------------------------------------------
collected = [{"text": PREFACE[0], "note": PREFACE[1]}]
for ln in block:
    if not ln:
        continue
    if ln in NOTES:
        collected[-1]["note"] = ln
        continue
    collected.append({"text": ln})

# --- Tags ----------------------------------------------------------------
# "skala" wird automatisch erkannt, "date" aus der Bonus-Liste abgeleitet,
# "liebe"/"selbst"/"random" sind redaktionell zugeordnet:
#   liebe  = Beziehung, Sex, Naehe, andere Menschen
#   selbst = Selbstbild, Innenleben, Reflexion
#   random = Alltag, Spass, Absurdes
THEMES = {
    "Was ist eigentlich dein Lieblingsgefühl?": ["selbst"],
    "Worauf würdest du gerne öfter scheißen?": ["selbst", "random"],
    "Wie gut kennst du dich selbst von 1-3.172?": ["selbst"],
    "Was sind die positiven Seiten deiner Unsicherheiten?": ["selbst"],
    "Wie ist dein Leben grad in einem Wort?": ["selbst"],
    "Welches Arsch-Tattoo würdest du dir machen, wenn du 1 Million Euro dafür kriegen würdest?": ["random"],
    "Würdest du dich selbst in einer Bar aufreißen?": ["selbst", "liebe"],
    "Was findest du an anderen Menschen am beeindruckendsten?": ["liebe"],
    "Wovon hast du grad zu viel, wovon zu wenig?": ["selbst"],
    "Brauchst du viel, um glücklich zu sein?": ["selbst"],
    "Was ist das schönste Kompliment, das man dir machen kann?": ["selbst", "liebe"],
    "Wann hast du zuletzt so richtig die Sau rausgelassen?": ["selbst", "random"],
    "Was macht für dich ein richtig gutes Gespräch aus?": ["liebe"],
    "Wie leithaglich bist du von 1-37?": ["selbst"],
    "Wie seeeeeehnsüchtig bist du?": ["selbst", "liebe"],
    "Wie viel kriminelle Energie hast du von 1-2.300?": ["selbst", "random"],
    "Was hat dich zuletzt an dir selbst überrascht?": ["selbst"],
    "Was erwartest du von der Liebe?": ["liebe"],
    "Wie viel Schmuse-Selbstvertrauen hast du von 1-321?": ["liebe", "selbst"],
    "Was sollen die Leute nach deinem Tod über dich sagen?": ["selbst"],
    "Wie entspannst du am besten?": ["selbst"],
    "Wo bist du manchmal nicht ganz ehrlich zu dir selbst?": ["selbst"],
    "Womit sollte man am Bahnhof auf dich warten, wenn man dich abholt?": ["liebe", "random"],
    "Was sind 9 Dinge, die du richtig gut kannst?": ["selbst"],
    "Was sagen Family & Friends: Was kannst du am besten?": ["selbst", "liebe"],
    "Würdest du deine/n Partner/in als deine/n Liebhaber/in bezeichnen?": ["liebe"],
    "Was verletzt dich?": ["selbst"],
    "Wer war die spannendste Person, die du zuletzt kennengelernt hast?": ["liebe"],
    "Welche 3 Eigenschaften magst du an anderen, die du selbst nicht hast?": ["selbst", "liebe"],
    "Was ist Erfüllung für dich?": ["selbst"],
    "Was fehlt dir zu einem erfüllten Leben?": ["selbst"],
    "Wie gut kannst du den Moment leben von 1-76?": ["selbst"],
    "Wie empathisch ist deine innere Stimme?": ["selbst"],
    "Was muss ich über dich wissen, um dich zu kennen?": ["selbst", "liebe"],
    "Tendierst du dazu, über deine Grenzen zu gehen?": ["selbst"],
    "Wie sehr überzergrübelst du das Leben von 1-133?": ["selbst"],
    "Was ist deine Lieblingsabteilung im Supermarkt?": ["random"],
    "Wie bequem bist du in deiner Sexualität?": ["liebe", "selbst"],
    "Wie gut kannst du dich auf Neues einlassen von 1-17?": ["selbst"],
    "Was machst du nach einem Scheiß-Tag am liebsten?": ["selbst", "random"],
    "Sagst du deinen Friends, dass du sie liebst?": ["liebe"],
    "Wie gut gspiarst du dich selbst von 1-234?": ["selbst"],
    "Von wem fühlst du dich am besten verstanden?": ["liebe"],
    "Was macht dir grad am meisten Spaß im Leben?": ["selbst"],
    "Hast du oft ein schlechtes Gewissen?": ["selbst"],
    "Was sind deine Selbstzweifel?": ["selbst"],
    "Was magst du an der Zeit mit mir am liebsten?": ["liebe"],
    "Wie gut kannst du Komplimente annehmen von 1-713?": ["selbst"],
    "Wie viel Bestätigung brauchst du für dein Aussehen?": ["selbst"],
    "Wie gut kannst du bei mir du selbst sein von 1-311?": ["liebe", "selbst"],
    "Von wem hast du am meisten über die Liebe gelernt?": ["liebe"],
    "Was glaubst du kann man von dir lernen?": ["selbst"],
    "Worüber lachst du am liebsten?": ["selbst", "random"],
    "Was war das Intimste, das du je gemacht hast?": ["liebe"],
    "Grübelst du viel?": ["selbst"],
    "Wie gut kannst du Entscheidungen treffen von 1-591?": ["selbst"],
    "Wenn du dich entscheiden müsstest: Selbstverwirklichung oder Sicherheit?": ["selbst"],
    "Kannst du besser „Ja“ oder „Nein“ sagen?": ["selbst"],
    "Was beschäftigt dich grad am meisten?": ["selbst"],
    "Was ist das Geilste am Älter werden?": ["selbst", "random"],
    "Glaubst du, tanzen die Leute so wie sie Sex haben?": ["liebe", "random"],
    "Wie sehr hast du dein Leben im Griff von 1-46?": ["selbst"],
    "Was sind deine 5 Lieblingssnacks?": ["random"],
    "Ist dir bedingungslose Wahrheit in Beziehungen wichtig?": ["liebe"],
    "Wie frei fühlst du dich von 1-96?": ["selbst"],
    "Wie stehst du zu Notlügen?": ["selbst", "liebe"],
    "Wie gut kannst du über dich selbst lachen von 1-793?": ["selbst"],
    "Hattest du eine wüde Jugend?": ["selbst", "random"],
    "Was ist das Cuteste in deinem Leben?": ["liebe", "random"],
    "Wie ist deine sexuelle Persönlichkeit in 3 Worten?": ["liebe", "selbst"],
    "Vor wem weinst du am liebsten?": ["liebe"],
    "Was willst du dir noch beweisen?": ["selbst"],
    "Was drücken meine Augen für dich aus?": ["liebe"],
    "Überzeugt dich deine Selbstkritik?": ["selbst"],
    "Was magst du an der Liebe nicht?": ["liebe"],
    "Welches Körperteil vernachlässigst du am meisten?": ["selbst", "random"],
    "Welches Arsch-Tattoo würdest du mir machen?": ["liebe", "random"],
    "Wen umarmst du am liebsten?": ["liebe"],
    "Was war das mutigste „Nein“, das du jemals gesagt hast?": ["selbst"],
    "Gibt es eine Seite an dir, von der du Angst hast, sie zu zeigen?": ["selbst"],
    "Was ist dein happy place?": ["selbst", "random"],
    "Was magst du an deinen best friends am liebsten?": ["liebe"],
    "Was findest du unsexy?": ["liebe", "random"],
    "Wie sieht dein perfekter Tag aus?": ["selbst", "random"],
    "Wenn du dich entscheiden müsstest: Ein Leben lang Wasser trinken oder alles was du magst, aber immer mit einem Schuss Pipi?": ["random"],
    "Über welche 3 Themen sprichst du am liebsten?": ["selbst"],
    "Was ist das hässlichste Ding in deiner Wohnung?": ["random"],
    "Wie grindig findest du dich selbst von 1-137?": ["selbst", "random"],
    "Wie gehst du mit Wut um?": ["selbst"],
    "Was sind deine Extreme?": ["selbst"],
    "Musst du jemanden sexy finden, um Sex mit der Person zu haben?": ["liebe"],
    "Wie nahe bist du deinem Idealbild von 1-3.100?": ["selbst"],
}

# Bonus-Liste "Nie wieder scheissfade Dates!" -> Tag "date".
# Der Wortlaut dort weicht bei 6 Fragen leicht ab (andere Skalenzahl,
# "Scheisstag" statt "Scheiss-Tag", ...); kanonisch ist der Hauptteil.
DATE = [
    "Würdest du dich selbst in einer Bar aufreißen?",
    "Von wem hast du am meisten über die Liebe gelernt?",
    "Wie sehr hast du dein Leben im Griff von 1-46?",
    "Was muss ich über dich wissen, um dich zu kennen?",
    "Was macht dir grad am meisten Spaß im Leben?",
    "Was machst du nach einem Scheiß-Tag am liebsten?",
    "Wie entspannst du am besten?",
    "Über welche 3 Themen sprichst du am liebsten?",
    "Was findest du unsexy?",
    "Wie viel kriminelle Energie hast du von 1-2.300?",
    "Was sind deine 5 Lieblingssnacks?",
    "Wen umarmst du am liebsten?",
    "Wie gut kannst du den Moment leben von 1-76?",
    "Wo bist du manchmal nicht ganz ehrlich zu dir selbst?",
    "Was erwartest du von der Liebe?",
    "Wie sieht dein perfekter Tag aus?",
    "Worauf würdest du gerne öfter scheißen?",
    "Was magst du an deinen best friends am liebsten?",
]

# --- zusammenbauen -------------------------------------------------------
TAG_ORDER = ["skala", "date", "liebe", "selbst", "random"]
questions = []
for i, item in enumerate(collected, start=1):
    text = item["text"]
    tags = set(THEMES[text])
    if "von 1-" in text:
        tags.add("skala")
    if text in DATE:
        tags.add("date")
    q = {"id": i, "text": text, "tags": [t for t in TAG_ORDER if t in tags]}
    if "note" in item:
        q["note"] = item["note"]
    questions.append(q)

# --- Konsistenzpruefungen ------------------------------------------------
assert len(questions) == len(set(q["text"] for q in questions)), "Dublette"
missing = [q["text"] for q in THEMES if q not in {x["text"] for x in questions}]
assert not missing, f"Tags fuer nicht vorhandene Frage: {missing}"
for d in DATE:
    assert any(q["text"] == d for q in questions), f"Date-Frage fehlt: {d}"

out = {
    "title": "Oha! Fragen",
    "source": "Oha! Fragen aus den Jahren 2023-2025",
    "license": "CC BY 4.0",
    "questions": questions,
}
(ROOT / "questions.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"{len(questions)} Fragen geschrieben")
for t in TAG_ORDER:
    print(f"  {t}: {sum(1 for q in questions if t in q['tags'])}")
print(f"  mit note: {sum(1 for q in questions if 'note' in q)}")
