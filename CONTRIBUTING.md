# Contributing to Dentist Portfolio & Clinic Management System

Thank you for your interest in contributing! This document provides guidelines for contributors.

## 🤝 How to Contribute

We welcome contributions in many forms:
- 🐛 Report bugs and suggest improvements
- 💡 Request features and enhancements
- 📝 Improve documentation
- 🔧 Fix bugs and implement features
- 🧪 Write tests and improve test coverage

## 📜 Code of Conduct

This project is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Git

### Setup
1. **Fork and clone** the repository
2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Setup database**:
   ```bash
   createdb dentist_dev
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. **Create `.env` file**:
   ```env
   DEBUG=True
   SECRET_KEY=your-development-secret-key
   DATABASE_URL=postgresql://localhost:5432/dentist_dev
   REDIS_URL=redis://localhost:6379/0
   ```

## 🔄 Development Workflow

### 1. Create Feature Branch
```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write clear commit messages
- Follow coding standards
- Add tests for new functionality
- Update documentation

### 3. Commit and Push
```bash
git add .
git commit -m "feat: add new feature description"
git push origin feature/your-feature-name
```

### 4. Create Pull Request
- Use descriptive title and description
- Ensure all tests pass
- Include screenshots for UI changes

## 📝 Code Standards

### Python/Django
- Follow PEP 8 with Black formatter (88 chars line length)
- Use Google-style docstrings
- Add type hints for functions
- Follow Django best practices

### JavaScript/HTML/CSS
- Use ES6+ features
- Follow Airbnb JavaScript Style Guide
- Use semantic HTML
- Follow BEM methodology for CSS

### Code Formatting
```bash
# Format Python code
black .
isort .

# Check code quality
flake8 .
```

## 🧪 Testing

### Requirements
- Unit tests for all new functionality
- Integration tests for API endpoints
- Minimum 80% test coverage

### Running Tests
```bash
# Run all tests

```

## 🐛 Reporting Issues

### Bug Report Template
```markdown
## Bug Description
Brief description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected vs Actual Behavior
What you expected vs what happened.

## Environment
- OS: [e.g., Windows 10, macOS 12.0]
- Python: [e.g., 3.9.7]
- Django: [e.g., 4.2.0]
```

## 💡 Requesting Features

### Feature Request Template
```markdown
## Feature Description
Brief description of the feature.

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this feature work?
```

## 🔍 Code Review

### Before Submitting PR
- [ ] Code follows style guidelines
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered

### Review Process
1. Automated checks pass
2. Code review by maintainers
3. Address feedback
4. Final approval and merge

## 📞 Contact

### Maintainers
- **Lead Maintainer**: [Youssef Osama](osama74454@gmail.com)
- **Technical Lead**: [Youssef Osama](osama74454@gmail.com)

### Communication
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and discussions
- **Email**: [Youssef Osama](osama74454@gmail.com)

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)

---

Thank you for contributing! Your contributions help make dental care more accessible and efficient.
