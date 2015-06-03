PoP doc
=======

Placeholder.

Proof-of-Possession sequence diagram
------------------------------------

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
* [3] https://tools.ietf.org/html/draft-ietf-oauth-signed-http-request-01#section-3.1

Use case sequence diagram
-------------------------

Specifics for the use case:

  * Code flow
  * Asymmetric key transport per https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5
  * Confirmation claim (``cnf``) of access token: 'jwk' element contains full JWK per https://tools.ietf.org/html/draft-ietf-oauth-proof-of-possession-02#section-3.1


.. seqdiag::
    :desctable:

    seqdiag {
      Client    ->      Provider [label = "Webfinger"];
      Client    <-      Provider;
      Client    ->      Provider [label = "Discovery"];
      Client    <-      Provider;
      Client    ->      Provider [label = "Fetch keys from jwks_uri"];
      Client    <-      Provider;
      Client    ->      Provider [label = "Registration"];
      Client    <-      Provider;
      Client    ->      Provider [label = "Authn. req."];
      Client    <-      Provider;
      Client    ->      Provider [label = "Token req."];
      Client    <-      Provider;
      Client    ->      Provider [label = "User info req."];
      Client    <-      Provider;

      Client [description = "pyoidc relying party"];
      Provider [description = "pyoidc provider"];
    }