Privacy Oriented CV Publishing
##############################

:date: 2019-03-09
:tags: devops
:summary: Publish your full CV and a privacy
	redacted version to put online with a bit
	of devops magic
:category: howto

.. contents::


Since the day I wrote a curriculum I've maintained two copies of 
it: they are identical, but the version I put online doesn't have
my home address/phone numbers, I give them to recuiters/HR only.

Problem was, the approach I used to wasn't very DRY, a couple of
identical tex document with and without my data:

.. code-block:: latex

	\name{Alessandro}{Ogier}
	\title{System and network administrator, developer}
	\email{alessandro.ogier@gmail.com}
	\social[linkedin]{alessandro-ogier}
	\social[github]{aogier}

and a oneliner for switching:

.. code-block:: bash

    sed s/%CONTACTS%/$contacts/ cv.tex > cvtemp.tex
    ./compile cvtemp.tex

time for I change!

New requisites
==============

What I want:

- keep my info away from internet weirdos
- edit cv code and trigger either doc builds on push
- having my public CV published on `github releases`_ so I
  can further automate stuff, maybe linkedin etc
- somehow, receiving back the private version so I can
  easily interact w/ headhunters

.. _github releases: https://github.com/aogier/aogier.github.io/releases

Private repositories
====================

Gitlab offers free private repos *and* CI bots that run on
them so I'll put there my data. Given the current `CI permission
model`_, I can add a private repo as a submodule in the main
project using a relative pointer that will work on gitlab and
on my machine:

.. code-block:: sh

	➜  oggei@cane ~/dev/cv git:(master)  cat .gitmodules 
	[submodule "private"]
        path = private
        url = ../private-curriculum.git

Private repo content will be protected by default wherever the
request come from. If a ``private`` subdirectory cannot be found,
relevant latex include will simply skip:

.. code-block:: latex

    \IfFileExists{private/contacts.tex}{\include{private/contacts}}

Neat!

.. _CI permission model: https://docs.gitlab.com/ee/user/project
	/new_ci_build_permissions_model.html

Building CV
===========

Build workflow
--------------

Build pipeline will have two stages:

- a *build* stage where the pdfs will be generated. Private or
  public version is just a matter of choosing an appropriate
  GIT_SUBMODULE_STRATEGY_ when cloning repo in CI
- a *deploy* stage where I'll put my artifact wherever I'll want

.. _GIT_SUBMODULE_STRATEGY: https://docs.gitlab.com/
    ee/ci/yaml/#git-submodule-strategy

Specialized build container
---------------------------

In order to keep build times low a `simple container`_
comes handy:

.. code-block:: dockerfile

    FROM debian
    
    RUN apt-get update \
        && apt-get install -y \
            texlive-latex-base \
            texlive-binaries \
            texlive-latex-extra \
            curl \
            jq

.. _simple container: https://hub.docker.com/r/aogier/latex

Build pipeline
--------------

Latest version `is here`_, I'll split and comment this one.

.. _is here: https://gitlab.com/aogier
    /public-curriculum/blob/master/.gitlab-ci.yml

First of all we define stages:

.. code-block:: yaml

    stages:                                                                                                                                                        
      - build                                                                                                           
      - deploy                                                                                                              

A build snippet common to either build jobs
we will parametrize via environment variables later:

.. code-block:: yaml

    .common_job: &common_job                                                                                                                                       
      stage: build                                                                                                                          
      image: aogier/latex                                                                                                                                          
      artifacts:                                                                                                                    
        paths:                                                                                                              
          - $OUTPUT_FILE.pdf                                                                                                                                       
      script:                                                                                                           
        - >                                                                                                     
          latex aogier-cv.tex;                                                                                                                                     
          latex aogier-cv.tex;                                                                                                                                     
          bibtex aogier-cv;                                                                                                                                        
          latex aogier-cv.tex;                                                                                                                                     
          pdflatex -jobname=$OUTPUT_FILE aogier-cv.tex                                                                                                             

Actual build jobs. They will run in parallel on Gitlab
infrastructure. Two variables drive the submodule strategy
and the final artifact filename:

.. code-block:: yaml
    
    build_private_cv:                                                                                                                                   
      variables:                                                                                                                    
        GIT_SUBMODULE_STRATEGY: normal                                                                                                                             
        OUTPUT_FILE: aogier-cv.private                                                                                                                             
      <<: *common_job
    
    build_public_cv:
      variables:
        GIT_SUBMODULE_STRATEGY: none
        OUTPUT_FILE: aogier-cv.public
      <<: *common_job

The deploy job, that only runs on tagged refs, interact via
github `releases v3 API`_ using a `personal access token`_ specified in
gitlab project's config as a `CI variable`_.

At first it POST a release and get his id, then use it for the
file upload:

.. _releases v3 API: https://developer.github.com/v3/repos/releases/
.. _personal access token: https://help.github.com/en/articles
    /creating-a-personal-access-token-for-the-command-line
.. _CI variable: https://docs.gitlab.com/ee/ci/variables/

.. code-block:: yaml
    
    deploy_public_cv:
      variables:
        REPO: https://api.github.com/repos/aogier/aogier.github.io
        AUTH_HEADER: "Authorization: token $GITHUB_TOKEN"
        UPLOAD_URL: https://uploads.github.com/repos/aogier/aogier.github.io
        FILENAME: aogier-curriculum.pdf
      stage: deploy
      image: alpine
      only:
        - tags
      before_script:
        - apk add --no-cache jq curl
      script:

        # preparing data and POSTing the new release
        #
        - >
          json_body="$(printf
          '{"tag_name":"%s","body":"# Alessandro Ogier CV\\nversion %s","name":"aogier CV"}'
          $CI_COMMIT_TAG $CI_COMMIT_TAG)"
        - >
          release_raw="$(curl
          $REPO/releases
          -X POST
          -H "$AUTH_HEADER"
          -d "$json_body")"
        - echo $release_raw | jq .
        - release_id=$(echo $release_raw | jq -r .id)
        - echo release id is $release_id
        
        # posting public file to release id
        #
        - >
          response=$(curl 
          $UPLOAD_URL/releases/$release_id/assets\?name\=$FILENAME
          -X POST
          -H "$AUTH_HEADER"
          -H 'Content-Type: application/pdf'
          -F 'data=@aogier-cv.public.pdf' | jq .url)

        # exit non-zero if anything goes wrong
        #
        - >
          if [[ $response == null ]]; then
          exit 1;
          fi

Further steps
=============

Now we have a `release list`_ whose latest item is programmatically
accessible via github either `via link`_ or `via API`_. I'll 
use this feature in order to include latest CV on this site
generation pipeline.

.. _release list: https://github.com/aogier/aogier.github.io/releases
.. _via link: https://help.github.com/en/articles/linking-to-releases
.. _via API: https://developer.github.com/v3/repos
    /releases/#get-the-latest-release




