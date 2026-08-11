// CHOROGRAPH-ANCHOR: shared/stub declarations only. Merged estate-wide by chorograph --anchors.
//
// This file lets `npx chorograph render .` pass inside this repo alone. When the whole
// Tatch-AI estate is rendered as one map, every repo's anchor.ts is deleted and replaced by a
// single master anchor, so nothing here may declare a node this repo actually owns — owned
// nodes live in chorograph/architecture.ts.

/**
 * Harper is an AI-forward commercial insurance brokerage. Revenue is commission on placed
 * premium; the platform runs the funnel from lead acquisition through intake, quoting and
 * placement, binding, payment, post-bind servicing, and renewal.
 * @system Harper
 */

/**
 * Developer experience tooling: config loaders (brek*), SDKs, agentic development, release
 * automation, and shared component libraries.
 * @domain DevEx
 */

/**
 * Infrastructure, Terraform, AWS, DevOps, and platform automation.
 * @domain Platform
 */

/**
 * AWS Secrets Manager — runtime secret fetch for database passwords, API keys, and other
 * credentials referenced in layered JSON config via the bundled awsSecret loader.
 * @external AWS-Secrets-Manager in:DevEx
 */
