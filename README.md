# Explain Like I'm 5

A tiny web app that takes any topic and returns an 
explanation suitable for a child. Built end-to-end on Cloudflare's developer
platformto get hands-on with Workers AI.

**Live demo:** https://my-ai-worker.misteragsharma.workers.dev/

## Stack

- **Cloudflare Workers (Python)** — serverless runtime, single-file deploy
- **Workers AI** — `@cf/meta/llama-3-8b-instruct` for inference, no external API keys
- **Wrangler** — local dev and deploy tooling

Cold start runs in under ~50ms on the edge; inference is billed per neuron via
Cloudflare's pay-as-you-go model, so idle cost is zero.

## Run it locally

```bash
npm install
npx wrangler dev
```

Then open http://localhost:8787.

## Deploy

```bash
npx wrangler deploy
```

## Possible next steps

- Stream the model response word-by-word via SSE
- Cache popular topics in Workers KV to cut inference cost
- Put AI Gateway in front of the inference call for observability and rate limits
