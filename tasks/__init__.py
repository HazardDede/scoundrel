from invoke import Collection

from tasks import (
    audit,
    config,
    game,
    linting,
    testing
)

ns = Collection()

audit = Collection.from_module(audit, name="audit")
lint = Collection.from_module(linting, name="lint")
test = Collection.from_module(testing, name="test")

# Subtasks
ns.add_collection(audit)
ns.add_collection(lint)
ns.add_collection(test)

# Tasks
ns.add_task(config.config)
ns.add_task(game.play)