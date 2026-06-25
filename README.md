# AI Notary — GenLayer dApp

**AI Notary** lets you submit any public URL and a plain-language claim about its content, then a GenLayer intelligent contract fetches the page, reasons over it using AI validators, and returns a verifiable on-chain attestation confirming whether the claim is supported, not supported, or inconclusive. No oracles — validators reach consensus natively.

---

## Quick Start

### 1. Deploy the Contract

1. Open [GenLayer Studio](https://studio.genlayer.com/)
2. Create a new contract and paste the entire contents of **`notary.py`**
3. Click **Deploy** — Studio will compile and deploy the contract to the testnet
4. Copy the **deployed contract address** from the Studio UI (it will look like `0xAbCdEf...1234`)

### 2. Configure the Frontend

1. Open **`index.html`** in a text editor
2. Find this line near the top of the `<script>` tag:
   ```js
   const CONTRACT_ADDRESS = "PASTE_YOUR_CONTRACT_ADDRESS_HERE";
   ```
3. Replace `PASTE_YOUR_CONTRACT_ADDRESS_HERE` with your deployed contract address
4. Save the file

### 3. Open the dApp

1. Open **`index.html`** in a browser with [MetaMask](https://metamask.io/) installed
2. Approve the wallet connection when prompted
3. You're ready to notarize!

---

## Test It

Use this example to verify the dApp works:

| Field | Value |
|-------|-------|
| **URL** | `https://en.wikipedia.org/wiki/Bitcoin` |
| **Claim** | `Bitcoin was invented by Satoshi Nakamoto` |

Expected result: **SUPPORTED** with high confidence — the Wikipedia article clearly states this.

Another good test:

| Field | Value |
|-------|-------|
| **URL** | `https://en.wikipedia.org/wiki/Bitcoin` |
| **Claim** | `Bitcoin was created by Elon Musk` |

Expected result: **NOT SUPPORTED** — the article attributes Bitcoin to Satoshi Nakamoto, not Elon Musk.

---

## Architecture

```
┌──────────────────────┐      JSON-RPC / SDK       ┌─────────────────────────┐
│   index.html         │  ◄──────────────────────►  │   GenLayer Testnet      │
│   (Browser dApp)     │                            │                         │
│   • MetaMask wallet  │                            │   notary.py             │
│   • GenLayer JS SDK  │                            │   • Fetches web pages   │
│                      │                            │   • LLM fact-checking   │
│                      │                            │   • Validator consensus │
│                      │                            │   • On-chain storage    │
└──────────────────────┘                            └─────────────────────────┘
```

## Files

| File | Description |
|------|-------------|
| `notary.py` | GenLayer intelligent contract — the on-chain AI fact-checker |
| `index.html` | Self-contained frontend dApp (HTML + CSS + JS, no build step) |
| `README.md` | This file |
