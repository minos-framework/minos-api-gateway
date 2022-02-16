# History

## 0.0.1 (2021-06-14)

* First release on PyPI.

## 0.0.2 (2021-06-18)

* Bugfix.

## 0.0.3 (2021-08-19)

* Support auto discoverable endpoints.
* Handle requests to unavailable microservices.
* Improve request forwarding to microservices.
* Fix bug related with unnecessary `json` casting.

## 0.0.4 (2021-08-25)

* Add support to `CORS`.

## 0.1.0 (2021-11-03)

* Add support for external Authentication systems based on tokens.
* Remove `minos-apigateway-common` dependency.

## 0.1.1 (2021-11-03)

* Enforce Authentication Service validation if enabled.
* Improve error messages and use more appropriate status codes.

## 0.1.2 (2021-11-04)

* Fix bug related with byte-encoded requests forwarding.

## 0.2.0 (2022-02-03)

* Integration with `minos-auth`.
* Add PostgreSQL database with SQLAlchemy dependency.
* Auth Rules for authentication.
* Administration section for rules management.

## 0.3.0 (2022-02-04)

* Administration section BugFix getting index file.
* Adjust default auth routes

## 0.3.1 (2022-02-04)

* Administration section BugFix getting index file.

## 0.4.0 (2022-02-16)

* Add authorization rules to administration section.
* Authorization rules CRUD.
* Authorization checking on microservice call.
