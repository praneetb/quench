#!/usr/bin/env python

import os
import re
from subprocess import call

#import pdb; pdb.set_trace()

ifconfig = os.popen('vagrant ssh -c "ifconfig eth0"').read()
ipgroup = re.search(r'inet addr:(\S+)', ifconfig)
if not ipgroup:
    sys.exit(1)
ip = ipgroup.group(1)
print ip

