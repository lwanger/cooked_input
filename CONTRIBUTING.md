# Contributing to this Project
**Here's how you can help.**

## Process
In the spirit of openness, this project follows [the Forking Flow](http://www.dalescott.net/wordpress/?p=1266), a derivative of [the Gitflow model](http://nvie.com/posts/a-successful-git-branching-model/).  We use Pull Requests to develop conversations around ideas, and turn ideas into actions.

**Some PR Basics**
- Anyone can submit a Pull Request with changes they'd like to see made.
- Pull Requests should attempt to solve a single [1], clearly defined problem [2].
- Everyone should submit Pull Requests early (within the first few commits), so everyone on the team is aware of the direction you're taking.
- Authors are responsible for explicitly tagging anyone who might be impacted by the pull request and get the recipient's sign-off [3].
- The Pull Request should serve as the authority on the status of a change, so everyone on the team is aware of the plan of action.
- Relevant domain authority _must_ sign-off on a pull request before it is merged [4].
- Anyone _except_ the author can merge a pull request once all sign-offs are complete.

[1]: if there are multiple problems you're solving, it is recommended that you create a branch for each.  For example, if you are implementing a small change and realize you want to refactor an entire function, you might want to implement the refactor as your first branch (and pull request), then create a new branch (and pull request) from the refactor to implement your new _feature_.  This helps resolve merge conflicts and separates out the logical components of the decision-making process.  
[2]: include a description of the problem that is being resolved in the description field, or a reference to the issue number where the problem is reported.  Examples include; "Follow Button doesn't Reflect State of Follow" or "Copy on Front-page is Converting Poorly".  
[3]: notably, document the outcome of any out-of-band conversations in the pull request.  
[4]: changes to marketing copy, for example, must be approved by the authority on marketing.

## Coding Conventions
Detail and examples below; here are the basic principles.

### tl;dr
- In general, Python [PEP 8](https://www.python.org/dev/peps/pep-0008/) should be followed.
- Beyond that the [Google Python style guide](https://google.github.io/styleguide/pyguide.html) should be followed when possible.
- All new functions and parameters (including cleaners, convertors, and validators) should be added to the documentation.
- Examples of all new functions and parameters (including cleaners, convertors, and validators) should be added to the examples.
