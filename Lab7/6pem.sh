#!/bin/bash

openssl rsa \
  -pubin \
  -inform DER \
  -in public_key.der \
  -out public_key.pem