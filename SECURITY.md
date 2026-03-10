# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Security Measures

### Data Storage
- ✅ All session data is stored **locally** in `~/.crawl4ai-skill/`
- ✅ Session cookies are encrypted with **AES-128-CBC**
- ✅ Encryption key is derived from machine identifier (MAC address + hostname)
- ✅ File permissions are set to **600** (user read/write only)
- ✅ Cannot be decrypted on other machines

### No Data Transmission
- ✅ **Zero network transmission of credentials**
- ✅ All data processing happens locally
- ✅ No telemetry, no analytics, no tracking
- ✅ No external API calls except target websites

### Dependency Security

All dependencies are well-known, actively maintained open-source projects:

| Package | License | Maintainer | Description |
|---------|---------|------------|-------------|
| `playwright` | Apache 2.0 | Microsoft | Browser automation |
| `crawl4ai` | Apache 2.0 | @unclecode | Web scraping for LLMs |
| `duckduckgo-search` | MIT | @deedy5 | Search API |
| `playwright-stealth` | MIT | @AtuboDad | Anti-detection |
| `cryptography` | Apache 2.0/BSD | PyCA | AES encryption |

### Automated Security Scanning

- ✅ **Bandit** security scan on every commit
- ✅ **pip-audit** dependency vulnerability check
- ✅ GitHub Dependabot enabled
- ✅ PyPI package security scan

## Verification

### Check if encryption is working:

```bash
crawl4ai-skill session-status
# Expected output:
# Platform: twitter
# Status: Logged in
# Encrypted: ✅ (AES-128-CBC)
# Last used: 2026-03-10 12:34:56
```

### Audit the code yourself:

```bash
# Clone and audit
git clone https://github.com/lancelin111/crawl4ai-skill.git
cd crawl4ai-skill

# Install audit tools
pip install bandit pip-audit

# Run security scans
bandit -r src/
pip-audit -r requirements.txt

# Review encryption implementation
cat src/crawl4ai_skill/login/session_manager.py
```

### Verify no network transmission:

```bash
# Monitor network traffic while using the tool
# (example using tcpdump on macOS/Linux)
sudo tcpdump -i any -nn host pypi.org or host github.com

# Then run the tool
crawl4ai-skill login twitter --cookies "auth_token=test; ct0=test"

# You should see NO traffic to unknown servers
# Only requests to target websites (x.com, xiaohongshu.com)
```

## Credential Input Security

### Recommended Methods (Secure → Less Secure)

| Method | Security | Shell History | Visibility |
|--------|----------|---------------|------------|
| **Environment Variable** | ⭐⭐⭐ | ✅ Not recorded | ✅ Not visible |
| **Interactive Input** | ⭐⭐⭐ | ✅ Not recorded | ✅ Not visible |
| **File Read** | ⭐⭐ | ✅ Not recorded | ⚠️ File must be chmod 600 |
| **Command Line** | ⭐ | ❌ Recorded in history | ❌ Visible in ps |

### Best Practice:

```bash
# Use environment variable
export TWITTER_COOKIES="auth_token=xxx; ct0=yyy"
crawl4ai-skill login twitter

# Or interactive mode
crawl4ai-skill login twitter --interactive
# (will prompt for input without displaying it)
```

## What We Do NOT Collect

- ❌ No cookies or credentials transmitted to external servers
- ❌ No telemetry or usage analytics
- ❌ No user tracking or fingerprinting
- ❌ No crash reports sent to third parties
- ❌ No email or personal information stored

## Reporting a Vulnerability

**Please report security vulnerabilities via:**
- GitHub Issues: https://github.com/lancelin111/crawl4ai-skill/issues
- Email: (will be added if needed)

**Response Time:** 48 hours

**Disclosure Policy:**
1. Report received → Acknowledged within 48h
2. Fix developed → Released within 7 days (for critical issues)
3. Public disclosure → After fix is released

## Security Updates

We commit to:
- ✅ Promptly fix reported vulnerabilities
- ✅ Release security patches within 7 days for critical issues
- ✅ Publish security advisories on GitHub
- ✅ Maintain changelogs with security notes

## License

This security policy is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

**Last Updated:** 2026-03-11  
**Contact:** [@lancelin111](https://github.com/lancelin111)
