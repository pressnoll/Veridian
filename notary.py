# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class AINotary(gl.Contract):
    attestations: DynArray[str]

    def __init__(self):
        pass

    @gl.public.write
    def notarize(self, url: str, claim: str) -> None:
        # Capture method params into local variables for the non-det block
        # (non-det blocks cannot access contract storage via self)
        target_url = url
        target_claim = claim

        # Define the non-deterministic block: fetch page + LLM reasoning
        def _analyze():
            # Fetch the web page content
            page_content = gl.nondet.web.get_webpage(target_url, mode="text")

            # Truncate to 3000 chars to avoid prompt overflow
            if len(page_content) > 3000:
                page_content = page_content[:3000]

            # Build the fact-checking prompt
            prompt = (
                "You are a neutral, objective fact-checker. "
                "You will be given a CLAIM and the TEXT CONTENT of a web page. "
                "Your task is to determine whether the page content supports, refutes, "
                "or is inconclusive about the claim.\n\n"
                f"CLAIM: {target_claim}\n\n"
                f"PAGE CONTENT:\n{page_content}\n\n"
                "Instructions:\n"
                "1. Determine the verdict: SUPPORTED (the page clearly supports the claim), "
                "NOT SUPPORTED (the page clearly contradicts or does not support the claim), "
                "or INCONCLUSIVE (the page does not contain enough information to confirm or deny).\n"
                "2. Assess your confidence: high (clear and direct evidence), "
                "medium (indirect or partial evidence), low (very little relevant information).\n"
                "3. Provide a one to two sentence evidence_summary that quotes or paraphrases "
                "the specific part of the page that supports or refutes the claim.\n\n"
                "Respond ONLY with a JSON object with exactly these keys: "
                "verdict, confidence, evidence_summary. "
                "No other text, no markdown, no preamble."
            )

            result = gl.nondet.exec_prompt(prompt, response_format="json")
            return result

        # Run through equivalence principle for validator consensus
        raw_result = gl.eq_principle.strict_eq(_analyze)

        # Parse the LLM response safely
        try:
            parsed = json.loads(raw_result)
            verdict = parsed.get("verdict", "INCONCLUSIVE")
            confidence = parsed.get("confidence", "low")
            evidence_summary = parsed.get("evidence_summary", "No evidence summary provided.")

            # Validate verdict value
            if verdict not in ("SUPPORTED", "NOT SUPPORTED", "INCONCLUSIVE"):
                verdict = "INCONCLUSIVE"

            # Validate confidence value
            if confidence not in ("high", "medium", "low"):
                confidence = "low"

        except (json.JSONDecodeError, TypeError, KeyError):
            verdict = "INCONCLUSIVE"
            confidence = "low"
            evidence_summary = "Contract could not parse the LLM response."

        # Build the full attestation record
        attestation = {
            "url": url,
            "claim": claim,
            "verdict": verdict,
            "confidence": confidence,
            "evidence_summary": evidence_summary,
            "timestamp": str(gl.message_raw.datetime),
            "submitter": str(gl.message.sender_address),
        }

        # Store as JSON string in the DynArray
        self.attestations.append(json.dumps(attestation))

    @gl.public.view
    def get_attestations(self) -> str:
        result = []
        for i in range(len(self.attestations)):
            try:
                result.append(json.loads(self.attestations[i]))
            except (json.JSONDecodeError, TypeError):
                result.append({"error": "Could not parse attestation record"})
        return json.dumps(result)

    @gl.public.view
    def get_attestation_count(self) -> int:
        return len(self.attestations)

    @gl.public.view
    def get_latest_attestation(self) -> str:
        if len(self.attestations) == 0:
            return json.dumps({})
        try:
            record = json.loads(self.attestations[len(self.attestations) - 1])
            return json.dumps(record)
        except (json.JSONDecodeError, TypeError):
            return json.dumps({"error": "Could not parse attestation record"})
