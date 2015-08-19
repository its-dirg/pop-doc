.. PoP doc documentation master file, created by
    sphinx-quickstart on Wed Jun  3 14:20:23 2015.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

A pyoidc Proof-of-Possession POC
================================

A Proof of Concept (`POC`) implementation of Proof-of-Possession (`PoP`) for OAuth will be implemented with `pyoidc <https://github.com/rohe/pyoidc>`_.
The intention is to show one use case of PoP for OpenID Connect (OIDC).

Only some parts of the Internet-Drafts for PoP have been included in the POC and the focus is on the following specifications:

* |oauth_pop|
* |oauth_pop_key_dist|
* |oauth_sig_req|


Overview for PoP solution
=========================

The sequence diagram below gives a general overview of what the POC for PoP will cover.
The references in the sequence diagram indicates where the PoP functionality will be added to the OIDC authorization code flow.

Sequence diagram
----------------

.. seqdiag::

    seqdiag {
      Client    <-      Provider [label = "Provider keys"];
      Client    ->      Client [label = "Gen. key-pair"];
      Client    ->      Provider [label = "Authn. req."];
      Client    <-      Provider;
      Client    ->      Provider [label = "Token req. per [1]"];
      Provider  ->      Provider [label = "Make access token with 'cnf' per [2]"];
      Provider  ->      Provider [label = "Sign access token"];
      Client    <-      Provider [label = "Return token with token_type='pop' per [2]"];
      Client    ->      Provider [label = "Signed user info req. per [3]"];
      Provider  ->      Provider [label = "Verify sig. of access token"];
      Provider  ->      Provider [label = "Verify hash of signed request"];
      Provider  ->      Provider [label = "Verify sig. of user info req. against 'cnf' in access token"];
      Client    <-      Provider [label = "User info response if successful PoP"];
    }

* [1] https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5.1
* [2] https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5.2
* [3] https://tools.ietf.org/html/draft-ietf-oauth-signed-http-request-01


Use case
========

The POC implementation will be focused on solving one use case. That is PoP of asymmetric key when using the authorization code flow in OIDC.

Specifics for the use case:

  * `OIDC authorization code flow <http://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth>`_
  * Transport of the asymmetric key per https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5
  * Confirmation claim (``cnf``) in access token: 'jwk' element contains full JWK per https://tools.ietf.org/html/draft-ietf-oauth-proof-of-possession-02#section-3.1

In the sequence diagram below the references to PoP specifications indicates where the functionality will be added in the OIDC flow.

Sequence diagram
----------------

.. seqdiag::

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


Details of the implementation
=============================

* The signature of the HTTP request to the userinfo endpoint is placed in the
  request body as the parameter ``http_signature``.
* When creating/verifying the signature of the HTTP request, SHA{256, 384, 512}
  is used.
* The access token is signed by the provider using the 'RS256' algorithm.




.. |oauth_pop_key_dist| raw:: html

  <a href="https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5" target="_top">
  OAuth 2.0 Proof-of-Possession: Authorization Server to Client Key Distribution
  </a>

.. |oauth_pop| raw:: html

   <a href="https://tools.ietf.org/html/draft-ietf-oauth-proof-of-possession-02#section-3.1" target="_top">
   Proof-Of-Possession Semantics for JSON Web Tokens
   </a>

.. |oauth_sig_req| raw:: html

   <a href="https://tools.ietf.org/html/draft-ietf-oauth-signed-http-request-01" target="_top">
   A Method for Signing an HTTP Requests for OAuth
   </a>
