# 🔒 Security Notice

## Git History Cleaned

This repository's Git history has been completely rewritten to remove all sensitive data including:
- ✅ API keys
- ✅ Email addresses
- ✅ Cognito credentials
- ✅ Any other sensitive information

## What This Means

All commits in this repository now contain only placeholder values:
- `your_api_key_here` instead of actual API keys
- `your_email@example.com` instead of actual email addresses
- `your_cognito_client_id` instead of actual Cognito client IDs
- `your_cognito_client_secret` instead of actual Cognito secrets

## Before Running

Users must replace these placeholders with their own values:

```bash
# Set your own credentials
export ALPHA_VANTAGE_API_KEY=your_actual_api_key
export NOTIFICATION_EMAIL=your_actual_email@example.com
```

## Security Best Practices

1. **Never commit secrets** - Use environment variables or AWS Parameter Store
2. **Use .gitignore** - All config files with secrets are gitignored
3. **Review before pushing** - Always check what you're committing
4. **Rotate exposed keys** - If you accidentally commit a secret, rotate it immediately

## Files Protected by .gitignore

The following files are automatically excluded from Git:
- `config.json` (contains API keys)
- `*_config.json` (contains AWS resource IDs and credentials)
- `.env` files
- `.bedrock_agentcore.yaml`
- `Dockerfile`

## Safe to Use

This repository is now completely safe to:
- ✅ Share publicly
- ✅ Fork
- ✅ Clone
- ✅ Contribute to

All sensitive data is stored securely in AWS Parameter Store, not in the code.

---

**Last Security Audit**: February 23, 2026
**Status**: ✅ Clean - No sensitive data in repository or history
