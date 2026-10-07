# Viide: SPEC

What the app does and the rules it must keep. This file explains what the code is for.

## Purpose

Viide is Lapikud's URL shortener. Users turn long links into short ones on the app's domain, optionally with their own code, an expiry date, and a QR code. Anyone with a short link can follow it.

## People

Users authenticate with their existing FreeIPA account. The app never creates or stores passwords and keeps no user table: a user is their username, which is also how links record their owner.

| Role    | Summary                                     |
| ------- | ------------------------------------------- |
| Visitor | Follows short links                         |
| User    | Creates, lists and deletes their own links  |

Authentication goes through a client (`src/viide/app/auth/client.py`). The app uses the FreeIPA client; an LDAP client is also available.

## Links

A link has a target URL, a short code, an owner, a creation time, and optionally an expiry and a QR code (`src/viide/app/aka/links.py`).

| Field      | Rule                                                                  |
| ---------- | --------------------------------------------------------------------- |
| Target URL | An `http` or `https` URL                                              |
| Short code | 1 to 255 letters, digits, `-` or `_`; chosen by the user or generated |
| Expiry     | 1 to 3650 days from creation, or none                                 |

- Short codes are unique across all users and case-sensitive.
- A code that matches an app route, such as `login` or `links`, is reserved.
- A generated code is 7 random characters. On a collision the app tries again, up to 5 times.
- Only the owner can see a link, delete it, or give it a QR code. Anyone else's link behaves as if it does not exist.

## Redirects

`/<code>` is public. An active link redirects to its target URL; a missing or expired link returns 404. Expired links stay in their owner's list, marked as expired, until deleted.

## QR codes

- A link has at most one QR code, which encodes its short URL.
- The PNG is stored in Garage; the database keeps only its storage key.
- The bucket is private. The link list shows each image through a signed URL that lasts one hour.
- Deleting a link deletes its QR code and image.
- If two requests create a QR code for the same link at once, only one is kept.

## Errors

Link and login errors carry a message that is shown to the user as written (`src/viide/app/aka/errors.py`, `src/viide/app/auth/errors.py`). Storage failures are logged.

## Security

- Every form is CSRF protected, and every action that changes data is a POST.
- The session cookie is `SameSite=Lax` and signed with `SECRET_KEY`.

## Architecture

`src/viide/app` holds the core and the protocols (ports) it depends on. `db`, `storage` and `app/auth/clients` implement those ports, and `src/viide/web/app.py` wires them into the Flask app.

## Configuration

Settings are read from the environment or `.env` and validated at startup by `src/viide/config.py`. `DB_PASSWORD`, `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY` and `SECRET_KEY` are required; `.env.example` has a starting set.
