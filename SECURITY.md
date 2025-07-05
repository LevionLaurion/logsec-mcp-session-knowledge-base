# Security Policy

## Supported Versions

LogSec follows semantic versioning. Security updates are provided for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

We take the security of LogSec seriously. If you discover a security vulnerability, please follow these steps:

### 🔒 Private Disclosure

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security issues privately:

- **Email**: mail@felixlang.de
- **Subject**: [SECURITY] LogSec Vulnerability Report
- **Encryption**: PGP key available upon request

### 📋 Information to Include

When reporting a vulnerability, please provide:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** assessment
4. **Suggested fix** (if known)
5. **Your contact information** for follow-up

### ⏱️ Response Timeline

- **Initial response**: Within 48 hours
- **Investigation**: 7-14 days
- **Fix development**: 14-30 days (depending on complexity)
- **Public disclosure**: After fix is released

### 🛡️ Security Considerations

LogSec handles sensitive information including:

- **Session data and knowledge bases**
- **Project-specific information**
- **User content and metadata**
- **API keys and configuration**

### 🔐 Best Practices for Users

#### Secure Configuration
- Use environment variables for sensitive configuration
- Regularly rotate API keys and credentials
- Limit file system access permissions
- Enable logging for security monitoring

#### Data Protection
- Be mindful of sensitive data in session content
- Use project separation for confidential information
- Regularly backup and secure database files
- Monitor access logs for unusual activity

#### MCP Security
- Verify MCP server configurations
- Use secure communication channels
- Limit MCP server permissions
- Keep Claude Desktop and MCP servers updated

#### Desktop Commander Logging (CRITICAL)
⚠️ **IMPORTANT**: Desktop Commander logs operations to:
`C:\Users\[User]\.claude-server-commander-logs\`

**Privacy Implications:**
- File paths and search queries are logged
- Project names and sensitive file names may be exposed
- Log files persist across sessions
- No automatic log rotation or encryption

**Mitigation Strategies:**
- Regularly clean log directory: `C:\Users\[User]\.claude-server-commander-logs\`
- Avoid using sensitive project/file names
- Consider using generic directory names for confidential projects
- Monitor log files for sensitive information exposure
- Implement manual log rotation for long-running projects

### 🚨 Known Security Considerations

#### Desktop Commander Logging
- **Log Location**: `C:\Users\[User]\.claude-server-commander-logs\`
- **Logged Information**: File paths, search queries, operation details
- **Persistence**: Logs are not automatically cleaned
- **Encryption**: Log files are stored in plain text
- **Access Control**: Standard user file permissions apply

#### Database Security
- SQLite databases are stored locally
- No built-in encryption for database files
- Project separation provides logical isolation
- Consider file-level encryption for sensitive data

#### File System Access
- LogSec requires read/write access to project directories
- Temporary files may contain sensitive information
- Log files might include session metadata
- Archive folders contain historical data

#### Network Security
- MCP communication uses local protocols
- No network-based authentication required
- Consider firewall rules for enhanced security
- Monitor network traffic for anomalies

### 🔧 Security Updates

Security updates will be:
- Released as patch versions (e.g., 3.0.1)
- Documented in CHANGELOG.md
- Announced through GitHub releases
- Highlighted in README.md when critical

### 📞 Emergency Contact

For critical security issues requiring immediate attention:
- **Email**: mail@felixlang.de
- **Subject**: [URGENT SECURITY] LogSec Critical Vulnerability

### 🙏 Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who report vulnerabilities:
- Credit in release notes (with permission)
- Recognition in SECURITY.md
- Coordination on public disclosure timing

---

**Thank you for helping keep LogSec secure!**
