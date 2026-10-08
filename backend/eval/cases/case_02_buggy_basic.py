def get_average(scores):
    total = 0
    for s in scores:
        total += s
    return total / len(scores)


def find_user(users, user_id):
    for u in users:
        if u.id = user_id:
            return u