"""FRY FUEL - PyScript logic.

Every function decorated with @when(...) is an EVENT HANDLER:
the browser fires an event (click, input, change, submit) and
PyScript calls the matching Python function.
"""
import random
from datetime import datetime

from js import setTimeout, setInterval, window
from pyodide.ffi import create_proxy
from pyscript import document, when

from menu import (
    MENU, PROMOS, DELIVERY_FEE, CURRENCY, OPEN_HOUR, CLOSE_HOUR, SIZES, ADDONS,
)

# ---------- Application state ----------
ITEMS = {item["id"]: item for item in MENU}
ADDON_BY_ID = {a["id"]: a for a in ADDONS}
# cart: line key -> {"id": item id, "size": size name, "addons": [addon ids], "qty": int}
cart = {}
state = {"category": "All", "search": "", "promo": None, "mode": "Pickup"}


# ---------- Helpers ----------
def el(element_id):
    return document.getElementById(element_id)


def money(value):
    return f"{CURRENCY}{value:,.2f}"


def toast(message):
    box = el("toast")
    box.textContent = message
    box.classList.add("show")
    setTimeout(create_proxy(lambda: box.classList.remove("show")), 2200)


def customizable(item):
    """Food gets size and add-ons. Drinks do not."""
    return item["category"] != "Drinks"


def unit_price(item_id, size, addon_ids):
    item = ITEMS[item_id]
    price = item["price"]
    if customizable(item):
        price += SIZES[size]
        price += sum(ADDON_BY_ID[a]["price"] for a in addon_ids)
    return price


def line_key(item_id, size, addon_ids):
    return f"{item_id}|{size}|{','.join(sorted(addon_ids))}"


def line_label(line):
    item = ITEMS[line["id"]]
    if not customizable(item):
        return item["name"]
    text = f"{item['name']} ({line['size']})"
    if line["addons"]:
        text += " + " + ", ".join(ADDON_BY_ID[a]["name"] for a in line["addons"])
    return text


def totals():
    subtotal = sum(
        unit_price(l["id"], l["size"], l["addons"]) * l["qty"] for l in cart.values()
    )
    discount = subtotal * PROMOS.get(state["promo"], 0)
    fee = DELIVERY_FEE if (state["mode"] == "Delivery" and cart) else 0
    return subtotal, discount, fee, subtotal - discount + fee


def size_options():
    out = ""
    for name, extra in SIZES.items():
        label = name if extra == 0 else f"{name} (+{CURRENCY}{extra})"
        out += f'<option value="{name}">{label}</option>'
    return out


def addon_boxes():
    return "".join(
        f'<label class="addon"><input type="checkbox" value="{a["id"]}"> '
        f'{a["name"]} <em>+{CURRENCY}{a["price"]}</em></label>'
        for a in ADDONS
    )


def custom_html(item):
    if not customizable(item):
        return ""
    return (
        '<div class="custom">'
        f'<label class="size-row">Size <select class="size">{size_options()}</select></label>'
        f'<fieldset class="addons"><legend>Add-ons</legend>{addon_boxes()}</fieldset>'
        "</div>"
    )


def read_choice(card):
    """Read the size and add-ons currently selected on a menu card."""
    item_id = card.dataset.id
    size_box = card.querySelector(".size")
    size = size_box.value if size_box else "Regular"
    addons = sorted(box.value for box in card.querySelectorAll(".addon input:checked"))
    return item_id, size, addons


def refresh_card_price(card):
    item_id, size, addons = read_choice(card)
    card.querySelector(".price").textContent = money(unit_price(item_id, size, addons))


# ---------- Rendering (dynamic page updates) ----------
def render_menu():
    query = state["search"].lower()
    shown = [
        m for m in MENU
        if (state["category"] == "All" or m["category"] == state["category"])
        and (query in m["name"].lower() or query in m["desc"].lower())
    ]
    if not shown:
        el("menu-grid").innerHTML = '<p class="empty">No match. Try another word or pick All.</p>'
        return
    el("menu-grid").innerHTML = "".join(
        f'''<article class="card" data-id="{m["id"]}">
              <div class="pic">{m["emoji"]}</div>
              <div class="body">
                {f'<span class="tag">{m["tag"]}</span>' if m["tag"] else ''}
                <h3>{m["name"]}</h3>
                <p>{m["desc"]}</p>
                {custom_html(m)}
                <div class="row">
                  <span class="price">{money(m["price"])}</span>
                  <button class="btn small add">Add to box</button>
                </div>
              </div>
            </article>'''
        for m in shown
    )


def render_cart():
    el("cart-count").textContent = str(sum(l["qty"] for l in cart.values()))

    if not cart:
        el("cart-items").innerHTML = '<p class="empty">Your box is empty. Add something from the menu.</p>'
    else:
        rows = ""
        for key, line in cart.items():
            price = unit_price(line["id"], line["size"], line["addons"])
            rows += f'''<div class="line">
                  <div><strong>{ITEMS[line["id"]]["emoji"]} {line_label(line)}</strong>
                       <span>{money(price)} each</span></div>
                  <div class="qty">
                    <button data-act="dec" data-key="{key}" aria-label="Remove one">-</button>
                    <b>{line["qty"]}</b>
                    <button data-act="inc" data-key="{key}" aria-label="Add one">+</button>
                  </div>
                  <div class="line-total">{money(price * line["qty"])}</div>
                </div>'''
        el("cart-items").innerHTML = rows

    subtotal, discount, fee, total = totals()
    el("t-sub").textContent = money(subtotal)
    el("t-disc").textContent = "-" + money(discount)
    el("t-fee").textContent = money(fee)
    el("t-total").textContent = money(total)
    el("row-discount").hidden = discount == 0
    el("row-fee").hidden = fee == 0


def update_status():
    hour = datetime.now().hour
    is_open = OPEN_HOUR <= hour < CLOSE_HOUR
    badge = el("open-status")
    badge.textContent = (
        f"Open now until {CLOSE_HOUR - 12}:00 pm" if is_open
        else f"Closed right now. We open at {OPEN_HOUR}:00 am"
    )
    badge.classList.toggle("closed", not is_open)


# ---------- EVENT HANDLERS ----------
@when("click", "#menu-grid")
def on_menu_click(event):
    """Click event (delegated): 'Add to box' uses the size and add-ons chosen on that card."""
    button = event.target.closest(".add")
    if not button:
        return
    item_id, size, addons = read_choice(button.closest(".card"))
    key = line_key(item_id, size, addons)
    if key in cart:
        cart[key]["qty"] += 1
    else:
        cart[key] = {"id": item_id, "size": size, "addons": addons, "qty": 1}
    render_cart()
    toast(f"{ITEMS[item_id]['name']} added")


@when("change", "#menu-grid")
def on_option_change(event):
    """Change event (delegated): picking a size or add-on updates that card's price."""
    card = event.target.closest(".card")
    if card:
        refresh_card_price(card)


@when("click", ".chip")
def on_category_click(event):
    """Click event: filter the menu by category."""
    state["category"] = event.currentTarget.dataset.cat
    for chip in document.querySelectorAll(".chip"):
        chip.classList.toggle("active", chip.dataset.cat == state["category"])
    render_menu()


@when("input", "#search")
def on_search(event):
    """Input event: runs on every keystroke."""
    state["search"] = event.target.value.strip()
    render_menu()


@when("click", "#cart-items")
def on_cart_click(event):
    """Click event (delegated): the + and - quantity buttons."""
    button = event.target.closest("button")
    if not button:
        return
    key, action = button.dataset.key, button.dataset.act
    if action == "inc":
        cart[key]["qty"] += 1
    elif action == "dec":
        cart[key]["qty"] -= 1
        if cart[key]["qty"] <= 0:
            del cart[key]
    render_cart()


@when("click", "#apply-promo")
def on_apply_promo(event):
    """Click event: validate a promo code and recalculate totals."""
    code = el("promo").value.strip().upper()
    note = el("promo-msg")
    if code in PROMOS:
        state["promo"] = code
        note.textContent = f"Code {code} applied: {int(PROMOS[code] * 100)}% off."
        note.className = "note ok"
    else:
        state["promo"] = None
        note.textContent = "That code isn't valid. Check the spelling and try again." if code else ""
        note.className = "note bad"
    render_cart()


@when("change", "#order-mode")
def on_mode_change(event):
    """Change event: switch pickup/delivery, show the address field, add the fee."""
    state["mode"] = event.target.value
    el("address-field").hidden = state["mode"] != "Delivery"
    render_cart()


@when("click", "#clear-cart")
def on_clear(event):
    """Click event: empty the box."""
    cart.clear()
    render_cart()
    toast("Box emptied")


@when("submit", "#checkout-form")
def on_checkout(event):
    """Submit event: validate the form and confirm the order."""
    event.preventDefault()
    error = el("form-error")
    name = el("cust-name").value.strip()
    phone = el("cust-phone").value.strip()
    address = el("cust-address").value.strip()
    digits = "".join(ch for ch in phone if ch.isdigit())

    if not cart:
        error.textContent = "Your box is empty. Add something from the menu first."
    elif len(name) < 2:
        error.textContent = "Please enter your name."
    elif len(digits) < 10:
        error.textContent = "Enter a mobile number with at least 10 digits."
    elif state["mode"] == "Delivery" and len(address) < 6:
        error.textContent = "Please enter your delivery address."
    else:
        error.textContent = ""
        order_no = f"FF-{random.randint(1000, 9999)}"
        total = totals()[3]
        count = sum(l["qty"] for l in cart.values())
        el("confirm-title").textContent = f"Order {order_no} placed!"
        el("confirm-text").textContent = (
            f"Thanks, {name}. {count} item(s), total {money(total)}, for {state['mode'].lower()}. "
            "We're frying it now."
        )
        el("confirm").hidden = False
        cart.clear()
        state["promo"] = None
        el("promo").value = ""
        el("promo-msg").textContent = ""
        el("checkout-form").reset()
        render_cart()
        toast("Order placed")


# ---------- Ad slideshow ----------
slides = document.querySelectorAll(".slide")
dots = document.querySelectorAll(".dot")
slide_state = {"i": 0}


def show_slide(index):
    slide_state["i"] = index % len(slides)
    for n, slide in enumerate(slides):
        slide.classList.toggle("active", n == slide_state["i"])
    for n, dot in enumerate(dots):
        dot.classList.toggle("active", n == slide_state["i"])


@when("click", ".dot")
def on_dot_click(event):
    """Click event: jump to the chosen offer."""
    show_slide(int(event.currentTarget.dataset.i))


# Timer event: advance every 5 seconds (skipped if the visitor prefers reduced motion)
if not window.matchMedia("(prefers-reduced-motion: reduce)").matches:
    setInterval(create_proxy(lambda: show_slide(slide_state["i"] + 1)), 5000)


# ---------- Start up ----------
render_menu()
render_cart()
update_status()
