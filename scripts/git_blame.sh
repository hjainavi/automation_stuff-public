#!/bin/bash

cd $1
git blame --porcelain $2 | grep '^author ' 