# 🔧 Database Connection Fix

## ✅ Issue Fixed!

The database password contained `@` which needed to be URL-encoded.

### Problem:
```
DATABASE_URL=postgresql://postgres:YOUR_DB_PASSWORD@db.YOUR_SUPABASE_PROJECT_ID.supabase.co:5432/postgres
```
The `@` in the password was being interpreted as the separator between credentials and hostname.

### Solution:
URL-encode the `@` as `%40`:
```
DATABASE_URL=postgresql://postgres:YOUR_DB_PASSWORD@db.YOUR_SUPABASE_PROJECT_ID.supabase.co:5432/postgres
```

## ✅ psycopg2 Installed

The PostgreSQL driver (`psycopg2-binary`) has been installed and added to `requirements.txt`.

## 🧪 Test Connection

```bash
python -c "from app import app, db; app.app_context().push(); from models import Call; print(f'✅ Connected! Calls: {Call.query.count()}')"
```

## 📝 Special Characters in Passwords

If your database password contains special characters, URL-encode them:
- `@` → `%40`
- `#` → `%23`
- `%` → `%25`
- `&` → `%26`
- `+` → `%2B`
- `=` → `%3D`

---

**Database connection is now fixed!** ✅




