#!/usr/bin/env python3

import lxml.etree as etree

etree.parse("./GO_Diploma.xml").write("./GO_Diploma.svg", encoding="utf-8")
