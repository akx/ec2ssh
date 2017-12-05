ec2ssh
======

Simple utility to make it easier to connect to EC2 instances by automating
lookup of IP address by way of instance identifier and Name tag.

:battery: Python 3 standard library only, no additional batteries required!

Usage
-----

* `python3 -m ec2ssh --list` – list the identifiers recognized by ec2ssh.
* `python3 -m ec2ssh prod60` – connect to `prod6013591` if it's the only one with the prefix `prod60`.

You may want to alias or wrap the `python3 -m ec2ssh` incantation as you like.
You can also alias or symblink the included `run_ec2ssh.py` script.
