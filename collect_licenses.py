# collect_licenses.py
# Python 3.10+ 권장

import os
import re
import csv
import shutil
from pathlib import Path
from importlib import metadata

# ------------------------------ 공통 설정 ------------------------------
OUT_DIR = Path("dist_licenses")
LICENSES_DIR = OUT_DIR / "licenses"
OUT_DIR.mkdir(exist_ok=True)
LICENSES_DIR.mkdir(parents=True, exist_ok=True)

# 듀얼 라이선스 중 LGPL 선택 대상 (PySide6 계열)
LGPL_CHOICE_PACKAGES = {
    "pyside6",
    "pyside6-essentials",
    "pyside6_addons",
    "pyside6-addons",
    "shiboken6",
}

# 상업용 안내 파일 제외
EXCLUDE_PATTERNS = [
    r"license.*ref.*qt.*commercial",   # LicenseRef-Qt-Commercial*
    r".*qt.*commercial.*",
]
EXCLUDE_REGEXES = [re.compile(pat, re.IGNORECASE) for pat in EXCLUDE_PATTERNS]

# LGPL/GPL 문서 우선 복사
PREFER_PATTERNS = [
    r".*lgpl.*", r".*gpl.*", r"copying(\.txt|\.md|\.rst)?$"
]
PREFER_REGEXES  = [re.compile(pat, re.IGNORECASE) for pat in PREFER_PATTERNS]

# 일반 라이선스 파일 후보
LICENSE_NAME_PATTERNS = [
    r"^license(\.txt|\.md|\.rst)?$",
    r"^licence(\.txt|\.md|\.rst)?$",
    r"^copying(\.txt|\.md|\.rst)?$",
    r"^notice(\.txt|\.md|\.rst)?$",
    r"^copyright(\.txt|\.md|\.rst)?$",
    r"^licen[cs]e-?.*",
    r".*/license(\.txt|\.md|\.rst)?$",
    r".*/copying(\.txt|\.md|\.rst)?$",
    r".*/notice(\.txt|\.md|\.rst)?$",
]
LICENSE_REGEXES = [re.compile(pat, re.IGNORECASE) for pat in LICENSE_NAME_PATTERNS]

COPyleft_HINTS = ["GPL", "LGPL", "AGPL", "MPL"]

# LGPL v3 전문 다운로드 후보 URL (순차 시도)
LGPL_URLS = [
    "https://www.gnu.org/licenses/lgpl-3.0.txt",
    "https://www.gnu.org/licenses/old-licenses/lgpl-3.0.txt",  # 백업 경로
    "https://spdx.org/licenses/LGPL-3.0-only.txt",
]

# ------------------------------ 유틸 ------------------------------
def guess_license_from_classifiers(classifiers):
    for c in classifiers or []:
        if c.startswith("License ::"):
            label = c.split("::")[-1].strip()
            if label:
                return label
    return None

def is_copyleft(license_str: str) -> bool:
    if not license_str:
        return False
    s = license_str.upper()
    return any(h in s for h in COPyleft_HINTS)

def locate_distribution_files(dist):
    try:
        return dist.files or []
    except Exception:
        return []

def find_candidate_license_files(dist) -> list[Path]:
    candidates = []
    files = locate_distribution_files(dist)

    for f in files:
        p = Path(dist.locate_file(f))
        name = p.name
        rel = str(f)
        if any(rx.match(name) or rx.match(rel) for rx in LICENSE_REGEXES):
            if p.is_file():
                candidates.append(p)

    # PEP 639: License-File / License-Files
    try:
        meta = dist.metadata
        for key in ("License-File", "License-Files"):
            vals = meta.get_all(key) or []
            for v in vals:
                p = Path(dist.locate_file(v))
                if p.is_file() and p not in candidates:
                    candidates.append(p)
    except Exception:
        pass

    # 휴리스틱
    root = Path(dist.locate_file(""))
    for pat in ["LICENSE", "LICENSE.txt", "COPYING", "NOTICE", "LICENSE.md"]:
        p = root / pat
        if p.is_file() and p not in candidates:
            candidates.append(p)

    return candidates

def normalize_pkg_name(name: str) -> str:
    return name.replace(" ", "-").replace("_", "-")

def should_exclude_file_for_pkg(pkg_name_lower: str, path: Path) -> bool:
    if pkg_name_lower in LGPL_CHOICE_PACKAGES:
        rel = path.as_posix()
        base = path.name
        for rx in EXCLUDE_REGEXES:
            if rx.match(base) or rx.match(rel):
                return True
    return False

def prefer_sort_key_for_pkg(pkg_name_lower: str, path: Path):
    rel = path.as_posix()
    base = path.name
    prefer_score = 0
    if pkg_name_lower in LGPL_CHOICE_PACKAGES:
        for rx in PREFER_REGEXES:
            if rx.match(base) or rx.match(rel):
                prefer_score -= 10
        for rx in EXCLUDE_REGEXES:
            if rx.match(base) or rx.match(rel):
                prefer_score += 100
    return (prefer_score, base.lower())

def ensure_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def try_download(url: str, timeout=20):
    # 표준 라이브러리만 사용 (urllib) — 외부 종속 최소화
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = resp.read()
            return data.decode("utf-8", errors="replace")
    except Exception:
        return None

def fetch_lgpl_text():
    for url in LGPL_URLS:
        txt = try_download(url)
        if txt and "GNU LESSER GENERAL PUBLIC LICENSE" in txt.upper():
            return txt
    return None

# ------------------------------ 메인 처리 ------------------------------
rows = []
seen = set()
lgpl_cached = None  # 한 번 내려받은 LGPL 전문 캐시
lgpl_common_written = False  # 루트 LGPL 사본 저장 여부

for dist in metadata.distributions():
    name = dist.metadata.get("Name") or dist.metadata.get("name") or "UNKNOWN"
    version = dist.version or "UNKNOWN"
    key = (name.lower(), version)
    if key in seen:
        continue
    seen.add(key)

    homepage = (dist.metadata.get("Home-page") or
                dist.metadata.get("Project-URL") or "")
    license_decl = dist.metadata.get("License") or ""
    license_expr = dist.metadata.get("License-Expression") or ""
    classifiers = dist.metadata.get_all("Classifier") or []
    classifier_guess = guess_license_from_classifiers(classifiers)
    license_str = (license_expr or license_decl or classifier_guess or "").strip()

    author = (dist.metadata.get("Author") or dist.metadata.get("Author-email") or
              dist.metadata.get("Maintainer") or dist.metadata.get("Maintainer-email") or "")

    pkg_lower = name.lower()
    lic_files = find_candidate_license_files(dist)

    # 파일 필터링/정렬
    lic_files = [p for p in lic_files if not should_exclude_file_for_pkg(pkg_lower, p)]
    lic_files.sort(key=lambda p: prefer_sort_key_for_pkg(pkg_lower, p))

    copied_paths = []
    copy_root = LICENSES_DIR / f"{normalize_pkg_name(name)}-{version}"
    copy_root.mkdir(parents=True, exist_ok=True)

    for src in lic_files:
        try:
            dst = copy_root / src.name
            if dst.exists():
                base = src.stem
                ext = src.suffix
                i = 2
                while True:
                    alt = copy_root / f"{base}-{i}{ext}"
                    if not alt.exists():
                        dst = alt
                        break
                    i += 1
            shutil.copy2(src, dst)
            copied_paths.append(dst.relative_to(OUT_DIR).as_posix())
        except Exception:
            pass

    # PySide6 계열이고 LGPL 문서가 없다면 => 자동으로 LGPL v3 전문 내려받아 추가
    if pkg_lower in LGPL_CHOICE_PACKAGES:
        has_lgpl = any("lgpl" in Path(p).name.lower() for p in copied_paths)
        if not has_lgpl:
            # 처음 한 번만 네트워크에서 가져와 캐시
            if lgpl_cached is None:
                lgpl_cached = fetch_lgpl_text()

            if lgpl_cached:
                # 패키지별 위치에 저장
                dst_pkg = copy_root / "LGPL-3.0.txt"
                ensure_text(dst_pkg, lgpl_cached)
                copied_paths.append(dst_pkg.relative_to(OUT_DIR).as_posix())

                # 루트 공통 사본(한 번만)
                if not lgpl_common_written:
                    dst_common = LICENSES_DIR / "LGPL-3.0.txt"
                    if not dst_common.exists():
                        ensure_text(dst_common, lgpl_cached)
                    lgpl_common_written = True
            else:
                # 네트워크 실패 시 경고 파일
                warn = copy_root / "MISSING-LGPL-3.0.txt"
                ensure_text(
                    warn,
                    "LGPL v3 license text could not be fetched.\n"
                    "Please ensure internet access and re-run this script, "
                    "or manually place the LGPL v3 text in this folder as 'LGPL-3.0.txt'.\n"
                    "Recommended source: https://www.gnu.org/licenses/lgpl-3.0.txt\n"
                )
                copied_paths.append(warn.relative_to(OUT_DIR).as_posix())

    rows.append({
        "name": name,
        "version": version,
        "license": license_str,
        "author": author,
        "homepage": homepage,
        "copyleft": "YES" if is_copyleft(license_str) else "NO",
        "license_files": "; ".join(copied_paths) if copied_paths else "",
        "dual_choice": ("LGPL v3 (chosen)" if pkg_lower in LGPL_CHOICE_PACKAGES else ""),
    })

# 요약 CSV
csv_path = OUT_DIR / "licenses-summary.csv"
with csv_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name","version","license","copyleft","author","homepage","license_files","dual_choice"])
    writer.writeheader()
    for r in sorted(rows, key=lambda x: x["name"].lower()):
        writer.writerow(r)

# ThirdPartyLicenses.txt
txt_path = OUT_DIR / "ThirdPartyLicenses.txt"
with txt_path.open("w", encoding="utf-8") as f:
    f.write("# Third-Party Licenses\n\n")
    f.write("이 소프트웨어는 아래 오픈소스 패키지에 의존합니다.\n")
    f.write("각 패키지의 LICENSE 원문은 ./licenses/<패키지-버전>/ 에 포함되어 있습니다.\n\n")
    f.write("※ 주의: 'Copyleft=YES' 표시는 GPL/LGPL/MPL 등 카피레프트 계열 가능성을 의미합니다. 실제 의무는 LICENSE 원문을 확인하십시오.\n\n")

    important = {"pyside6", "pyside6-essentials", "pyside6-addons", "pyside6_addons", "certifi", "cryptography"}
    rows_sorted = sorted(rows, key=lambda x: (x["name"].lower() not in important, x["name"].lower()))

    for r in rows_sorted:
        f.write(f"## {r['name']} ({r['version']})\n")
        chosen = f"  |  Dual-License Choice: {r['dual_choice']}" if r["dual_choice"] else ""
        f.write(f"- License: {r['license'] or 'UNKNOWN'}  |  Copyleft: {r['copyleft']}{chosen}\n")
        if r["author"]:
            f.write(f"- Copyright/Author: {r['author']}\n")
        if r["homepage"]:
            f.write(f"- Homepage: {r['homepage']}\n")
        if r["license_files"]:
            f.write(f"- License files: {r['license_files']}\n")
        f.write("\n")

    f.write("\n---\n")
    f.write("### PySide6 (LGPL v3) 고지\n")
    f.write("본 배포본은 Qt for Python(PySide6) 듀얼 라이선스 중 **LGPL v3** 옵션을 선택합니다.\n")
    f.write("사용자는 LGPL v3에 따라 PySide6를 교체할 권리가 있습니다.\n")
    f.write("LGPL v3 원문은 ./licenses/LGPL-3.0.txt 또는 각 패키지 폴더의 LGPL-3.0.txt에서 확인할 수 있습니다.\n")
    f.write("원문 출처: https://www.gnu.org/licenses/lgpl-3.0.txt\n\n")

    f.write("### certifi (MPL 2.0) 고지\n")
    f.write("certifi를 수정한 경우 해당 수정 파일에 한하여 MPL 2.0에 따라 소스 공개 의무가 있습니다. 수정하지 않았다면 고지로 충분합니다.\n")

print(f"[OK] Created: {txt_path}")
print(f"[OK] Created: {csv_path}")
print(f"[OK] Licenses copied under: {LICENSES_DIR}")
