.PHONY: link unlink install package

link: ## Link workflow to Alfred for development
	@uv run bin/release.py link

unlink: ## Unlink workflow from Alfred
	@uv run bin/release.py unlink

install: ## Package and open workflow for installation
	@uv run bin/release.py install

package: ## Create .alfredworkflow package
	@uv run bin/release.py package

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
