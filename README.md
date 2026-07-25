# Reply Tracker

#### Video Demo: https://youtu.be/WkqX6y5o-_w

#### Description:

Reply Tracker is a web application built with Flask, SQLite, and Bootstrap that helps
users keep track of who they still owe a reply to. The idea came from a personal,
everyday problem: it's easy to lose track of who has messaged you and
who you still need to get back to, especially across a busy group of family and
friends. Reply Tracker solves this by letting a user log every contact's last
interaction with a single click, and surfaces anyone who has been waiting more
than 24 hours for a reply right at the top of the dashboard.

The application is a personal contact-management tool rather than a messaging
app itself — it does not connect to WhatsApp or any other messaging service.
Instead, the user manually logs each interaction ("They messaged me" / "I
replied"), and the app handles the rest: calculating how long it's been,
flagging anyone who is overdue, and sorting the dashboard so the
longest-waiting contact always appears first.

## Features

- **Accounts.** Users register with a username and password. Passwords are
  hashed with Werkzeug's `generate_password_hash` before being stored, and
  usernames are enforced as unique via a `UNIQUE INDEX` in the database.
- **Dashboard.** After logging in, the user sees every contact they've added,
  sorted so the contact who has gone longest without a reply appears first.
  Each contact is shown as a card with their name, how many hours have passed
  since the last interaction, and a colored status badge — green for "On
  Track", red for "Overdue" (24+ hours since they last messaged and the user
  hasn't replied yet).
- **Quick logging.** Each contact card has two buttons: "They messaged me" and
  "I replied." Clicking either instantly updates that contact's status and
  timestamp, with no extra typing required — this was a deliberate design
  choice, since a tracker that requires effort to use quickly falls out of use.
- **Adding and deleting contacts.** Users can add new contacts via a simple
  form, and remove individual contacts they no longer want to track via a
  "Delete" button on each contact card, protected by a confirmation dialog
  that names the contact so the user knows exactly who they're about to
  remove, preventing accidental deletion.
- **Account deletion.** Users can permanently delete their account and all
  associated contacts, again behind a confirmation dialog, since this action
  is irreversible.
- **Flash messages.** JavaScript's `confirm()` dialog and Flask's `flash()`
  messaging are both used to make destructive or important actions clearer to
  the user — confirming before deletion, and giving feedback ("Marked as
  replied!") after logging an interaction.

## File Structure

- `app.py` — All Flask routes and application logic:
  - `register` / `login` / `logout` — account creation and session handling.
  - `index` (`/`) — builds the dashboard: queries all of the logged-in user's
    contacts, calculates hours since last contact for each one, flags overdue
    contacts, and sorts the list so the most overdue contact appears first.
  - `add` (`/add`) — form to add a new contact, defaulting their status to
    "from_me" so a freshly added contact doesn't immediately appear overdue.
  - `update` (`/update/<contact_id>`) — a single route, parameterized by a
    `direction` field, that handles both "They messaged me" and "I replied"
    button presses. Chose to merge these into one route rather than two
    near-identical ones, since the only real difference between them is which
    value gets written to the database. Only the "I replied" branch resets
    `last_timestamp` to the current time; "They messaged me" only flips
    `last_direction`, since the clock should measure how long a contact has
    been waiting for a reply, not how long since any interaction at all.
  - `delete_contact` (`/delete_contact/<contact_id>`) — removes a single
    contact via a "Delete" button on its card, scoped to the logged-in user
    so one user cannot delete another user's contacts by guessing IDs. Backed
    by a confirmation dialog naming the contact, to prevent accidental
    deletion.
  - `delete_account` (`/delete_account`) — deletes the logged-in user's
    account along with all of their contacts, in that order, to avoid leaving
    orphaned rows behind.
- `reply_tracker.db` — SQLite database with two tables:
  - `users` — `id`, `username`, `hash`, with a unique index on `username`.
  - `contacts` — `id`, `user_id` (foreign key to `users`), `name`,
    `last_direction` (`"from_them"` or `"from_me"`), `last_timestamp`.
- `templates/` — Jinja templates: `layout.html` (shared navbar, flash
  messages, and page structure), `index.html` (the dashboard), `add.html`,
  `register.html`, `login.html`.
- `static/styles.css` — custom styling: a card-based layout for contacts
  (rather than a plain table), a color palette defined with CSS variables, and
  a colored left border on each card to make overdue status visible at a
  glance.
- `helpers.py` — `apology()` and `login_required()`, used across the app for
  error handling and route protection.

## Design Choices

A few decisions were made along the way that are worth explaining:

- **One `contacts` table instead of a separate interaction log.** An earlier
  design considered a second table recording every individual interaction, to
  support a future "history" view. Since the current scope is a dashboard
  only, with no history page, each contact's row is simply overwritten with
  their most recent interaction. This keeps the schema and the queries much
  simpler, at the cost of not retaining history — a reasonable trade-off given
  the app's current scope, and one that could be revisited if a history
  feature were added later.
- **Login was added even though this is a personal, single-user tool**,
  specifically to reflect the account/session-handling skills covered in the
  course, and to leave the door open for the app to be used by more than one
  person in the future without a redesign.
- **The overdue threshold is fixed at 24 hours** rather than configurable per
  contact, to keep the first version of the app simple. A natural extension
  would be letting users set a custom threshold per contact.

## How to run

1. Install dependencies: `pip install flask cs50 flask-session werkzeug`
2. Ensure `reply_tracker.db` exists in the same directory as `app.py`, with
   the `users` and `contacts` tables created.
3. Run `flask run` and open the address shown in the terminal.
