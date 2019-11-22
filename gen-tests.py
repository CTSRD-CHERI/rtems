#!/usr/bin/env python3

# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (C) 2019 embedded brains GmbH
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import re

def make_list(name, lst, extra):
    if not lst:
        return f"""{name}: []"""
    lines = f"""{name}:"""
    for l in lst:
            lines += f"""
- {l}{extra}"""
    return lines

def make_enabled_by(obj):
    if obj.enable:
        lines = f"""enabled-by:
- and:
  - not: TEST_EXCLUDE_{obj.short}"""
        for e in obj.enable:
                lines += f"""
  - {e}"""
        return lines
    else:
        return f"""enabled-by:
- not: TEST_EXCLUDE_{obj.short}"""

class TestSuite(object):
    def __init__(self, path, name, short, info, includes, special):
        self.path = "testsuites/" + path
        self.name = name
        self.short = short
        self.info = info
        self.includes = ["testsuites/support/include"] + includes
        self.objs_by_name = {}
        self.objs_by_uid = {}
        self.special = special

    def uid(self):
        return f"RTEMS-BUILD-TEST-{self.short}-GROUP"

    def write(self):
        if self.special:
            self.special(self)
        level = 1
        uids = [tc.uid() for tc in self.objs_by_name.values()]
        uids.sort()
        for uid in uids:
            level += 1
            obj = self.objs_by_uid[uid]
            obj.write(level)
        with open(f"spec/build/{self.path}/{self.uid()}.yml", "w") as f:
            f.write(f"""active: true
build-type: group
derived: false
enabled-by:
- BUILD_{self.name}
header: ''
{make_list("includes", self.includes, "")}
ldflags:
- -Wl,--wrap=printf
- -Wl,--wrap=puts
level: '1.{level}'
{make_list("links", uids, ": null")}
normative: true
order: 0
ref: ''
reviewed: null
text: ''
top-level: false
type: build
use:
- rtemstest
""")

class TestCase(object):
    def __init__(self, ts, name):
        self.test_suite = ts
        self.enable = []
        self.name = name
        self.short = self.name.replace("_", "").replace("-", "").upper()
        self.source = []
        self.c = False
        self.cxx = False
        self.norun = False
        self.cflags = []
        self.cppflags = ["${TEST_CPPFLAGS_" + self.short + "}"]
        self.cxxflags = []
        self.includes = []
        self.ldflags = []
        self.stlib = []
        self.use = []
        ts.objs_by_name[name] = self
        ts.objs_by_uid[self.uid()] = self

    def uid(self):
        return f"RTEMS-BUILD-TEST-{self.test_suite.short}-{self.short}"

    def write(self, level):
        features = "c cprogram"
        if self.c and self.cxx:
            features = "c cxx cxxprogram"
        elif self.cxx:
            features = "cxx cxxprogram"
        norun = ""
        if self.norun:
            norun = ".norun"
        with open(f"spec/build/{self.test_suite.path}/{self.uid()}.yml", "w") as f:
            f.write(f"""active: true
build-type: test-program
{make_list("cflags", self.cflags, "")}
{make_list("cppflags", self.cppflags, "")}
{make_list("cxxflags", self.cxxflags, "")}
derived: false
{make_enabled_by(self)}
features: {features}
header: ''
{make_list("includes", self.includes, "")}
{make_list("ldflags", self.ldflags, "")}
level: '1.{level}'
links: []
normative: true
order: 0
ref: ''
reviewed: null
{make_list("source", self.source, "")}
{make_list("stlib", self.stlib, "")}
target: {self.test_suite.path}/{self.name}{norun}.exe
text: ''
type: build
{make_list("use", self.use, "")}
""")

class Library(object):
    def __init__(self, ts, name):
        self.test_suite = ts
        self.enable = []
        self.name = name
        self.short = self.name.replace("_", "").replace("-", "").upper()
        self.source = []
        self.c = False
        self.cxx = False
        ts.objs_by_name[name] = self
        ts.objs_by_uid[self.uid()] = self

    def uid(self):
        return f"RTEMS-BUILD-TEST-{self.test_suite.short}-LIB{self.short}"

    def write(self, level):
        with open(f"spec/build/{self.test_suite.path}/{self.uid()}.yml", "w") as f:
            f.write(f"""active: true
active: true
build-type: library
cflags: []
cppflags: []
cxxflags: []
derived: false
{make_enabled_by(self)}
header: ''
includes: []
install: []
install-path: null
level: '1.{level}'
links: []
normative: true
order: 0
ref: ''
reviewed: null
{make_list("source", self.source, "")}
target: {self.name}
text: ''
type: build
""")

def special_sptests(ts):
    ts.objs_by_name["spcxx01"].cxxflags.append("-std=gnu++17")

def special_smptests(ts):
    ts.objs_by_name["smpopenmp01"].cflags.append("-fopenmp")
    ts.objs_by_name["smpopenmp01"].ldflags.append("-fopenmp")

test_suites = [
#TestSuite("ada/mptests", "ADA_MPTESTS", "ADAMP", "Ada MPCI test"),
#TestSuite("ada/samples", "ADA_SAMPLES", "ADASAMPLE", "Ada sample"),
#TestSuite("ada/sptests", "ADA_SPTESTS", "ADASP", "Ada single-processor test"),
#TestSuite("ada/tmtests", "ADA_TMTESTS", "ADATM", "Ada timing test"),
TestSuite("benchmarks", "BENCHMARKS", "BENCHMARK", "benchmark", [], None),
TestSuite("libtests", "LIBTESTS", "LIB", "library test", [], None),
TestSuite("mptests", "MPTESTS", "MP", "MPCI test", [], None),
TestSuite("psxtests", "PSXTESTS", "PSX", "POSIX test", ["testsuites/psxtests/include"], None),
TestSuite("psxtmtests", "PSXTMTESTS", "PSXTM", "POSIX timing test", ["testsuites/tmtests/include"], None),
TestSuite("rhealstone", "RHEALSTONE", "RHEALSTONE", "Rhealstone benchmark", ["testsuites/tmtests/include"], None),
TestSuite("samples", "SAMPLES", "SAMPLE", "sample", [], None),
TestSuite("smptests", "SMPTESTS", "SMP", "SMP test", [], special_smptests),
TestSuite("sptests", "SPTESTS", "SP", "single-processor test", [], special_sptests),
TestSuite("tmtests", "TMTESTS", "TM", "timing test", ["testsuites/tmtests/include"], None),
]

def process_test_suite_dir(ts, tc):
    return

def get_test_case(ts, name):
    if name in ts.objs_by_name:
        return ts.objs_by_name[name]
    return TestCase(ts, name)

def get_lib(ts, name):
    if name in ts.objs_by_name:
        return ts.objs_by_name[name]
    return Library(ts, name)

def check_norun(ts, name):
    if name.endswith("_norun"):
        name = name.replace("_norun", "")
        tc = get_test_case(ts, name)
        tc.norun = True
    return name

enable_map = {
"HAS_MP": "RTEMS_MULTIPROCESSING",
"HAS_POSIX": "RTEMS_POSIX_API",
"HAS_SMP": "RTEMS_SMP",
"NO_SMP": "not: RTEMS_SMP",
"NETTESTS": "RTEMS_NETWORKING",
}

def obj_set_enable(obj, enable):
    if not obj.enable:
        for e in enable:
            if e in enable_map:
                obj.enable.append(enable_map[e])

source_counts = {}

def obj_add_one_source(obj, source):
    m = re.match(r"\.\./([^.].*)", source)
    if m:
        source = "testsuites/" + m.group(1)
    else:
        source = obj.test_suite.path + "/" + source
    obj.source.append(source)
    count = source_counts.get(source, 0)
    source_counts[source] = count + 1

def obj_add_source(obj, source, enable):
    obj_set_enable(obj, enable)
    source = source.split()
    for s in source:
        m = re.match(r"(.+\.c)$", s)
        if m:
            obj_add_one_source(obj, m.group(1))
            obj.c = True
        m = re.match(r"(.+\.cc)$", s)
        if m:
            obj_add_one_source(obj, m.group(1))
            obj.cxx = True

def add_lib_source(ts, name, source, enable):
    m = re.match(r"lib(\w+)_a", name)
    if m:
        lib = get_lib(ts, m.group(1))
        obj_add_source(lib, source, enable)
        return True
    return False

def add_source(ts, name, source, enable):
    if not add_lib_source(ts, name, source, enable):
        name = check_norun(ts, name)
        tc = get_test_case(ts, name)
        obj_add_source(tc, source, enable)

def add_lib(ts, name, libs, enable):
    name = check_norun(ts, name)
    tc = get_test_case(ts, name)
    obj_set_enable(tc, enable)
    libs = libs.split()
    for l in libs:
        m = re.search(r"lib(\w+)\.a", l)
        if m:
            print(name, 'use', m.group(1))
            tc.use.append(m.group(1))
            continue
        m = re.match(r"-l(\w+)", l)
        if m:
            print(name, 'stlib', m.group(1))
            tc.stlib.append(m.group(1))
            continue

def add_cppflags(ts, name, cppflags, enable):
    name = check_norun(ts, name)
    tc = get_test_case(ts, name)
    obj_set_enable(tc, enable)
    cppflags = cppflags.split()
    for f in cppflags:
        m = re.search(r"-I(.+)", f)
        if m:
            h = m.group(1)
            if h.endswith("include"):
                continue
            h = h.replace("$(RTEMS_SOURCE_ROOT)/", "")
            h = h.replace("$(top_srcdir)/../../", "")
            h = h.replace("$(top_srcdir)/..", "testsuites")
            h = h.replace("$(top_srcdir)", ts.path)
            tc.includes.append(h)

def process_test_suite(ts):
    with open(ts.path + "/Makefile.am", "r") as f:
        lines = f.read().replace('\\\n', '').split('\n')
        enable = []
        for line in lines:
            line = line.strip()
            m = re.match(r"if\s+(\w+)", line)
            if m:
                enable.append(m.group(1))
                continue
            m = re.match(r"endif", line)
            if m:
                enable.pop()
                continue
            m = re.match(r"(\w+)_SOURCES\s*.=(.*)", line)
            if m:
                add_source(ts, m.group(1), m.group(2), enable)
                continue
            m = re.match(r"(\w+)_LDADD\s*.=(.*)", line)
            if m:
                add_lib(ts, m.group(1), m.group(2), enable)
                continue
            m = re.match(r"(\w+)_CPPFLAGS\s*.=(.*)", line)
            if m:
                add_cppflags(ts, m.group(1), m.group(2), enable)
                continue
    ts.write()

for ts in test_suites:
    process_test_suite(ts)
