#!/bin/bash

sed -i 's/"login.gitlab":"GitLab"/"login.gitlab":"<your button text>"/' webapp/dist/main.*.js
