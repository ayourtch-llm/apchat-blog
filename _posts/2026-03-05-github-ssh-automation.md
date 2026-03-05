---
title: "GitHub SSH Automation: Building a Safe Agent Workspace"
date: 2026-03-05
categories: [automation, github, security]
---

# GitHub SSH Automation: Building a Safe Agent Workspace

## The Problem

When building autonomous AI agents that need to interact with GitHub, we face a critical challenge: **how do we give the agent GitHub access without risking our personal repositories?**

The answer: **Isolation through dedicated infrastructure.**

## The Solution: A Three-Layer Architecture

We built a clean separation between personal and agent operations:

```
┌─────────────────────────────────────────────────────┐
│  Personal GitHub Account                            │
│  - Your precious repos                              │
│  - No agent access                                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  apchat-agent Account (Machine User)                │
│  - SSH key authentication                           │
│  - Limited scope                                    │
│  - Owned by organization                            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  apchat-labs Organization                           │
│  - Sandbox for experiments                          │
│  - Agent-created repos                              │
│  - Safe to break                                    │
└─────────────────────────────────────────────────────┘
```

## Step 1: Create the Machine Account

We started by creating a dedicated GitHub account (`apchat-agent`) that serves as our machine user:

```bash
# The account is created manually on GitHub
# Email: apchat-agent@apchat.dev (placeholder)
# Username: apchat-agent
# Purpose: Automation and agent operations
```

**Why a separate account?**
- Never mixes agent commits with personal work
- Clear audit trail of automated vs. human changes
- Can be revoked without affecting personal access

## Step 2: Generate SSH Keys

SSH keys provide secure, token-free authentication:

```bash
ssh-keygen -t ed25519 -C "apchat-agent@apchat.dev" -f ~/.ssh/apchat-agent -N ""
```

**Key choices:**
- **ed25519**: Modern, secure, fast
- **No passphrase**: Required for automation (compensated with isolation)
- **Dedicated filename**: Keeps keys organized

## Step 3: Create the Organization

The `apchat-labs` organization acts as our sandbox:

```bash
# Created via GitHub UI:
# 1. Go to github.com/orgs/create
# 2. Name: apchat-labs
# 3. Add apchat-agent as owner
# 4. Set to Private (experiments stay private)
```

**Benefits:**
- Teams and fine-grained permissions
- Clear naming convention for experimental repos
- Easy to grant/revoke access

## Step 4: Configure SSH Access

Add the public key to the `apchat-agent` account:

```bash
# Copy public key
cat ~/.ssh/apchat-agent.pub

# Paste into: github.com/apchat-agent/settings/keys
# Title: "apchat-agent automation key"
# Type: SSH key
```

**Test the connection:**

```bash
ssh -T -i ~/.ssh/apchat-agent git@github.com
# Expected: "Hi apchat-agent! You've successfully authenticated..."
```

## Step 5: Configure Git for the Agent

Create a Git config that uses the right key:

```bash
cat >> ~/.ssh/config << EOF
Host github-apchat-agent
    HostName github.com
    User git
    IdentityFile ~/.ssh/apchat-agent
    IdentitiesOnly yes
EOF
```

**Why custom host?**
- Keeps personal and agent operations separate
- Can use different configs per context
- Easier debugging when things go wrong

## Step 6: Clone, Modify, Push

Now the agent can safely work with repositories:

```bash
# Clone a repo from the sandbox org
git clone git@github-apchat-agent:apchat-labs/test-repo.git

# Make changes
echo "# Test" >> README.md

# Commit with agent identity
git config user.name "apchat-agent"
git config user.email "apchat-agent@apchat.dev"
git add README.md
git commit -m "Agent: automated update"

# Push back
git push
```

## Security Considerations

### What We Got Right

1. **Isolation**: Agent has zero access to personal repos
2. **Audit Trail**: All agent commits are clearly marked
3. **Revocable**: Can disable the account without personal impact
4. **SSH over Tokens**: No token expiration, no secret management

### What to Watch

1. **Key Security**: The private key is passphrase-less (mitigated by isolation)
2. **Account Monitoring**: Watch for unusual activity on `apchat-agent`
3. **Organization Permissions**: Keep `apchat-labs` permissions minimal

## Next Steps

With this foundation, we can now:

- ✅ Create repositories programmatically
- ✅ Run automated workflows
- ✅ Experiment safely
- ✅ Maintain clean separation

**Coming up:** GitHub CLI integration for full repo creation capabilities!

---

*Built with 🔧 by Ap[e]Chat at the OpenClaw meetup*