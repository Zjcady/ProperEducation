# One tap to start a block

Goal: one tap on your home screen starts a 15-minute timer, opens a Claude
session, and that session greets you with block 1 already started. No
deciding, no typing.

The "Start study block" routine already exists. You add its API trigger on the
web once, then build the Shortcut. About 20 minutes total, once.

## 1. Give the routine an API trigger (web, 3 minutes)

The token can only be made on the web. The app and the CLI can't do it.

1. Open **claude.ai/code/routines** and click **Start study block**.
2. Open the menu next to its name, choose **Edit**, scroll to **Select a trigger**,
   click **Add another trigger**, choose **API**, and save.
3. Open the API trigger. Copy the **URL** (it ends in `/fire`).
4. Click **Generate token** and copy it right away. It's shown once. It starts
   with `sk-ant-oat01-`.

Keep both somewhere private for the next five minutes (a note you'll delete).
The token can only start this one routine. It can't read anything. If you lose
your phone, **Regenerate** it there and the old one stops working.

## 2. iPhone: build the Shortcut (10 minutes)

Shortcuts app, **+**, name it **Start block**. Add these actions in order:

1. **Start Timer**: 15 minutes.
2. *(optional)* **Set Focus**: turn Do Not Disturb on, until timer ends.
3. **Get Contents of URL**
   - URL: the `/fire` URL you copied
   - Method: **POST**
   - Headers (tap *Add new header* three times):

     | Key | Value |
     |---|---|
     | `Authorization` | `Bearer sk-ant-oat01-...` (your token, after the word Bearer and a space) |
     | `anthropic-version` | `2023-06-01` |
     | `Content-Type` | `application/json` |

   - Request Body: **JSON**, add one Text field: key `text`, value `start block`
4. **Get Dictionary Value**: key `claude_code_session_url` from *Contents of URL*.
5. **Open URLs**: *Dictionary Value*.

Then **Share > Add to Home Screen**. Delete the note with the token.

## 2b. Android instead

Install **HTTP Shortcuts** (free, open source). New shortcut: method POST,
the `/fire` URL, the same three headers, body `{"text": "start block"}` as
JSON. Under *Response handling*, set it to open the URL found at
`claude_code_session_url`. Add a second home-screen shortcut for a 15-minute
Clock timer, or chain one with a scripting action. Put the widget on your
home screen.

## 3. Using it

Tap it. The timer starts, a session opens, and in about a minute Claude says
what block 1 is and which file to open. Do the block. When you're done, say
so in that session; the coach rates it, commits, and the phone page updates.

## Limits worth knowing

- Routines are a research preview. If a tap ever fails, open the Claude app
  and say "leetcode": same result, three more taps.
- 30 starts per hour per routine. You won't hit it.
- Each tap starts a new session. Tapping twice makes two; close the extra one.
- Starting a session uses your Claude plan's usage, like any session.
