#Get the que and the length of the que
Class_WL = Waiting_List.objects.filter(class_name=classId)
Que_length = Class_WL.count()
que = 2
#Get and delete the WL slot for user
WL_slot = Waiting_List.objects.get(user=user, class_name=classId)
WL_slot.delete()
#Update the positions for the rest of the que
try:
    while que <= Que_length:
        print(que)
        WL_next = Waiting_List.objects.get(class_name=classId, que=que)
        WL_next.que -=1
        WL_next.save()
        que +=1
except Waiting_List.DoesNotExist:
    print("Nobody on the waitinglist")


Example: token1 user1=U1, user2=U2, user3=U3 // token 2 user1=U2, user2=U3, user3=U4 // token3 user1=U3, user2=U4, user3=U5. When U3(user number 3 in the waitinglist que) is removed then the order shifts as follow: token1 user1=U1, user2=U2, user3=U4 // token 2 user1=U2, user2=U4, user3=U5 // token3 user1=U4, user2=U5, user3=U6. (If there are only 5 U in the waitinglist, then intstead iof U6, user3 has a value of None)



#CHAT SUGGESTION:
#Update the PH_users (1,2,3) based on their position in the que
def PH_users_update(request, class_id, user_to_remove):
    # Fetch all placeholders for the class, ordered by token
    PH_list = Placeholder.objects.filter(tt_class=class_id).order_by('token')

    try:
        # Get the position of the user to be removed in the waiting list
        try:
            class_WL = Waiting_List.objects.get(class_name=class_id, user=user_to_remove)
        except Waiting_List.DoesNotExist:
            print(f"Error: User {user_to_remove} is not in the waiting list for class {class_id}")
            return  # Exit the function if the user is not found in the waiting list

        que = class_WL.que  # Start from the user's queue position

        # Get the waiting list for the class and order by queue position
        waiting_list = Waiting_List.objects.filter(class_name=class_id).order_by('que')

        # Iterate through placeholders
        for PH in PH_list:
            # For each placeholder, check the user positions (user1, user2, user3)
            for i in range(1, 4):
                user_attr = f'user{i}'
                current_user = getattr(PH, user_attr)

                if current_user == user_to_remove:
                    # If the user is found in this position, shift the subsequent users forward
                    # Shift users in positions after the removed user
                    for j in range(i, 3):  # Only shift user2 -> user3, user3 -> None
                        next_user_attr = f'user{j+1}'
                        next_user = waiting_list.filter(que=que + 1).first()

                        if next_user:
                            setattr(PH, next_user_attr, next_user.user)
                            que += 1
                        else:
                            setattr(PH, next_user_attr, None)  # No user to fill this spot

                    # After shifting, set the current position (user1, user2, or user3) to None
                    setattr(PH, user_attr, None)
                    break  # Exit the loop once we’ve removed the user from this placeholder

            PH.save()  # Save updates to the placeholder
            que += 1  # Move to the next placeholder's queue position

    except Exception as e:
        print(f"An error occurred: {e}")
