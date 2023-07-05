# Summary

A new (largely rewritten) version of the Python autograder addressing security and usability issues. This document will
serve as a hybrid of RFC and initial design discussion.

# Motivation

The initial motivation behind this discussion was to improve the existing autograder. Rewriting the autograder
represents a significant scope expansion, which is motivated by the following:

1. The security vulnerabilities in the existing autograder are architectural. In particular, the scoring mechanism
used by the existing autograder is both easy to exploit and uses unnatural control flow that makes it difficult to
maintain. Implementing fixes for this requires changes to the way client grader code is written.

2. Outside of security, there is significant demand for changes to the architecture, features, and tooling (including
the addition of an independent test suite) of the autograder.

3. At a broader level, there is demand for a standalone Python package that autogrades student code (for example,
see https://pypi.org/project/autograder/). Serving this more general use case allows development of more robust
features and wider adoption.

# Basic Usage

The new autograder will be __backwards incompatible__ with previously written questions, but changes to the interface
will be kept at a minimum to facilitate easy migration. There will also be additional functionality implemented to
streamline certain operations (such as retrieving and checking equality for a symbol with a given name).

In addition, changes to the architecture will allow for uses outside of just the PL ecosystem with the addition of a
more general CLI.
## IO Based Graders

In particular, the new autograder will __not__ be "IO based", since this would introduce a major incompatibility
with the old autograder. Although this change could facilitate greater security, it would represent a
serious roadblock to widespread adoption by existing parts of the PL ecosystem, and thus wouldn't do anything
to patch the security problems for these courses.

Even this change would not be bulletproof and guarding against every possible exploit by arbitrary code is
nearly impossible. It's better to prioritize designing an autograder that can be easily migrated to and is more
secure than something that won't be used (but still has vulnerabilities anyway).

# Security

The following will facilitate greater security in the new autograder:

1. Introduction of code sandboxing features that provide (at least basic) safeguards against malicious code.
This would include safeguards against the use of certain builtin modules (via the [Restricted Python package](https://github.com/zopefoundation/RestrictedPython)), IO rate limiting, and timeouts for individual tests.

2. The addition of security-focused features in CI jobs. These would include use of the [Bandit package](https://bandit.readthedocs.io/en/latest/)
and a test suite that asserting common exploits fail.

3. Allowing fine-grained instructor control over operations allowed in test code, along with being very restrictive in
default settings. This would include things like limiting imports and printing to the console unless manually enabled
by instructors.

4. Changes to the architecture that employ greater compartmentalization of code and information that generally make security exploits
harder to pull off.

5. Conducting security audits before an initial release.

# Other Additional Features

The additional features here are a combination of requested features and generally useful things that would be compatible with
existing architecture.

1. A general CLI (written with [typed argument parser](https://pypi.org/project/typed-argument-parser/)). This would enable packaging and
usage outside of the PL ecosystem, along with heavily simplifying the code needed to run the autograder within PL. Right now, the entrypoint
of the autograder is a bash script that sets up the directory structure and looks for certain hardcoded file names. This can all be done within
Python and installed as part of the Python environment (and not require any file copying).

2. More relaxed file assumptions. Along with the previous items, some files are required for the autograder to run. These assumptions can be
relaxed, and the names of the files can be specified with the CLI.

3. Better parametrization features. Either using external dependencies (see [this](https://github.com/wolever/parameterized) or
[this](https://stackoverflow.com/a/13606054/2923069)) or implementing as part of the package itself, we can make it easier for
instructors to write more test cases for student code.

4. Concurrent and parallel test execution. Goes hand in hand with parameterized test cases. Very easy to handle if architecture is changed
using builtin modules.

5. Add compatibility with other autograding frameworks, such as Canvas and Gradescope. This should be straightforward and only require
changes to the output.
