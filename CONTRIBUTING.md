# Contributing Guide

This document outlines how the team works in this repository, including our branching strategy, pull request process, and definition of done.

---

## Branching Strategy

### Primary Branches

- **main**
  - Stable, production-ready code
  - Used for demos
  - Updated at the end of each sprint

- **dev**
  - Primary integration branch
  - All completed features are merged here

- **ui**
  - UI team pulls from this branch to develop UI-related features

- **backend**
  - Backend team pulls from this branch to develop backend features

- **database**
  - Database team pulls from this branch to develop database-related features

---

### Feature Branches

- Feature branches are created for each task in the sprint
- Each backlog item must have its own feature branch
- Feature branches should be short-lived and focused on a single task

#### Naming Convention

- feature/sprint#-task
	-ex: feature/S1-homepage

## Pull Request Policy

- All changes must be submitted through a pull request
- Pull requests must target the `dev` branch unless otherwise specified
- The Project Manager (PM) reviews each pull request before merging
- Each pull request must include:
  - A clear description of the change
  - Test steps explaining how to verify the feature

---

## Definition of Done

A task is considered complete when all of the following are true:

- Code runs without errors
- Required functionality is implemented
- Test steps are included in the pull request
- Database migrations are listed if a model was changed
- Code has been reviewed and approved

---

## Additional Notes

- Direct commits to `main` are not allowed
- Keep commits small and descriptive
- Communicate blockers early
	

	
