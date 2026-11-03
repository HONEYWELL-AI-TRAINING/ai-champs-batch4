# Checkout service runbook

## 1. Purpose

On-call actions for the checkout service. Sample content for the Module 10 lab; values are invented.

## 2. Severity levels

Sev1 means customers cannot complete a purchase. Sev2 means purchases are slow or degraded. Sev3 means a non-customer-facing problem.

## 3. Sev1 response

For a Sev1 on checkout, page the checkout on-call engineer and the incident commander at the same time. Open a channel named after the incident and post a status update every 15 minutes until the incident is resolved.

## 4. Feature flags

Checkout features are behind flags. To disable a feature during an incident, set its flag to off in the flag console. Record the change in the incident channel.
