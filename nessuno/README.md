# Nessuno

A simple static website for photo collections.

This folder is separate from the existing academic website. It does not require Quarto, npm, or a build step.

## Rebuild collections

The source folder is:

```text
C:\Users\User\Dropbox\Foto\Best Pics
```

Each direct child folder is treated as one collection. To rebuild the web-ready images and collection data:

```powershell
python tools\build_collections.py
```

The script writes optimized JPEGs to `photos/` and updates `assets/collections.js`.

## Preview

Serve this folder with a local static server:

```powershell
python -m http.server 8001 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8001/`.
