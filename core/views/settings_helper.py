# Richard Functions for changing user settings
def updateProfileData(profile, request):
    print("function called")
    if request.POST.get("address_line1"):
        profile.address_line1 = request.POST.get('address_line1')

    if request.POST.get('address_line2'):
        profile.address_line2 = request.POST.get('address_line2')

    if request.POST.get('city'):
        profile.city = request.POST.get('city')

    if request.POST.get('state'):
       profile.state = 'NC'

    if request.POST.get('zipcode'):
        profile.zipcode = request.POST.get('zipcode')

    profile.save()

    print("Saved", profile.address_line1)

def updateUserData (postedUser, request):
    if request.POST.get('first_name'):
        postedUser.first_name = request.POST.get('first_name').strip()

    if request.POST.get('last_name'):
        postedUser.last_name =  request.POST.get('last_name').strip()

    if request.POST.get('email'):
        postedUser.email = request.POST.get('email').strip()

    postedUser.save()



# Richard functions for checking if user has made changes to profile or account settings.
# This is used to determine whether to update the database or not,
# and to prevent unnecessary database writes when no changes have been made.
def check_Profile_changed(request):
        hasValue = False
        if request.POST.get("address_line1"):
            hasValue = True 

        if request.POST.get('address_line2'):
            hasValue = True

        if request.POST.get('city'):
            hasValue = True

        if request.POST.get('state'):
            hasValue = True

        if request.POST.get('zipcode'):  
            hasValue = True

        return hasValue

def check_Account_changed(request):
        hasChanged = False
        if request.POST.get('first_name'):
            hasChanged = True

        if request.POST.get('last_name'):
            hasChanged = True

        if request.POST.get('email'):
            hasChanged =  True

        return hasChanged
