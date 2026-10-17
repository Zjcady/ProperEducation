# E3 · Design talks: explain C3 and C5 in ten minutes

**Maps to:** "Documents interface requirements" and every "walk me through something you built" question.
**You'll have at the end:** two ten-minute whiteboard talks you can give from memory, with the follow-up questions already answered once.

A design talk has five beats: the problem, the shape (draw it), the key decision and its trade-off, what changes at ten times the scale, the questions you expect. Ten minutes total, four of them on the drawing.

## Step 1 · The MCP server (C3)  (15 min)

Fill in the first talk in `TALKS.md`. Draw the shape on paper first: client, server, tools, the token check. Photograph or describe the drawing in the "shape" section. Then open a session and say "design talk C3": Claude listens for ten minutes, then asks three follow-ups and grades. Log it. Then `check`.

## Step 2 · The RAG system (C5)  (15 min)

Same for the second talk. The key decision here is chunking and the eval loop; the scale question is what breaks first at a million documents. Then rubric review and `python3 coach.py done E3`.
