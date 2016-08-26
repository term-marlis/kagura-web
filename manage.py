#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from flask_script import Manager
from web.app import app

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
