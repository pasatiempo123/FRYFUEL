"""FRY FUEL - PyScript logic.

Every function decorated with @when(...) is an EVENT HANDLER:
the browser fires an event (click, input, change, submit) and
PyScript calls the matching Python function.
"""
import random
from datetime import datetime

from js import setTimeout
from pyodide.ffi import create_proxy
from pyscript import document, when

from menu import MENU, PROMOS, DELIVERY_FEE, CURRENCY, OPEN_HOUR, CLOSE_HOUR

# ---------- Application state ----------
ITEMS = {item["id"]: item for item in MENU}
cart = {}  # item id -> quantity
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


def totals():
    subtotal = sum(ITEMS[i]["price"] * q for i, q in cart.items())
    discount = subtotal * PROMOS.get(state["promo"], 0)
    fee = DELIVERY_FEE if (state["mode"] == "Delivery" and cart) else 0
    return subtotal, discount, fee, subtotal - discount + fee


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
        f'''<article class="card">
              <div class="pic">{m["emoji"]}</div>
              <div class="body">
                {f'<span class="tag">{m["tag"]}</span>' if m["tag"] else ''}
                <h3>{m["name"]}</h3>
                <p>{m["desc"]}</p>
                <div class="row">
                  <span class="price">{money(m["price"])}</span>
                  <button class="btn small add" data-id="{m["id"]}">Add to box</button>
                </div>
              </div>
            </article>'''
        for m in shown
    )


def render_cart():
    el("cart-count").textContent = str(sum(cart.values()))

    if not cart:
        el("cart-items").innerHTML = '<p class="empty">Your box is empty. Add something from the menu.</p>'
    else:
        el("cart-items").innerHTML = "".join(
            f'''<div class="line">
                  <div><strong>{ITEMS[i]["emoji"]} {ITEMS[i]["name"]}</strong>
                       <span>{money(ITEMS[i]["price"])} each</span></div>
                  <div class="qty">
                    <button data-act="dec" data-id="{i}" aria-label="Remove one">-</button>
                    <b>{q}</b>
                    <button data-act="inc" data-id="{i}" aria-label="Add one">+</button>
                  </div>
                  <div class="line-total">{money(ITEMS[i]["price"] * q)}</div>
                </div>'''
            for i, q in cart.items()
        )

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
    """Click event (delegated): any 'Add to box' button inside the menu."""
    button = event.target.closest(".add")
    if button:
        item_id = button.dataset.id
        cart[item_id] = cart.get(item_id, 0) + 1
        render_cart()
        toast(f"{ITEMS[item_id]['name']} added")


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
    item_id, action = button.dataset.id, button.dataset.act
    if action == "inc":
        cart[item_id] += 1
    elif action == "dec":
        cart[item_id] -= 1
        if cart[item_id] <= 0:
            del cart[item_id]
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
        count = sum(cart.values())
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


# ---------- Start up ----------
render_menu()
render_cart()
update_status()
