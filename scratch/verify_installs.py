"""Quick verification script — checks all new dependencies are installed."""

packages = {
    "requests": "requests",
    "torch": "torch",
    "torchvision": "torchvision",
    "google.generativeai": "google-generativeai",
    "PIL": "Pillow",
}

print("=" * 50)
print("AgriPredict Dependency Verification")
print("=" * 50)

all_ok = True
for import_name, pip_name in packages.items():
    try:
        mod = __import__(import_name)
        version = getattr(mod, "__version__", "OK")
        print(f"  ✅ {pip_name:25s} → {version}")
    except ImportError:
        print(f"  ❌ {pip_name:25s} → NOT INSTALLED (run: pip install {pip_name})")
        all_ok = False

print("=" * 50)
if all_ok:
    print("🎉 All dependencies installed successfully!")
else:
    print("⚠️  Some packages missing — see above.")
print("=" * 50)
