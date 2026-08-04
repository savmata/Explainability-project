registry = MismatchRegistry()
explainer = ExplanationGenerator()
context = WorldContext()

# register expected load order from counter layout at episode start
registry.sequential.register_expected_order(
    [cfg["name"] for cfg in env.obj_cfgs]
)

for t, action in enumerate(actions):
    context.current_step = t
    beliefs = belief_mod.update(obs, env)
    current_b = beliefs[0]
    desire = desire_mod.active_goal(current_b)
    intention = intention_mod.decide(current_b, desire)

    events = registry.check_all(intention, context)
    for event in events:
        explainer.emit(event)

    if not intention.skip:
        context.load_history.append(current_b.name)
        context.last_action_step = t

    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break
