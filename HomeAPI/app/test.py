def get_tasks_by_query(
        done: bool | None = None,
        title: str | None = None,
        subject: str | None = None
) :
    query_list = [value for value in (done, title, subject) if value is not None]
    return query_list

print(*get_tasks_by_query(done=False, title=None, subject='gjjf'))