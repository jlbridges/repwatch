Branching strategy
	Primary branches
		Main -> stable/ready for demo/updated at the end of each sprint
			Dev -> primary team works on
				UI -> UI team pulls from this branch to develop features
				Backend -> Backend team pulls from this branch to develop features
				Database -> Database team pulls from this branch to develop features
					Feature -> team created branches for each task in the sprint
	Feature branch conventions
		Each backlog item should have its own feature branch
		Naming -> feature/sprint#-task
			ex: feature/S1-homepage
	Pull Request Policy
		All changes must be submitted through a pull request
		PM will review each change before merging into dev
		Each PR must have test steps to verify how the feature works 
	Definition of done
		Code must run without errors
		Must include test steps
		list migrations if task changed a model
	
	