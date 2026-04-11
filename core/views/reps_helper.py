from core.models import Representative


def clear_user_reps(user):
    reps = Representative.objects.filter(constituents=user)

    for rep in reps:
        rep.constituents.remove(user)

        # delete rep if no users remain
        if rep.constituents.count() == 0:
            rep.delete()
