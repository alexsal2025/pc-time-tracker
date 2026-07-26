# PC Time Tracker

متعقّب خفيف لوقت استخدام الحاسوب على نظام Windows. يحسب الوقت الذي تقضيه أمام الجهاز، مع إيقاف تلقائي عند الخمول، وهدف يومي قابل للضبط، وسجلّ لآخر 7 أيام.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## الميزات

- 🕒 مؤقّت كبير للجلسة الحالية + مجموع وقت اليوم
- ⏸ أزرار **بدء / إيقاف مؤقت / إعادة ضبط**
- 😴 **إيقاف تلقائي** عند الخمول — يمكن ضبط العتبة (10…3600 ثانية)
- 🎯 **هدف يومي** قابل للضبط (1–24 ساعة) مع شريط تقدّم
- 📊 **سجل 7 أيام** مع أشرطة تقدّم لكل يوم
- 🪟 خيار "دائمًا في الأعلى"
- 💾 حفظ تلقائي كل 10 ثوانٍ وعند الإغلاق — تستمر الجلسات بعد إعادة التشغيل
- 🎨 ثيم داكن، وخطوط Consolas / Segoe UI
- 🌐 **10 لغات للواجهة** — [English (default)](./README.md), [Русский](./ru.md), [中文](./zh.md), [Español](./es.md), [Français](./fr.md), [Deutsch](./de.md), [Português](./pt.md), [日本語](./ja.md), [한국어](./ko.md), [العربية](./ar.md)

## لقطة الشاشة

![PC Time Tracker](screenshots/ar.png)

## التثبيت والتشغيل

يتطلّب **Python 3.10+** مع وحدة `tkinter` (مضمّنة افتراضيًا في Windows).

```bash
python src/pc_time_tracker.py
```

النقر المزدوج يعمل أيضًا، إذا كانت ملفات `.py` مربوطة ببرنامج Python.

## أين تُحفظ البيانات

جميع الإعدادات والسجلّ محفوظة في ملف JSON واحد:

```
%APPDATA%\PCTimeTracker\data.json
```

## الرخصة

MIT
