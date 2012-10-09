txcloudfiles examples
=====================

These examples require valid Cloud Files account details to be stored in
environment variables to complete. For example under any decent *NIX shell:

```bash
$ export TXCFUSR="username"
$ export TXCFAPI="apikey"
```

The tests will interact with the live account specified in the environment
variables. It is not advised to play with these examples on a live account
unless you know what you're doing.

Once txcloudfiles is installed and the environment variables are set you can run
any of examples from the command line, for example:

```bash
$ python account_metadata.py
```
