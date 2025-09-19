# FlowMarket — Full Site (Integrated, Production Ready)

## نشر على Render (Blueprint)
1) ارفع محتويات هذا المجلد إلى GitHub (الجذر يحتوي `render.yaml`).
2) Render → New → Blueprint → اختر الريبو.
3) أضف متغير:
   - `IMGBB_API_KEY=<مفتاحك>`

## فحص سريع
- `/healthz` — صحة الخدمة.
- `/db-ping` — اتصال قاعدة البيانات.
- `/uploader` — واجهة رفع صور.
- `/upload` — API رفع صور إلى ImgBB.
- `/auth/health` — فحص المصادقة.

## ملاحظات
- تم تنظيف ملفات حساسة (cookies/logs).
- تم حقن مسارات فحص وإضافات Auto-Register تلقائيًا.