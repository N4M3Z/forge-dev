# forge-dev

> Developer discipline skills and agents for the forge ecosystem — code quality, testing, defensive programming, debugging, git workflows, and code review.

I want you to install forge-dev for me. Execute all the steps below autonomously.

## OBJECTIVE

Deploy forge-dev skills and agents to all AI providers and activate the pre-commit validation hook.

## DONE WHEN

`make validate` exits 0 and `ls ~/.claude/skills/CodeCleanup/SKILL.md` prints the path.

## TODO

- [ ] Install prerequisites
- [ ] Build or install the tool
- [ ] Verify the installation

## Steps

### Prerequisites

You need the following installed before proceeding:

```sh
# check prerequisite
forge --version
```

### Install

```sh
git clone https://github.com/N4M3Z/forge-dev.git
cd forge-dev
make install
```

### Verify

You must confirm the installation succeeded:

```sh
# verification command that matches DONE WHEN
make validate
```

EXECUTE NOW: Complete the above TODO list to achieve: `make validate` exits 0 and `ls ~/.claude/skills/CodeCleanup/SKILL.md` prints the path.
