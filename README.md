# FRY FUEL

A French fries business website built with **PyScript** for our Event-Driven Programming final project.

## Files

| File | Role |
|---|---|
| `index.html` | Front end: page structure |
| `style.css` | Front end: design |
| `main.py` | PyScript: all event handlers and page updates |
| `menu.py` | Business data: menu, prices, promo codes, hours |
| `pyscript.toml` | PyScript config |

## Run it locally

PyScript must load files over HTTP, so don't just double-click `index.html`.

```
python -m http.server 8000
```

Then open http://localhost:8000. (VS Code "Live Server" also works.)

## Publish it (GitHub Pages)

Repo > Settings > Pages > Deploy from a branch > `main` / root.

## Event-driven features

| Event | What happens |
|---|---|
| `click` | Add to box, change quantity, filter categories, apply promo, empty box |
| `input` | Live menu search while typing |
| `change` | Pickup/Delivery switch shows the address field and adds the fee |
| `submit` | Order form validation and confirmation |

Promo codes to try: `FUEL10`, `FIRSTBOX`.

## Team contributions

| Member | Part |
|---|---|
| Member 1 | (example) `index.html` structure |
| Member 2 | (example) `style.css` design |
| Member 3 | (example) `main.py` cart and promo logic |
| Member 4 | (example) `menu.py`, README, video |
