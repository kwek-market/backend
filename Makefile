start:
	@echo "start"

full_push:
	@echo "adding changes"
	@git add .
	@echo "commiting changes"
	@git commit -m "updates"
	@echo "setting to main branch"
	@git branch -M main
	@echo "pushing to upstream main"
	@git push upstream main
	@echo "pulling to local main"
	@git pull upstream main
	@echo "setting to prod branch"
	@git branch -M prod
	@echo "pushing to upstream prod"
	@git push upstream prod
	@echo "setting to main branch"
	@git branch -M main