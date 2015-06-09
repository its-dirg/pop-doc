.. PoP doc documentation master file, created by
   sphinx-quickstart on Wed Jun  3 14:20:23 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

A pyoidc PoP POC
================

A Proof Of Concept(``POC``) implementation of Proof Of Possession(``PoP``) will be implemented for pyoidc.

Only some parts of the standard have been included in the POC and the focus is on the following specifications:

* https://tools.ietf.org/html/draft-ietf-oauth-pop-key-distribution-01#section-5
* https://tools.ietf.org/html/draft-ietf-oauth-proof-of-possession-02#section-3.1

The intention is to show one successful PoP for asymmetric keys for the code flow within OpenId Connect using pyoidc python framework.

Contents:

.. toctree::
   :maxdepth: 2

   pop
   usecase
