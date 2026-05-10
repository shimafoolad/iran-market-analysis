# 📊 تحلیل داده‌های بازار ایران — پروژه مشارکتی

> پروژه کلاسی تحلیل داده | مشارکت از طریق Fork / Branch / Pull Request

این مخزن، مرکز مشترک پروژه‌های تحلیل داده دانشجویان است. هر دانشجو یک سناریوی واقعی (مثل قیمت خودرو، موبایل، یا اجاره مسکن) را انتخاب کرده، داده‌های آن را از وب استخراج می‌کند، پاک‌سازی و تحلیل می‌کند و نتایج را در یک Pull Request ارسال می‌کند.

---

## 🗺️ ساختار مخزن

```
iran-market-analysis/
├── README.md               ← همین فایل
├── CONTRIBUTING.md         ← راهنمای کامل fork / branch / PR
├── projects/
│   ├── _example/           ← نمونه ساختار (اینجا را ببینید!)
│   │   ├── notebook.ipynb
│   │   ├── dataset_sample.json
│   │   ├── scrape_divar.py
│   │   └── README.md
│   └── [نام-شما]/          ← پوشه شما اینجا اضافه می‌شود
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

---

## 🚀 شروع سریع

1. این مخزن را **Fork** کنید (دکمه Fork بالا-راست)
2. در مخزن Fork شده خود یک **Branch** با نام `analysis/نام-موضوع` بسازید
3. پوشه‌ای با ساختار `projects/_example/` برای خودتان بسازید
4. فایل‌هایتان را آپلود و **Commit** کنید
5. یک **Pull Request** به این مخزن باز کنید

📖 **راهنمای کامل:** [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📋 پروژه‌های دانشجویان

| دانشجو | موضوع تحلیل | منبع داده | وضعیت | لینک PR |
|--------|-------------|-----------|--------|---------|
| _نمونه_ | قیمت پژو ۲۰۷ دست دوم | دیوار | ✅ Merged | [#0]() |
| | | | | |
| | | | | |

> پس از Merge شدن PR شما، ردیف خودتان را در این جدول اضافه کنید.

---

## 🛠️ ابزارهای مورد استفاده

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.x-green)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-scraping-orange)
![Requests](https://img.shields.io/badge/Requests-scraping-orange)
![Matplotlib](https://img.shields.io/badge/Matplotlib-visualization-red)
![Jupyter](https://img.shields.io/badge/Jupyter-notebook-yellow)

---

## ⚖️ قوانین مشارکت

- هر دانشجو فقط در پوشه خودش تغییر ایجاد می‌کند
- هیچ‌وقت مستقیم روی `main` کار نکنید
- پیام‌های Commit باید توضیح‌دهنده باشند
- حداقل ۵۰۰ سطر داده در فایل json یا CSV
