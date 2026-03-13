from tasks import demo_task

tasks = [
    ("low-1", 1),
    ("low-2", 1),
    ("high-1", 9),
    ("medium-1", 5),
    ("high-2", 9),
]

for name, priority in tasks:
    demo_task.apply_async(
        args=(name, 5),
        queue="priority",
        priority=priority,
    )
    print(f"Sent {name} priority={priority}")