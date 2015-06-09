Overview for PoP solution
=========================



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
* [3] https://tools.ietf.org/html/draft-ietf-oauth-signed-http-request-01#section-3.1