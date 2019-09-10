# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/Dwolla/certificate-validator/issues>.

If you are reporting a bug, please include:

 * Your operating system name and version.
 * Any details about your local setup that might be helpful in troubleshooting.
 * Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with `bug` and `help wanted` is open to whomever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with `enhancement` and `help wanted` is open to whomever wants to implement it.

### Write Documentation

Certificate Validator could always use more documentation, whether as part of the official Certificate Validator docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at <https://github.com/Dwolla/certificate-validator/issues>.

If you are proposing a feature:

 * Explain in detail how it would work.
 * Keep the scope as narrow as possible, to make it easier to implement.
 * Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `certificate-validator` for local development.

1. Fork the [`certificate-validator`](https://github.com/Dwolla/certificate-validator) repository on GitHub.

2. Clone your fork locally:

```bash
git clone git@github.com:<username>/certificate-validator.git
```

3. Create a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your environment for local development:

```bash
mkvirtualenv certificate-validator
```

4. Install development requirements:

```bash
pip install -r requirements_dev.txt
`````

5. Create a branch for local development:

```bash
git checkout -b <branch>
```

Now you can make your changes locally.

6. When you're done making changes, check that your changes are formatted correctly and pass tests and checks:

```bash
make format && make test
```

7. Commit your changes and push your branch to GitHub:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin <branch>
```

8. Submit a [pull request](https://github.com/Dwolla/certificate-validator/pulls) through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the `README.md` or `docs/`.
3. The pull request should work for Python 3.7.
