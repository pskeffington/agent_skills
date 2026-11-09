# Valuation Systema methods

## Quantitative scorecards

Score engineering maturity, evidence strength, commercial readiness and maintainability from 0 to 5, or null when unknown. Scores characterize evidence and readiness; **never convert aggregate scores directly to dollars**.

## Economic triangulation

- Replacement cost: reconstruction hours by skill/role multiplied by realistic loaded labor rates, plus testing and infrastructure, discounted for unowned, duplicated, obsolete or unusable code.
- Income approach: only supported net-cash-flow scenarios, with adoption, margins, lifecycle support, probability and discount-rate assumptions specified. No revenue evidence means scenario, not proven value.
- Market approach: verifiable transaction or license comparables, adjusted for buyer fit, ownership, restrictions, maturity and liquidity. If unavailable, mark unavailable.
- Always store USD low/base/high or null, as-of date, rationale, sensitivity and confidence.
- Distinguish enterprise value, IP value, replacement cost and realized revenue.

## Double-counting

Build family dependency graph and attribute each shared library, dataset, deployment and product once. Use explicit allocations and check allocation sums. Treat correlated revenue and common costs correctly when aggregating.

## Hard gates

Read source repositories without mutation. Store valuation estimates and financial scores only in the central private Portfolio workspace. Review material changes before publishing; never leak records into Portfolio public pages or assistants.
