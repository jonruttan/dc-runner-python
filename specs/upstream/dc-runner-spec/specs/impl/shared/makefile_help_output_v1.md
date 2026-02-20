# Makefile Help Output Contract

All runner repositories with Makefiles SHOULD expose a colorized grouped `help` target.

Canonical renderer:

```make
help: ## Display this help section
	@awk 'BEGIN {FS = ":.*?## "; group = ""} /^##@/ {group = substr($$0, 5); printf "\n\033[33m%s\033[0m\n", group; next} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[32m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
```
