# Collaboration Guide

## Getting Started

### For New Collaborators

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd doordash-omi
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your development environment:**
   ```bash
   git checkout development
   ```

## Development Workflow

### Branch Strategy
- `main` - Production-ready code
- `development` - Integration branch for features
- `feature/feature-name` - Individual feature branches

### Daily Workflow

1. **Start your day:**
   ```bash
   git checkout development
   git pull origin development
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "Add: Brief description of changes"
   ```

4. **Push your feature branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request on GitHub:**
   - Go to GitHub repository
   - Click "Compare & pull request"
   - Set base branch to `development`
   - Add description of changes
   - Request review from collaborators

### Real-time Collaboration Tips

1. **Frequent Pulls:**
   ```bash
   git pull origin development
   ```
   Do this before starting new work and when you see others have pushed changes.

2. **Communication:**
   - Use GitHub Issues for bug reports and feature requests
   - Use Pull Request comments for code discussions
   - Consider using Discord/Slack for real-time chat

3. **Avoid Conflicts:**
   - Work on different files when possible
   - If working on same file, coordinate with team
   - Use `git status` to check for conflicts

4. **Testing Before Push:**
   ```bash
   python main.py
   ```
   Always test your changes before pushing.

## File Organization

- `main.py` - Main FastAPI application
- `doordash_client.py` - DoorDash API integration
- `voice_processor.py` - Voice command processing
- `order_manager.py` - Order management logic
- `user_preferences.py` - User preference handling
- `static/` - Frontend assets
- `templates/` - HTML templates

## Best Practices

1. **Commit Messages:**
   - Use clear, descriptive messages
   - Format: "Type: Description"
   - Types: Add, Fix, Update, Remove, Refactor

2. **Code Style:**
   - Follow PEP 8 for Python
   - Add comments for complex logic
   - Keep functions small and focused

3. **Testing:**
   - Test your changes locally
   - Check that the app starts without errors
   - Verify API endpoints work

## Troubleshooting

### Merge Conflicts
```bash
git status  # See conflicted files
# Edit files to resolve conflicts
git add .
git commit -m "Resolve merge conflicts"
```

### Undo Changes
```bash
git checkout -- filename  # Undo changes to specific file
git reset --hard HEAD     # Undo all uncommitted changes
```

### Get Latest Changes
```bash
git fetch origin
git pull origin development
```

## Quick Commands Reference

```bash
# Check status
git status

# See recent commits
git log --oneline

# Switch branches
git checkout branch-name

# Create new branch
git checkout -b new-branch-name

# See all branches
git branch -a

# Delete local branch
git branch -d branch-name
```
