# Contributing to Samarth Coop

Thank you for contributing! To maintain a clean and reliable history, we use a strict Pull Request (PR) based workflow. 
**Never push directly to the `master` branch.**

## Branching & Merging Workflow

1. **Start from the latest master**:
   Ensure you have the latest changes before starting new work.
   ```bash
   git checkout master
   git pull origin master
   ```

2. **Create a Feature Branch**:
   Create a new branch for your issue or feature. Use descriptive names (e.g., `feature/issue-123-description`, `fix/login-bug`).
   ```bash
   git checkout -b feature/<issue-name>
   ```

3. **Develop and Test locally**:
   Write your code, and make sure to run the local QA checks before committing/pushing.
   ```powershell
   # Run local checks (Ruff, Pyright, Pytest, TSC)
   .\qa_check.ps1
   ```

4. **Push your branch**:
   ```bash
   git push -u origin feature/<issue-name>
   ```

5. **Open a Pull Request**:
   - Go to GitHub and open a PR from your feature branch against `master`.
   - CI (GitHub Actions) will automatically run tests, linting, and formatting checks.
   - Wait for all checks to pass and request reviews if necessary.

6. **Merge**:
   - Once approved and CI passes, use the "Merge pull request" or "Squash and merge" button on GitHub.
   - **Important**: GitHub will automatically delete your remote feature branch after merging.

7. **Sync your local repository**:
   After your PR is merged, update your local machine:
   ```bash
   git checkout master
   git pull origin master
   git branch -d feature/<issue-name>  # Delete local branch
   ```

## Keeping Feature Branches Updated

If `master` receives new commits while you are working on your feature branch, you should rebase your branch against the latest `master` instead of creating merge commits:

```bash
git fetch origin
git rebase origin/master
```
If you encounter conflicts, resolve them, `git add` the resolved files, and run `git rebase --continue`. Once rebased, you may need to force-push to your remote branch (`git push --force-with-lease`).

## Git Hooks and QA Checks

Our repository enforces a `pre-push` git hook to prevent failing CI builds. **You must configure this once on your local machine**:

```bash
git config core.hooksPath .githooks
```
This ensures the QA script runs automatically before any `git push` to save CI minutes.

### Running QA Checks Manually
You can run the QA checks manually to verify formatting and tests before pushing:
- **macOS / Linux**:
  ```bash
  ./qa_check.sh
  ```
  *(To auto-fix formatting, run `./qa_check.sh --fix`)*

- **Windows**:
  ```powershell
  .\qa_check.ps1
  ```
  *(To auto-fix formatting, run `.\qa_check.ps1 -Fix`)*

## Vitest Snapshots

If you intentionally modify a UI component, tests might fail with a snapshot mismatch. You must update the snapshots locally and commit them.

To update snapshots, run:
```bash
cd frontend
npm run test -- -u
```
