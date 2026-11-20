#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the complete multilingual static site for familypick.studiotaeo.com.

Zero third-party Python dependencies (uses Python 3 stdlib + macOS sips / cwebp).

Outputs:
  - /index.html                   (ko -> personas/kr, screenshots/ko)
  - /en/index.html                (en-US -> personas/en, screenshots/en)
  - /en-GB/index.html             (en-GB -> personas/en, screenshots/en-GB)
  - /ja/index.html                (ja -> personas/jp, screenshots/ja)
  - /zh-Hans/index.html           (zh-Hans -> personas/zh, screenshots/zh-Hans)
  - /zh-Hant/index.html           (zh-Hant -> personas/zh, screenshots/zh-Hant)
  - /fr-FR/index.html             (fr-FR -> personas/eu, screenshots/fr-FR)
  - /de-DE/index.html             (de-DE -> personas/eu, screenshots/de-DE)
  - /es-ES/index.html             (es-ES -> personas/eu, screenshots/es-ES)
  - /es-MX/index.html             (es-MX -> personas/eu, screenshots/es-MX)
"""

import argparse
import glob
import html as html_lib
import os
import re
import shutil
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from i18n_data import APPSTORE_URL, KEYS, LOCALES, SITE_ORIGIN, STRINGS  # noqa: E402

DEFAULT_ICON_SRC = "/Volumes/DEV_SSD/prj/photo-pick/ios/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png"
DEFAULT_PERSONAS_SRC = "/Volumes/DEV_SSD/prj/photo-pick/build/marketing/personas"
DEFAULT_SCREENSHOT_SRCS = [
    "/Volumes/DEV_SSD/prj/photo-pick/build/marketing/screenshots",
    "/Volumes/DEV_SSD/prj/photo-pick/marketing/screenshots",
]
STUDIOTAEO_DIR = "/Volumes/DEV_SSD/prj/StudioTaeo"
BADGE_API = "https://toolbox.marketingtools.apple.com/api/v2/badges/download-on-the-app-store"

PERSONA_STEMS = [
    ("01-hero-park", 720),
    ("02-play-blocks", 480),
    ("03-snack-smile", 480),
    ("04-outdoor-walk", 480),
    ("05-review-messy-room", 480),
    ("06-review-parent-selfie", 480),
]

REGIONS = ["kr", "jp", "zh", "en", "eu"]

CWEBP = shutil.which("cwebp") or ("/opt/homebrew/bin/cwebp" if os.path.exists("/opt/homebrew/bin/cwebp") else None)
SIPS = shutil.which("sips") or "/usr/bin/sips"

HAND_CHECK_SVG = (
    '<svg class="pencil-chk" viewBox="0 0 20 20" fill="none" aria-hidden="true">'
    '<circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="1.5" stroke-opacity="0.72"/>'
    '<path d="M6.3 10.3 8.9 12.8 13.8 7.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)


def convert_to_webp_or_jpg(src_path: str, dst_stem_path: str, target_width: int, force: bool = False) -> str:
    webp_dst = dst_stem_path + ".webp"
    jpg_dst = dst_stem_path + ".jpg"

    if not force:
        if os.path.exists(webp_dst) and os.path.getsize(webp_dst) > 0:
            return os.path.basename(webp_dst)
        if os.path.exists(jpg_dst) and os.path.getsize(jpg_dst) > 0 and not CWEBP:
            return os.path.basename(jpg_dst)

    os.makedirs(os.path.dirname(dst_stem_path), exist_ok=True)

    if CWEBP:
        cmd = [CWEBP, "-quiet", "-q", "82", "-resize", str(target_width), "0", src_path, "-o", webp_dst]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and os.path.exists(webp_dst):
            return os.path.basename(webp_dst)

    subprocess.run(
        [SIPS, "-s", "format", "jpeg", "-s", "formatOptions", "82", "--resampleWidth", str(target_width), src_path, "--out", jpg_dst],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    return os.path.basename(jpg_dst)


def ensure_brand_icons(force: bool = False) -> None:
    assets_dir = os.path.join(ROOT, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    app_icon = os.path.join(assets_dir, "app-icon.png")
    favicon = os.path.join(assets_dir, "favicon.png")
    if os.path.exists(DEFAULT_ICON_SRC):
        if force or not os.path.exists(app_icon):
            subprocess.run([SIPS, "-z", "256", "256", DEFAULT_ICON_SRC, "--out", app_icon], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if force or not os.path.exists(favicon):
            subprocess.run([SIPS, "-z", "64", "64", DEFAULT_ICON_SRC, "--out", favicon], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def sync_personas(personas_src: str, force: bool = False) -> dict:
    resolved = {r: {} for r in REGIONS}
    for region in REGIONS:
        local_dir = os.path.join(ROOT, "assets", "personas", region)
        os.makedirs(local_dir, exist_ok=True)
        ext_dir = os.path.join(personas_src, region) if personas_src and os.path.isdir(personas_src) else ""

        for stem, width in PERSONA_STEMS:
            dst_stem = os.path.join(local_dir, stem)
            src_candidate = None
            for search_dir in ([ext_dir, local_dir] if ext_dir else [local_dir]):
                for ext in (".jpg", ".jpeg", ".png", ".webp"):
                    cand = os.path.join(search_dir, stem + ext)
                    if os.path.exists(cand) and os.path.getsize(cand) > 0:
                        src_candidate = cand
                        break
                if src_candidate:
                    break

            if src_candidate:
                if src_candidate == dst_stem + ".webp" and not force:
                    out_fn = os.path.basename(src_candidate)
                else:
                    out_fn = convert_to_webp_or_jpg(src_candidate, dst_stem, width, force=force)
                resolved[region][stem] = f"assets/personas/{region}/{out_fn}"

    return resolved


def find_screenshot_sources_for_locale(loc: dict, extra_srcs: list) -> list:
    loc_key = loc["dir"] or "ko"
    short_lang = loc["code"].split("-")[0]
    candidate_subfolders = []
    for k in (loc["code"], loc_key, short_lang):
        if k and k not in candidate_subfolders:
            candidate_subfolders.append(k)

    search_roots = [p for p in extra_srcs if p and os.path.isdir(p)] + [os.path.join(ROOT, "assets", "screenshots")]

    for root_dir in search_roots:
        for sub in candidate_subfolders:
            folder = os.path.join(root_dir, sub)
            if not os.path.isdir(folder):
                continue

            files = []
            for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
                files.extend(glob.glob(os.path.join(folder, ext)))
            files = sorted(f for f in files if os.path.getsize(f) > 0)
            if not files:
                continue

            iphone_files = [f for f in files if "ipad" not in os.path.basename(f).lower()]
            pool = iphone_files if len(iphone_files) >= 4 else files

            matched = []
            for idx in range(1, 5):
                prefixes = (f"ss-0{idx}", f"ss_{idx}", f"0{idx}", f"{idx}_", f"{idx}-")
                hit = None
                for f in pool:
                    bn = os.path.basename(f).lower()
                    if bn.startswith(prefixes) or f"0{idx}_" in bn or f"0{idx}-" in bn or f"-0{idx}." in bn:
                        hit = f
                        break
                if hit:
                    matched.append(hit)

            if len(matched) == 4:
                return matched
            if len(pool) >= 4:
                return pool[:4]

    return []


def sync_screenshots(extra_srcs: list, force: bool = False) -> dict:
    resolved = {}
    for loc in LOCALES:
        loc_key = loc["dir"] or "ko"
        out_dir = os.path.join(ROOT, "assets", "screenshots", loc_key)
        os.makedirs(out_dir, exist_ok=True)
        srcs = find_screenshot_sources_for_locale(loc, extra_srcs)
        if len(srcs) < 4:
            resolved[loc["code"]] = []
            continue

        rels = []
        for idx, sp in enumerate(srcs[:4], start=1):
            dst_stem = os.path.join(out_dir, f"ss-0{idx}")
            if os.path.abspath(sp) == os.path.abspath(dst_stem + ".webp") and not force:
                out_fn = f"ss-0{idx}.webp"
            else:
                out_fn = convert_to_webp_or_jpg(sp, dst_stem, 680, force=force)
            rels.append(f"assets/screenshots/{loc_key}/{out_fn}")
        resolved[loc["code"]] = rels
    return resolved


def ensure_badges(force: bool = False) -> dict:
    badges_dir = os.path.join(ROOT, "assets", "badges")
    os.makedirs(badges_dir, exist_ok=True)

    studiotaeo_map = {
        "ko-kr": "",
        "en-us": "en",
        "en-gb": "en",
        "ja-jp": "ja",
        "zh-cn": "zh-Hans",
        "zh-tw": "zh-Hant",
        "fr-fr": "fr-FR",
        "de-de": "de-DE",
        "es-es": "es-ES",
        "es-mx": "es-MX",
    }

    result = {}
    for loc in LOCALES:
        apple = loc["apple"]
        result[apple] = {}
        for variant in ("black", "white"):
            dst = os.path.join(badges_dir, f"{apple}-{variant}.svg")
            if os.path.exists(dst) and os.path.getsize(dst) > 0 and not force:
                result[apple][variant] = f"assets/badges/{apple}-{variant}.svg"
                continue

            copied = False
            st_sub = studiotaeo_map.get(apple)
            if st_sub is not None and apple != "en-gb":
                st_path = os.path.join(STUDIOTAEO_DIR, st_sub, f"appstore-{variant}.svg") if st_sub else os.path.join(STUDIOTAEO_DIR, f"appstore-{variant}.svg")
                if os.path.exists(st_path) and os.path.getsize(st_path) > 0:
                    shutil.copy2(st_path, dst)
                    copied = True

            if not copied:
                for code in (apple, "en-us"):
                    try:
                        req = urllib.request.Request(
                            f"{BADGE_API}/{variant}/{code}",
                            headers={"User-Agent": "Mozilla/5.0"},
                        )
                        data = urllib.request.urlopen(req, timeout=12).read()
                        if b"<svg" in data[:300]:
                            with open(dst, "wb") as fh:
                                fh.write(data)
                            copied = True
                            break
                    except Exception:
                        pass

            if not copied:
                fb = os.path.join(STUDIOTAEO_DIR, "en", f"appstore-{variant}.svg")
                if os.path.exists(fb):
                    shutil.copy2(fb, dst)

            result[apple][variant] = f"assets/badges/{apple}-{variant}.svg"

    return result


def build_hreflang_links() -> str:
    lines = []
    for loc in LOCALES:
        url = f"{SITE_ORIGIN}/" + (f"{loc['dir']}/" if loc["dir"] else "")
        lines.append(f'<link rel="alternate" hreflang="{loc["hreflang"]}" href="{url}">')
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{SITE_ORIGIN}/en/">')
    return "\n".join(lines)


def build_lang_dropdown(active_code: str) -> str:
    items = ['<ul class="lang-dropdown" role="listbox">']
    for loc in LOCALES:
        href = "/" + (f"{loc['dir']}/" if loc["dir"] else "")
        is_active = loc["code"] == active_code
        cls = ' class="active"' if is_active else ""
        chk = "<span>✓</span>" if is_active else ""
        items.append(f'  <li role="option"><a href="{href}" lang="{loc["lang"]}"{cls}><span>{loc["name"]}</span>{chk}</a></li>')
    items.append("</ul>")
    return "\n".join(items)


def build_serif_font_link(lang: str) -> str:
    families = ["Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400"]
    if lang == "ko":
        families.append("Gowun+Batang:wght@400;700")
    elif lang == "ja":
        families.append("Shippori+Mincho:wght@400;500")
    elif lang == "zh-Hans":
        families.append("Noto+Serif+SC:wght@400;500")
    elif lang == "zh-Hant":
        families.append("Noto+Serif+TC:wght@400;500")

    # Always include Noto Sans SC & TC so the language menu renders Chinese glyphs everywhere
    families.append("Noto+Sans+SC:wght@400;500")
    families.append("Noto+Sans+TC:wght@400;500")
    joined = "&family=".join(families)
    return f'<link href="https://fonts.googleapis.com/css2?family={joined}&display=swap" rel="stylesheet">'


def format_hero_note(note_text: str) -> str:
    parts = [p.strip() for p in note_text.split("·") if p.strip()]
    return " ".join(f'<span class="hn-seg">{p}</span>' for p in parts)


def render_hero_stage(loc: dict, s: dict, persona_map: dict, ss_list: list, prefix: str) -> str:
    reg = persona_map.get(loc["region"], {})
    p1_rel = reg.get("01-hero-park", "")
    p2_rel = reg.get("03-snack-smile", "")
    ss_hero = ss_list[0] if ss_list else "assets/screenshots/ko/ss-01.webp"

    p1_alt = html_lib.escape(s["HERO_P1_CAP"], quote=True)
    p2_alt = html_lib.escape(s["HERO_P2_CAP"], quote=True)
    ss_alt = html_lib.escape(f"{s['BRAND']} — {s['G1_TITLE']}", quote=True)

    return f"""<div class="desk-stage reveal" data-d="1">
        <div class="mat-sheet" aria-hidden="true"></div>

        <figure class="photo-print pr-left">
          <div class="pp-frame">
            <img src="{prefix}{p1_rel}" alt="{p1_alt}" width="260" height="260" loading="eager">
          </div>
          <figcaption class="pp-note">
            <span>{s["HERO_P1_CAP"]}</span>
            {HAND_CHECK_SVG}
          </figcaption>
        </figure>

        <div class="device-frame">
          <img src="{prefix}{ss_hero}" alt="{ss_alt}" width="680" height="1478" loading="eager" fetchpriority="high">
        </div>

        <figure class="photo-print pr-right">
          <div class="pp-frame">
            <img src="{prefix}{p2_rel}" alt="{p2_alt}" width="240" height="240" loading="eager">
          </div>
          <figcaption class="pp-note">
            <span>{s["HERO_P2_CAP"]}</span>
            {HAND_CHECK_SVG}
          </figcaption>
        </figure>
      </div>"""


def render_essay_print(loc: dict, s: dict, persona_map: dict, prefix: str) -> str:
    reg = persona_map.get(loc["region"], {})
    p3_rel = reg.get("02-play-blocks", "")
    p3_alt = html_lib.escape(s["HERO_P3_CAP"], quote=True)
    return f"""<figure class="essay-print">
            <div class="ep-img"><img src="{prefix}{p3_rel}" alt="{p3_alt}" width="320" height="240" loading="lazy"></div>
            <figcaption class="ep-cap">{s["HERO_P3_CAP"]}</figcaption>
          </figure>"""


def render_signoff_print(loc: dict, s: dict, persona_map: dict, prefix: str) -> str:
    reg = persona_map.get(loc["region"], {})
    p4_rel = reg.get("04-outdoor-walk", "")
    p4_alt = html_lib.escape(s["HERO_P4_CAP"], quote=True)
    return f"""<div class="signoff-print" aria-hidden="true">
            <img src="{prefix}{p4_rel}" alt="{p4_alt}" width="200" height="200" loading="lazy">
          </div>"""


def render_gallery_strip(s: dict, ss_list: list, prefix: str) -> str:
    cards = ['<div class="ex-strip">']
    for idx in range(1, 5):
        rel = ss_list[idx - 1] if len(ss_list) >= idx else f"assets/screenshots/ko/ss-0{idx}.webp"
        title = s[f"G{idx}_TITLE"]
        desc = s[f"G{idx}_DESC"]
        alt_text = html_lib.escape(f"{s['BRAND']} — {title}", quote=True)
        cards.append(
            f"""  <article class="ex-item reveal">
    <div class="ex-cap">
      <div class="ex-cap-hd">
        <span class="num-it">0{idx}</span>
        <h3>{title}</h3>
      </div>
      <p>{desc}</p>
    </div>
    <div class="ex-phone">
      <img src="{prefix}{rel}" alt="{alt_text}" width="680" height="1478" loading="lazy">
    </div>
  </article>"""
        )
    cards.append("</div>")
    return "\n".join(cards)


def render_locale_page(
    tpl: str,
    loc: dict,
    hreflang_html: str,
    persona_map: dict,
    ss_map: dict,
    badges: dict,
) -> str:
    s = STRINGS[loc["code"]]
    prefix = "" if loc["dir"] == "" else "../"
    home_href = "/" + (f"{loc['dir']}/" if loc["dir"] else "")
    canonical = f"{SITE_ORIGIN}{home_href}"
    terms_file = "terms.html" if loc["code"] == "ko" else "terms-en.html"
    privacy_file = "privacy.html" if loc["code"] == "ko" else "privacy-en.html"

    badge_black = prefix + badges[loc["apple"]]["black"]
    badge_white = prefix + badges[loc["apple"]]["white"]
    ss_list = ss_map.get(loc["code"], [])

    out = tpl
    replacements = {
        "%%CANONICAL_URL%%": canonical,
        "%%HREFLANG_LINKS%%": hreflang_html,
        "%%SERIF_FONT_LINK%%": build_serif_font_link(loc["lang"]),
        "%%HOME_HREF%%": home_href,
        "%%LANG_DROPDOWN%%": build_lang_dropdown(loc["code"]),
        "%%LANGNAME%%": loc["name"],
        "%%LANG%%": loc["lang"],
        "%%APPSTORE_URL%%": APPSTORE_URL,
        "%%BADGE_BLACK_SRC%%": badge_black,
        "%%BADGE_WHITE_SRC%%": badge_white,
        "%%TERMS_FILE%%": terms_file,
        "%%PRIVACY_FILE%%": privacy_file,
        "%%HERO_STAGE%%": render_hero_stage(loc, s, persona_map, ss_list, prefix),
        "%%ESSAY_PRINT%%": render_essay_print(loc, s, persona_map, prefix),
        "%%GALLERY_STRIP%%": render_gallery_strip(s, ss_list, prefix),
        "%%SIGNOFF_PRINT%%": render_signoff_print(loc, s, persona_map, prefix),
        "%%HERO_NOTE%%": format_hero_note(s["HERO_NOTE"]),
        "%%P%%": prefix,
    }

    for marker, val in replacements.items():
        out = out.replace(marker, val)

    for k in sorted(KEYS, key=len, reverse=True):
        out = out.replace(f"%%{k}%%", s[k])

    leftover = re.findall(r"%%[A-Z0-9_]+%%", out)
    if leftover:
        raise RuntimeError(f"Unreplaced placeholders in {loc['code']}: {leftover}")

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build familypick.studiotaeo.com static pages.")
    parser.add_argument("--html-only", action="store_true", help="Skip image conversion & badge checks")
    parser.add_argument("--force", action="store_true", help="Re-convert all persona/screenshot WebPs and badges")
    parser.add_argument("--personas-src", default=DEFAULT_PERSONAS_SRC, help="Source directory for regional persona photos")
    parser.add_argument("--screenshots-src", default="", help="Optional external directory for localized screenshots")
    args = parser.parse_args()

    if not args.html_only:
        ensure_brand_icons(force=args.force)

    persona_map = sync_personas("" if args.html_only else args.personas_src, force=args.force)
    ss_srcs = ([args.screenshots_src] if args.screenshots_src else []) + DEFAULT_SCREENSHOT_SRCS
    ss_map = sync_screenshots([] if args.html_only else ss_srcs, force=args.force)
    badges = ensure_badges(force=args.force)

    tpl_path = os.path.join(HERE, "template.html")
    with open(tpl_path, "r", encoding="utf-8") as fh:
        tpl = fh.read()

    hreflang_html = build_hreflang_links()

    for loc in LOCALES:
        html_out = render_locale_page(tpl, loc, hreflang_html, persona_map, ss_map, badges)
        out_dir = ROOT if loc["dir"] == "" else os.path.join(ROOT, loc["dir"])
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "index.html")
        with open(out_file, "w", encoding="utf-8") as fh:
            fh.write(html_out)

        p_cnt = len(persona_map.get(loc["region"], {}))
        s_cnt = len(ss_map.get(loc["code"], []))
        route = "/" + (f"{loc['dir']}/" if loc["dir"] else "")
        print(f"  {loc['code']:8s} -> {route:10s} [region={loc['region']}: {p_cnt}/6 personas · {s_cnt}/4 screenshots]")

    print(f"Built {len(LOCALES)} localized landing pages in {ROOT}")


if __name__ == "__main__":
    main()
