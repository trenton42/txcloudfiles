txcloudfiles tests
==================

These tests require valid Cloud Files account details to be stored in
environment variables to complete. For example under any decent *NIX shell:

```bash
$ export TXCFUSR="username"
$ export TXCFAPI="apikey"
```

The tests will interact with the live, real account. It is highly advisable to
not run these tests if you have data in your account.

While this is not ideal and violates some principles of testing methodology none
of the examples provided nor mocking provide the required depth and detailed
response of the production Cloud Files platform (and I'm not bored enough to
build a feature-complete mock server myself).

The tests can be run with the wrapper in twisted trial via:

$ trial txcloudfiles_tests

You can also run each test suite individually in the same way.
