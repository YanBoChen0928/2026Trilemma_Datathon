# City View insights (precomputed, for team review)

Source: `data/tickets_block_agg.csv` — Downtown Vancouver, 2025-01-01 to 2026-06-30, 183,188 issued tickets across 383 100-blocks (water tickets removed; VPD-issued tickets not included). Ticket counts show where enforcement happened, not parking demand or the probability of a ticket.

Status: DRAFT — needs review by a second team member before the demo.

## Insight 1 — Rush-hour tickets cluster on a few streets

Rush-hour no-stopping tickets (bylaw 2849 s.17.2(K), priority congestion-management roadways) are 4.7% of Downtown tickets (8,672), but they are concentrated: ten blocks account for 44% of them, and Seymour, Howe and W Pender St together account for 56%. The 1000 block of W Pender St alone has 877 rush-hour tickets (68% of that block's tickets). These blocks may be candidates for operational review of signage and enforcement.

## Insight 2 — Some blocks are dominated by a single infraction type

Meter-expired tickets make up 59% of Downtown tickets, and on blocks such as 400 Helmcken St, 500 Nicola St and 1400 W Hastings St they are over 95% of the block's tickets. More unusual are non-meter blocks where one type dominates: 90% of tickets on the 100 block of Keefer Place and 52% on the 600 block of Abbott St (1,226 tickets) are posted-sign restrictions, and 84% of tickets on the 400 block of Beach Crescent are for overstaying a limit. Where one infraction type is this concentrated, the rule or its signage may be worth reviewing.

## Insight 3 — Enforcement is concentrated in a small share of blocks

The 50 highest-volume blocks (13% of the 383 mapped blocks) account for 53% of all Downtown tickets, and the top ten account for 19%. 900 Canada Place is the single largest block with 9,059 tickets. Enforcement attention is highly concentrated, which says where tickets were issued, not where parking demand is highest.

## Notes for reviewers

- The draft mockup's insight "Rush-hour violations cluster on Georgia St" is **not supported** by the data: Georgia St has 63 rush-hour tickets. Use the streets above instead.
- The mockup's "requests peak 5–7 pm" insight depends on the 311 stretch chart, which is not built yet. Do not show it until that chart exists.
- 8% of tickets sit on blocks whose coordinates are estimated (`coord_estimated`). None of the blocks named in the insights are estimated.
- Wording avoids causal claims ("may be", "candidate for review").
