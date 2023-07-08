FROM amazonlinux:2023

# plbase-install.sh: script to install all needed packages and dependencies
# python-requirements.txt: list of python packages to be installed by pip
COPY plbase-install.sh python-requirements.txt python-environment.yml /

RUN /bin/bash /plbase-install.sh

ENV PATH /opt/conda/envs/prairielearn/bin:$PATH

CMD /bin/bash
