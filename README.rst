Development setup
=================

Mount photos from production::

    $ sshfs -o ro akaihola@kasvit.ambitone.com:/www/ylaneenkasvit/media media


Deployment
==========

    export ANSIBLE_VAULT_PASS=***********
    ansible-playbook ansible/bootstrap.yml
    ansible-playbook ansible/install.yml
