import sys, platform, importlib, json

modules = [
    # core project deps we expect
    "django",
    "whitenoise",
    "gunicorn",
    "dj_database_url",
    "psycopg2",           # may be provided by psycopg2-binary
    "psycopg2_binary",    # alias often exposed by psycopg2-binary
    "PIL",                # Pillow
]

results = {}
for m in modules:
    try:
        importlib.import_module(m)
        results[m] = "OK"
    except Exception as e:
        results[m] = f"ERROR: {e.__class__.__name__}: {e}"

print("=== Python Environment ===")
print("Python:", sys.version)
print("Machine:", platform.machine())
print("Platform:", platform.platform())
print("Prefix:", sys.prefix)
print()

print("=== Import Results ===")
for k, v in results.items():
    print(f"{k:18} : {v}")

# Optional: check Django settings import
print()
print("=== Django sanity ===")
try:
    import django
    from django.conf import settings
    print("Django version:", django.get_version())
    # Don't configure settings here; we only verify the package is importable.
except Exception as e:
    print("Django import failed:", repr(e))
