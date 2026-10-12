# Editorial review log (10 passes)

Severity: **S1** factually wrong or integrity risk, **S2** technically misleading or broken, **S3** craft.

## Pass 1: mechanical lint (tools/lint_articles.py)
- S2 review-ddia: flow node "Part I: ..." parsed as a row label, so the diagram renders wrong.
- S1 13 bar charts show invented percentages labelled "illustrative" / "my experience" (judge, routing, RAG, DDIA, DMLS, LLM-from-scratch, MLDP, Reliable ML, TFS, ship-safely, shrink, sys1/sys2, voice).
- S3 shrink-a-transformer: "100x" in title is an unsupported overclaim.

## Pass 2: facts and attribution
- S1 sys1/sys2: credits Kahneman with naming System 1/2. Stanovich and West (2000) coined the terms; Kahneman popularized them (and credits them).
- S2 sys1/sys2: "beat a model several times larger" is vague. Snell et al. report test-time compute outperforming a 14x larger model in a FLOPs-matched comparison, on prompts where the small model already has non-trivial success.
- S1 voice: "~200 ms gaps" is unsourced (Stivers et al., PNAS 2009). "About a second of silence" is unsourced, so remove it.
- S2 voice: latency budget bars sum to 830 ms while the caption promises "under ~800 ms".
- S2 voice: TRG layer list omits the conditional Multiparty axis and mislabels disclosures as an axis.
- S1 deep-learning review: "no attention" is wrong (covered briefly in ch. 12). "Residual connections are in the book" is overstated.
- S2 shrink: "naive int8 causes accuracy collapse" overgeneralizes. LLM.int8() shows outlier features emerging at around 6.7B parameters; small encoders often quantize fine.

## Pass 3: technical correctness
- S2 shrink: "classification cuts latency by the number of output tokens" is wrong. You remove the decode steps, not a factor of N (prefill remains).
- S2 shrink: compute profile was invented. Replace it with per-token multiply-accumulates derived from the BERT-base architecture.
- S2 sys1/sys2: "below the diagonal" refers to a line the figure never draws. The correct baseline is the straight line between never- and always-escalate, which is what random escalation achieves.
- S2 judge: "a judge cannot beat human-human agreement" is false (a judge can agree with the majority label more than individuals agree with each other). Reframe as a reference point.
- S2 ship-safely: "divides by a zero baseline and computes 0%" is wrong for Python (raises). The real hazard is NaN comparisons evaluating false in many languages.

## Pass 4: code correctness
- S2 rag: reciprocal rank fusion uses 0-based ranks. The RRF definition is 1/(k + rank) with rank starting at 1.
- S1 guardrails: the refund policy trusts `order_owner` from the agent's own arguments, which is attacker-controlled. Ownership must be looked up server-side.
- S2 semantic-caching: the "negations" set includes non-negations ("cancel", "stop"), and capitalized-word "entities" miss lowercase input. Rename it to polarity terms and state the limits.
- S3 ship-safely: zero-baseline guard is checked after it is needed. Reorder it and add the absolute latency ceiling the prose promises.
- S3 shrink: pseudo-API (`skip_layer`) is not labelled as a sketch.

## Pass 5: diagram fidelity
- S2 shrink: pruning "curve" is drawn as a quadrant scatter. It needs a real curve, so add a `curve` renderer.
- S2 every replaced bar chart: swap it for a structural diagram, a sourced scale (Landis and Koch kappa bands), or a derivation with stated assumptions.

## Pass 6: integrity of first-person claims
- S1 invented personal anecdotes written in the author's voice: "I reread it every couple of years", "bitten by every one of them", "I have built transformers before", "I recommend it to every mentee", "15-point improvement" story. Remove them, or keep only claims that are verifiable or clearly opinion.
- S1 backdated publication dates (Oct 1-11) for articles written on one day. Use the true date.

## Pass 7: book-review fidelity
- S3 add distinctive, checkable details that prove a real reading: Reliable ML's running example company (YarnIt), DDIA's chapter map, LLM-from-scratch loading GPT-2 weights, AI Agents in Action's behavior trees and Nexus platform, the BERTopic pipeline stages (UMAP, HDBSCAN, c-TF-IDF), and the 30-pattern count in ML Design Patterns.
- S2 replace opinion bar charts ("my assessment") with rubric tables, which are honest about being opinions.

## Pass 8: voice and craft
- S3 "Here is an uncomfortable truth" opens two articles. "The whole game" is a cliché.
- S3 "Why Your LLM Judge Is Lying to You" reads as clickbait. Make it precise: "...Is Biased".

## Pass 9: SEO and feed validity
- S2 RSS pubDate is ISO 8601, which is invalid. RSS 2.0 requires RFC 822.
- S3 article pages lack og:image (use the cover for reviews, the portrait for guides) and dateModified.

## 11. Length expansion (2026-10-12)

At the user's request, expanded all 20 guides and book reviews to **at least 2,000 substantive prose words**, with the gate explicitly excluding front matter, diagrams, and fenced code. Final range: **2,106–3,675 prose words**, 49,221 total. The linter now enforces the minimum. Reviews disclose that they assess public catalogs, samples, and official companion materials, not a claim to have personally read complete books. Ratings are labeled provisional/public-materials assessments.

- Added detailed implementation procedures, edge cases, risks, operational criteria, and exercises to all guides.
- Added book-specific study paths, chapter scope, limitations, technical interpretation, and transparent source boundaries to reviews.
- Corrected AI Engineering bibliographic details: publisher O'Reilly listing is 2025 / ISBN 9781098166304; author repo ISBN 9781801819312 is a conflicting citation that resolves to another book.
- AI Agents in Action page now identifies Manning's 2025 / ISBN 9781633436343 catalog metadata, and flags its current “new edition available” notice; later edition metadata not independently verified.
- DDIA review is explicitly about the 2017 first edition and makes no unverified claim about a second edition's publication status.
- Fixed sequence diagram source syntax; replaced a false generic `10x` compression premise; clarified illustrative router endpoints; labels illustrative latency/cost values as design examples.
- QA found and fixed a clipped router-chart legend (legend now wraps) and nested `<aside>` landmark warning (callouts are non-landmark `div`s).
- Final lint: 20/20 pass. Build: 21 pages, 20 RSS entries, 131 diagrams. No broken local assets/links. Browser QA: 42 viewport checks (21 pages x mobile/desktop) pass, no page-level overflow, 0 404 indicators, axe WCAG 2.2 AA zero violations on writing index, flagship article, and AI Agents review. Dark mode was not re-run during this final QA session.

Final state:
- Lint: 20/20 pass.
- 22 pages with no horizontal overflow at 390 or 1280 px, no 404s, no console errors, and 0 broken internal links.
- axe WCAG 2.2 AA: 0 violations in light and dark.
- RSS validates with RFC 822 dates.
