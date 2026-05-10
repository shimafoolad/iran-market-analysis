"""
scrape_divar.py
---------------
استخراج آگهی‌های خودرو از سایت دیوار با استفاده از API داخلی

⚠️  این فایل را حتماً روی سیستم خودتان (Local) اجرا کنید — نه در Google Colab.
    سایت‌های ایرانی دسترسی IP های خارجی را مسدود می‌کنند.

نحوه اجرا:
    python scrape_divar.py

خروجی:
    divar_listings.csv   ← فایل اصلی برای آپلود در Google Drive
    divar_listings.json  ← نسخه پشتیبان JSON
"""

import requests
import json
import time
import re
import csv
from pathlib import Path


# ─────────────────────────────────────────────
#  تنظیمات اصلی — اینجا را تغییر دهید
# ─────────────────────────────────────────────

CITIES = {
    "تهران":  "1",
    "مشهد":  "3",
    # شهرهای دیگر را اینجا اضافه کنید:
    # "اصفهان": "4",
    # "شیراز":  "8",
}

QUERY                 = "207"       # کلمه جستجو
PRODUCTION_YEAR_START = 1401        # از مدل سال
PRODUCTION_YEAR_END   = 1404        # تا مدل سال
MAX_PAGES_PER_CITY    = 10          # تعداد صفحات هر شهر (هر صفحه ~۲۴ آگهی)
SLEEP_BETWEEN_PAGES   = 1.5        # ثانیه تأخیر بین درخواست‌ها (احترام به سرور)

OUTPUT_CSV  = "divar_listings.csv"
OUTPUT_JSON = "divar_listings.json"


# ─────────────────────────────────────────────
#  توابع کمکی
# ─────────────────────────────────────────────

def persian_to_english(text: str) -> str:
    """تبدیل اعداد فارسی و عربی به انگلیسی"""
    if not isinstance(text, str):
        return text
    for fa, ar, en in zip("۰۱۲۳۴۵۶۷۸۹", "٠١٢٣٤٥٦٧٨٩", "0123456789"):
        text = text.replace(fa, en).replace(ar, en)
    return text


def parse_price(raw: str) -> int | None:
    """
    تبدیل رشته قیمت به عدد صحیح (تومان)
    مثال: '۸۵۰٬۰۰۰٬۰۰۰ تومان' → 850000000
           'توافقی' → None
    """
    if not raw:
        return None
    raw = persian_to_english(raw)
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def parse_subtitle(subtitle: str) -> tuple[int | None, int | None]:
    """
    استخراج سال ساخت و کارکرد از ستون subtitle
    مثال: '۱۴۰۳، ۴۵٬۰۰۰ کیلومتر' → (1403, 45000)
    """
    if not subtitle:
        return None, None

    subtitle = persian_to_english(subtitle)

    # استخراج سال (عدد ۴ رقمی بین ۱۳۸۰ تا ۱۴۱۰)
    year_match = re.search(r"\b(1[34]\d{2})\b", subtitle)
    year = int(year_match.group(1)) if year_match else None

    # استخراج کارکرد (عدد قبل از کلمه کیلومتر)
    mileage_match = re.search(r"([\d,،]+)\s*کیلومتر", subtitle)
    if mileage_match:
        mileage = int(re.sub(r"[^\d]", "", mileage_match.group(1)))
    else:
        mileage = None

    return year, mileage


# ─────────────────────────────────────────────
#  تابع اصلی scraping
# ─────────────────────────────────────────────

def scrape_city(city_name: str, city_id: str) -> list[dict]:
    """
    استخراج آگهی‌های یک شهر از دیوار
    برمی‌گرداند: لیستی از دیکشنری (هر آگهی یک سطر)
    """
    base_url = "https://api.divar.ir/v8/postlist/w/search"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://divar.ir",
        "Referer": "https://divar.ir/",
    }

    payload = {
        "city_ids": [city_id],
        "pagination_data": {
            "@type": "type.googleapis.com/post_list.PaginationData",
            "last_post_date": None,
            "page": 1,
            "layer_page": 1,
        },
        "search_data": {
            "form_data": {
                "data": {
                    "category": {"str": {"value": "light"}},
                    "q": {"str": {"value": QUERY}},
                    "production-year": {
                        "number_range": {
                            "minimum": PRODUCTION_YEAR_START,
                            "maximum": PRODUCTION_YEAR_END,
                        }
                    },
                }
            }
        },
    }

    listings = []

    for page in range(1, MAX_PAGES_PER_CITY + 1):
        print(f"  [{city_name}] صفحه {page}/{MAX_PAGES_PER_CITY} ...", end=" ")
        payload["pagination_data"]["page"] = page

        try:
            response = requests.post(base_url, headers=headers, json=payload, timeout=15)
        except requests.RequestException as e:
            print(f"\n  ⚠️  خطای اتصال: {e}")
            break

        if response.status_code != 200:
            print(f"\n  ⚠️  کد خطا: {response.status_code}")
            break

        data = response.json()
        widgets = data.get("list_widgets", [])

        if not widgets:
            print("پایان آگهی‌ها.")
            break

        page_count = 0
        for widget in widgets:
            if widget.get("widget_type") != "POST_ROW":
                continue

            post  = widget.get("data", {})
            web   = post.get("action", {}).get("payload", {}).get("web_info", {})

            raw_price    = post.get("middle_description_text", "")
            raw_subtitle = post.get("top_description_text", "")

            price         = parse_price(raw_price)
            year, mileage = parse_subtitle(raw_subtitle)

            # آگهی‌های توافقی (price=None) را نگه می‌داریم و در Cleaning حذف می‌شوند
            listing = {
                "title":        post.get("title", ""),
                "year":         year,
                "mileage_km":   mileage,
                "price_toman":  price,
                "price_raw":    raw_price,
                "city":         city_name,                    # از دیکشنری CITIES
                "district":     web.get("district_persian", ""),
                "token":        post.get("token", ""),
                "url":          f"https://divar.ir/v/{post.get('token', '')}",
            }
            listings.append(listing)
            page_count += 1

        print(f"{page_count} آگهی دریافت شد.")

        # توکن صفحه بعد
        last_date = data.get("pagination_data", {}).get("last_post_date")
        if last_date:
            payload["pagination_data"]["last_post_date"] = last_date

        time.sleep(SLEEP_BETWEEN_PAGES)

    return listings


# ─────────────────────────────────────────────
#  ذخیره خروجی
# ─────────────────────────────────────────────

def save_csv(listings: list[dict], path: str) -> None:
    if not listings:
        print("هیچ داده‌ای برای ذخیره وجود ندارد.")
        return
    fieldnames = listings[0].keys()
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(listings)
    print(f"✅ فایل CSV ذخیره شد: {Path(path).resolve()}")


def save_json(listings: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    print(f"✅ فایل JSON ذخیره شد: {Path(path).resolve()}")


# ─────────────────────────────────────────────
#  اجرای اصلی
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print(f"  استخراج آگهی‌های «{QUERY}» از دیوار")
    print(f"  مدل سال: {PRODUCTION_YEAR_START} تا {PRODUCTION_YEAR_END}")
    print(f"  شهرها: {', '.join(CITIES.keys())}")
    print("=" * 55)

    all_listings = []

    for city_name, city_id in CITIES.items():
        print(f"\n📍 شهر: {city_name}")
        city_data = scrape_city(city_name, city_id)
        all_listings.extend(city_data)
        print(f"  جمع آگهی‌های {city_name}: {len(city_data)}")

    print(f"\n{'─'*55}")
    print(f"  مجموع کل آگهی‌ها: {len(all_listings)}")
    print(f"{'─'*55}\n")

    save_csv(all_listings, OUTPUT_CSV)
    save_json(all_listings, OUTPUT_JSON)

    print(f"\n📌 مرحله بعد:")
    print(f"   فایل «{OUTPUT_CSV}» را در Google Drive آپلود کنید")
    print(f"   سپس notebook.ipynb را در Google Colab باز کنید.")
