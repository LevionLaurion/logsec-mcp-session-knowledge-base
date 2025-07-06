# Security Policy

## Supported Versions

LogSec follows semantic versioning. Security updates are provided for:

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | Yes                |
| < 3.0   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

### Private Disclosure

DO NOT create a public GitHub issue for security vulnerabilities.

Report security issues privately:
- Email: mail@laurion.de
- Subject: [SECURITY] LogSec Vulnerability Report

### Information to Include

When reporting a vulnerability, please provide:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

### Response Timeline

- Initial response: Within 48 hours
- Status update: Within 5 business days
- Resolution target: Within 30 days for critical issues

## Security Considerations

### Data Storage
- All data stored locally
- No network transmission
- Database files should be protected by OS permissions

### Best Practices
- Keep LogSec updated
- Restrict file system access
- Use generic project names for sensitive work
- Regular backups recommended

### Desktop Commander Integration
- Be aware that Desktop Commander logs file operations
- Logs stored in user directory
- Consider privacy implications for sensitive projects
