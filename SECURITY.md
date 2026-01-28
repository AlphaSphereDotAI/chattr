# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Chattr seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- **Do not** open a public GitHub issue for security vulnerabilities
- **Do not** disclose the vulnerability publicly until it has been addressed

### How to Report

**Email**: mohamed.hisham.abdelzaher@gmail.com

**Subject**: [SECURITY] Brief description of the issue

**Include**:
1. Type of vulnerability
2. Full paths of source file(s) related to the vulnerability
3. Location of the affected source code (tag/branch/commit or direct URL)
4. Step-by-step instructions to reproduce the issue
5. Proof-of-concept or exploit code (if possible)
6. Impact of the vulnerability
7. Your contact information

### What to Expect

- **Acknowledgment**: Within 48 hours of receiving your report
- **Initial Assessment**: Within 5 business days
- **Status Update**: Regular updates as we work on a fix
- **Resolution**: We aim to resolve critical issues within 30 days
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Measures

### Application Security

Chattr implements multiple security layers:

1. **Input Validation**
   - Pydantic schema validation
   - Type checking
   - Length limits

2. **Guardrails**
   - PII (Personally Identifiable Information) detection
   - Prompt injection prevention
   - Content filtering

3. **API Security**
   - Secure API key storage
   - Environment variable isolation
   - No hardcoded secrets

4. **Network Security**
   - HTTPS/TLS support
   - Rate limiting (when using reverse proxy)
   - CORS configuration

### Docker Security

- Uses minimal base images (Chainguard Wolfi)
- Non-root user execution
- Multi-stage builds
- Regular base image updates
- Vulnerability scanning

### Dependencies

- Regular dependency updates via Dependabot
- Security scanning with CodeQL
- Automated vulnerability alerts

## Best Practices for Users

### Configuration Security

1. **Never commit secrets** to version control:
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use strong API keys**:
   - Rotate keys regularly
   - Use environment-specific keys
   - Store securely (e.g., secrets manager)

3. **Limit access**:
   - Use firewall rules
   - Deploy in private networks
   - Use VPN for admin access

### Deployment Security

1. **Use HTTPS** in production:
   ```nginx
   ssl_certificate /path/to/cert.pem;
   ssl_certificate_key /path/to/key.pem;
   ```

2. **Keep software updated**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

3. **Monitor logs**:
   ```bash
   docker-compose logs -f | grep -i error
   ```

4. **Implement rate limiting**:
   ```nginx
   limit_req_zone $binary_remote_addr zone=chattr:10m rate=10r/s;
   ```

### Environment Variables

**Secure**:
```bash
export MODEL__API_KEY="$(cat /secure/path/api-key)"
```

**Not Secure**:
```bash
export MODEL__API_KEY="hardcoded-key"  # DON'T DO THIS
```

### Docker Secrets

For production, use Docker secrets:

```yaml
services:
  chattr:
    secrets:
      - model_api_key
    environment:
      MODEL__API_KEY_FILE: /run/secrets/model_api_key

secrets:
  model_api_key:
    external: true
```

## Known Security Considerations

### PII Detection

While Chattr includes PII detection guardrails, they are not 100% foolproof:

- Review logs regularly
- Implement additional filtering if handling sensitive data
- Consider data retention policies

### Prompt Injection

Prompt injection detection is active but evolving:

- Keep guardrails updated
- Monitor for suspicious patterns
- Implement input sanitization

### API Keys

API keys for model providers are sensitive:

- Use read-only keys when possible
- Set usage limits on provider side
- Rotate keys regularly
- Monitor usage for anomalies

### Vector Database

Qdrant stores conversation data:

- Implement backups
- Secure with authentication (production)
- Encrypt at rest if required
- Regular data cleanup

## Security Updates

Security updates are released as soon as possible:

1. Critical vulnerabilities: Immediate patch
2. High severity: Within 7 days
3. Medium severity: Next minor release
4. Low severity: Next major release

## Vulnerability Disclosure Policy

When a security vulnerability is confirmed:

1. **Private Fix**: We develop a fix privately
2. **Security Advisory**: Create GitHub Security Advisory
3. **Patch Release**: Release patched version
4. **Public Disclosure**: Publish advisory details
5. **CVE Assignment**: Request CVE if applicable

## Security Checklist for Deployments

- [ ] HTTPS/TLS enabled
- [ ] API keys stored securely
- [ ] Non-root user in containers
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] Regular backups configured
- [ ] Monitoring and alerting set up
- [ ] Logs reviewed regularly
- [ ] Dependencies up to date
- [ ] Security scanning enabled

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)

## Contact

For security concerns:
- Email: mohamed.hisham.abdelzaher@gmail.com
- GitHub Security Advisories: https://github.com/AlphaSphereDotAI/chattr/security/advisories

## Acknowledgments

We thank the following security researchers for responsibly disclosing vulnerabilities:

- (List will be updated as vulnerabilities are reported and fixed)

---

**Last Updated**: 2024-01-28

Thank you for helping keep Chattr and its users safe! 🔒
