Use case
========

Specifics for the use case:

  * Code flow
  * Asymmetric key transport per https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5
  * Confirmation claim (``cnf``) of access token: 'jwk' element contains full JWK per https://tools.ietf.org/html/draft-ietf-oauth-proof-of-possession-02#section-3.1

Sequence diagram
----------------

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