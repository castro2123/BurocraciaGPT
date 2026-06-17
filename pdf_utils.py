def highlight_text(context, query):

    words = query.lower().split()
    highlights = []

    for chunk in context.split("\n"):
        if any(w in chunk.lower() for w in words):
            highlights.append(chunk)

    return highlights[:8]