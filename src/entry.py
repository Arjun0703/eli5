from workers import Response, WorkerEntrypoint
from pyodide.ffi import to_js
from js import Object
from urllib.parse import urlparse, parse_qs
from html import escape

MAX_TOPIC_LENGTH = 200


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # Parse the query string properly instead of splitting on "?topic="
        query = urlparse(request.url).query
        params = parse_qs(query)
        topic = (params.get("topic", ["gravity"])[0] or "gravity").strip()

        # Guard against abuse / runaway cost
        if len(topic) > MAX_TOPIC_LENGTH:
            topic = topic[:MAX_TOPIC_LENGTH]

        # Call the model, with a graceful fallback if it fails
        try:
            result = await self.env.AI.run(
                "@cf/meta/llama-3-8b-instruct",
                to_js({
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You explain things in the simplest way possible, "
                                "like talking to a 5 year old. Use short sentences, "
                                "fun analogies, and no jargon. Keep answers under 120 words."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Explain this to me like I'm 5: {topic}",
                        },
                    ]
                }, dict_converter=Object.fromEntries)
            )
            answer = result.response
        except Exception:
            answer = "Sorry, I couldn't think of an answer right now. Please try again in a moment."

        # Escape any content from outside us before putting it in HTML
        safe_topic = escape(topic)
        safe_answer = escape(answer).replace("\n", "<br>")

        html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Explain Like I'm 5</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body style="font-family: system-ui, Arial, sans-serif; max-width: 640px; margin: 50px auto; padding: 20px; color: #222;">
    <h1>Explain Like I'm 5</h1>
    <form method="GET">
      <input name="topic"
             placeholder="Enter any topic..."
             maxlength="{MAX_TOPIC_LENGTH}"
             required
             style="width: 70%; padding: 10px; font-size: 16px;"
             value="{safe_topic}" />
      <button type="submit" style="padding: 10px 20px; font-size: 16px;">Ask!</button>
    </form>
    <br>
    <div style="background: #f0f0f0; padding: 20px; border-radius: 10px; font-size: 18px; line-height: 1.6;">
      {safe_answer}
    </div>
    <p style="color:#888; font-size: 12px; margin-top: 30px;">Powered by Cloudflare Workers AI &middot; Llama 3 8B</p>
  </body>
</html>"""

        return Response(html, headers={"Content-Type": "text/html; charset=utf-8"})