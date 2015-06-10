Use case
========

The POC implementation will be focused on solvning one use-case. That is PoP with asymetric keys for the code flow.

Specifics for the use case:

  * OIDC code flow
  * Asymmetric key transport per https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5
  * Confirmation claim (``cnf``) of access token: 'jwk' element contains full JWK per https://tools.ietf.org/html/draft-ietf-oauth-proof-of-possession-02#section-3.1

In the sequence diagram you can see references to PoP specifications indicating where the functionality will be added in the OIDC flow.

Sequence diagram
----------------

.. seqdiag::
    :desctable:

    seqdiag {
      "pyoidc relying party"    ->      "pyoidc provider" [label = "Webfinger"];
      "pyoidc relying party"    <-      "pyoidc provider";
      "pyoidc relying party"    ->      "pyoidc provider" [label = "Discovery"];
      "pyoidc relying party"    <-      "pyoidc provider";
      "pyoidc relying party"    ->      "pyoidc provider" [label = "Fetch keys from jwks_uri"];
      "pyoidc relying party"    <-      "pyoidc provider";
      "pyoidc relying party"    ->      "pyoidc provider" [label = "Registration"];
      "pyoidc relying party"    <-      "pyoidc provider";
      "pyoidc relying party"    ->      "pyoidc provider" [label = "Authn. req."];
      "pyoidc relying party"    <-      "pyoidc provider";
      "pyoidc relying party"    ->      "pyoidc provider" [label = "Token req. Extend with [1]"];
      "pyoidc relying party"    <-      "pyoidc provider" [label = "Token resp. Extend with [2]"];
      "pyoidc relying party"    ->      "pyoidc provider" [label = "User info req. Extend with [3]"];
      "pyoidc relying party"    <-      "pyoidc provider";
    }

* [1] https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5.1
* [2] https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5.2
* [3] https://tools.ietf.org/html/draft-ietf-oauth-signed-http-request-01#section-3.1