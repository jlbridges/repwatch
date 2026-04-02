import requests
import hashlib
import yaml
import logging

from core.models import Committee, CommitteeMembership, Representative, DataSourceState

logger = logging.getLogger(__name__)

"""
HOW THIS WORKS:

Data is pulled from a repository that is kept current.

Committees are repopulated only when:
- the Committee table is empty
- or the committee source checksum changes

Memberships are repopulated only when:
- the CommitteeMembership table is empty
- or the membership source checksum changes
- or committees were just rebuilt
"""

COMMITTEE_DATA_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/refs/heads/main/committees-current.yaml"
MEMBERSHIP_DATA_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/refs/heads/main/committee-membership-current.yaml"

COMMITTEE_DATA_SOURCE_NAME = "committees_yaml"
MEMBERSHIP_DATA_SOURCE_NAME = "membership_yaml"

membership_cache = None


def get_checksum(data_text):
    return hashlib.sha256(data_text.encode("utf-8")).hexdigest()


def get_data_source_state(key):
    state, _ = DataSourceState.objects.get_or_create(
        key=key,
        defaults={"checksum": ""}
    )
    return state


def create_committee(committee, parent=None, committee_type=None):
    name = committee.get("name", "").strip()
    url = committee.get("url")
    thomas_id = committee.get("thomas_id")

    if not thomas_id:
        return None

    if name.lower().startswith("house "):
        name = name.split(" ", 1)[1]
    elif name.lower().startswith("senate "):
        name = name.split(" ", 1)[1]

    if committee_type is None:
        committee_type = committee.get("type")

    if parent is None:
        committee_id = thomas_id
    else:
        committee_id = f"{parent.committee_id}{thomas_id}"

    committee_obj = Committee.objects.create(
        committee_id=committee_id,
        committee_name=name,
        committee_type=committee_type,
        url=url,
        parent_committee=parent,
        is_subcommittee=parent is not None
    )

    return committee_obj


def populate_committees_from_text(text):
    data = yaml.safe_load(text)

    Committee.objects.all().delete()

    for committee in data:
        parent_committee = create_committee(committee)
        committee_type = committee.get("type")

        subcommittees = committee.get("subcommittees", [])
        for subcommittee in subcommittees:
            create_committee(subcommittee, parent=parent_committee, committee_type=committee_type)


def create_membership(committee_id, member):
    bioguide_id = member.get("bioguide")
    role = member.get("title")
    rank = member.get("rank")

    if not bioguide_id:
        return None

    try:
        representative = Representative.objects.get(Bioguide_id=bioguide_id)
    except Representative.DoesNotExist:
        return None

    try:
        committee = Committee.objects.get(committee_id=committee_id)
    except Committee.DoesNotExist:
        return None

    membership, _ = CommitteeMembership.objects.update_or_create(
        representative=representative,
        committee=committee,
        defaults={
            "role": role,
            "rank": rank,
        }
    )

    return membership


def populate_memberships_from_text(text):
    global membership_cache

    membership_cache = yaml.safe_load(text)

    CommitteeMembership.objects.all().delete()

    bioguide_ids = set(
        Representative.objects.exclude(Bioguide_id__isnull=True)
        .exclude(Bioguide_id="")
        .values_list("Bioguide_id", flat=True)
    )

    for committee_id, members in membership_cache.items():
        for member in members:
            bioguide_id = member.get("bioguide")
            if bioguide_id in bioguide_ids:
                create_membership(committee_id, member)


def sync_committees():
    response = requests.get(COMMITTEE_DATA_URL, timeout=30)
    response.raise_for_status()
    text = response.text

    checksum = get_checksum(text)
    state = get_data_source_state(COMMITTEE_DATA_SOURCE_NAME)

    table_empty = not Committee.objects.exists()
    changed = state.checksum != checksum

    if not table_empty and not changed:
        logger.info("Committee data unchanged, skipping committee sync.")
        return False

    populate_committees_from_text(text)

    state.checksum = checksum
    state.save(update_fields=["checksum", "updated_at"])

    logger.info("Committee data populated.")
    return True


def sync_memberships(committees_rebuilt=False):
    response = requests.get(MEMBERSHIP_DATA_URL, timeout=30)
    response.raise_for_status()
    text = response.text

    checksum = get_checksum(text)
    state = get_data_source_state(MEMBERSHIP_DATA_SOURCE_NAME)

    table_empty = not CommitteeMembership.objects.exists()
    changed = state.checksum != checksum

    if not table_empty and not changed and not committees_rebuilt:
        logger.info("Membership data unchanged. Skipping membership sync.")
        return False

    populate_memberships_from_text(text)

    state.checksum = checksum
    state.save(update_fields=["checksum", "updated_at"])

    logger.info("Committee membership data populated.")
    return True


def populate_committee_data():
    # bool where if committees is not changed (checksum), will not attempt to rebuild memberships
    sync_committees()
    sync_memberships()