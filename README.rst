Development setup
=================

Mount photos from production::

    $ sshfs -o ro akaihola@kasvit.ambitone.com:/www/ylaneenkasvit/media media


Deployment
==========

In a checkout of the Ambitone deployment repository::

    $ ansible-playbook -v ylaneenkasvit.yml
