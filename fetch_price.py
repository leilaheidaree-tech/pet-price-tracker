# اسکریپت خواندن خودکار قیمت رزین PET از کانال عمومی تلگرام
# این اسکریپت صفحه‌ی پیش‌نمایش عمومی یک کانال تلگرام را می‌خواند
# (همان صفحه‌ای که بدون لاگین هم قابل مشاهده است: t.me/s/<channel>)
# و آخرین قیمت گرید مورد نظر را با یک الگوی متنی استخراج می‌کند.
#
# قبل از استفاده، دو خط مشخص‌شده با «باید عوض کنی» را با اطلاعات
# واقعی کارخونه‌تون پر کنید.

import re
import json
import os
from datetime import datetime
import requests

# باید عوض کنی: نام کاربری کانال تلگرام (بدون @)
CHANNEL_USERNAME = "Amizehaye_Polymer_Toos"

# باید عوض کنی: بخشی از متن که قبل از قیمت گرید شما می‌آید
PRODUCT_KEYWORD = "PET 781"

# فایل خروجی که تاریخچه‌ی قیمت در آن ذخیره می‌شود
OUTPUT_FILE = "price_history.json"


def fetch_channel_html(channel_username):
    # صفحه‌ی پیش‌نمایش عمومی کانال تلگرام را می‌خواند، نیازی به لاگین نیست
    url = "https://t.me/s/" + channel_username
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def extract_price(html, keyword):
    # به دنبال خطی می‌گردد که حاوی کلمه‌ی کلیدی محصول است
    # و اولین عدد بزرگ (قیمت) را از همان خط استخراج می‌کند
    messages = re.findall(r'tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
    for msg in reversed(messages):
        plain_text = re.sub(r'<[^>]+>', ' ', msg)
        if keyword in plain_text:
            numbers = re.findall(r'[\d,]{4,}', plain_text)
            if numbers:
                cleaned = numbers[0].replace(',', '')
                return float(cleaned)
    return None


def load_history(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(path, history):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    html = fetch_channel_html(CHANNEL_USERNAME)
    price = extract_price(html, PRODUCT_KEYWORD)

    if price is None:
        print("قیمتی با این کلیدواژه پیدا نشد. کلیدواژه یا نام کانال را بررسی کنید.")
        return

    history = load_history(OUTPUT_FILE)
    today = datetime.now().strftime("%Y-%m-%d")

    if history and history[-1]["date"] == today:
        history[-1]["price"] = price
    else:
        history.append({"date": today, "price": price})

    save_history(OUTPUT_FILE, history)
    print("ثبت شد: " + today + " -> " + str(price) + " تومان")


if __name__ == "__main__":
    main()
