# Payments service runbook

## 1. Purpose

This runbook covers on-call actions for the payments service. It is a sample document set for the Module 10 lab; the values are invented.

## 2. Health checks

The service exposes `/healthz` and `/readyz`. A failing `/readyz` for more than two minutes means the instance is removed from the load balancer automatically.

## 3. Deploys

Deploys run from the `main` pipeline and go out to one region at a time. A deploy is paused automatically if the error rate rises above 2 percent.

## 4. Rollback

The rollback window for the payments service is 45 minutes after a deploy completes. Inside the window, run the `rollback-payments` pipeline with the previous release tag. After 45 minutes, do not roll back: ship a hotfix and roll forward, because database migrations may no longer be reversible.

## 5. Escalation

Page the payments on-call engineer first. If there is no acknowledgement within 10 minutes, page the engineering manager on call.
